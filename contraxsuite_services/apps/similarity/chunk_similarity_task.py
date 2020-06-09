"""
    Copyright (C) 2017, ContraxSuite, LLC

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as
    published by the Free Software Foundation, either version 3 of the
    License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

    You can also be released from the requirements of the license by purchasing
    a commercial license from ContraxSuite, LLC. Buying such a license is
    mandatory as soon as you develop commercial activities involving ContraxSuite
    software without disclosing the source code of your own applications.  These
    activities include: offering paid services to customers as an ASP or "cloud"
    provider, processing documents on the fly in a web application,
    or shipping ContraxSuite within a closed source product.
"""
# -*- coding: utf-8 -*-

import datetime
import math
from typing import List, Set, Tuple, Optional, Dict, Generator, Iterable

import regex as re
from nltk import ngrams
from scipy import sparse
from scipy.sparse import csr_matrix
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from apps.analyze.models import DocumentSimilarity, TextUnitSimilarity
from apps.document.models import Document
from apps.task.tasks import BaseTask, ExtendedTask
from apps.similarity.similarity_metrics import make_text_units_query

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2020, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.6.0/LICENSE"
__version__ = "1.6.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class ChunkSimilarity(BaseTask):
    """
    Find Similar Documents, Text Units - almost the same as "Similarity"
    task, but processes documents / text units by chunks.
    Besides, ChunkSimilarity uses ngrams as terms in term frequency table.

    All class's logic is encapsulated in DocumentChunkSimilarityProcessor.
    """
    name = 'Chunk Similarity'

    def process(self, **kwargs):
        should_delete = kwargs['delete']
        project = kwargs['project']
        proj_id = project['pk'] if project else None
        search_target = kwargs['search_target']

        search_similar_documents = search_target == 'document'
        search_similar_text_units = not search_similar_documents

        similarity_threshold = kwargs['similarity_threshold']
        use_idf = kwargs['use_idf']
        term_type = kwargs['term_type']
        ngram_len = kwargs['ngram_len']
        ignore_case = kwargs['ignore_case']
        self.log_info('Min similarity: %d' % similarity_threshold)

        proc = DocumentChunkSimilarityProcessor(
            self, should_delete, proj_id,
            search_similar_documents, search_similar_text_units,
            similarity_threshold, use_idf, term_type, ngram_len, ignore_case)
        proc.process_pack()

    def estimate_time(self, **kwargs) -> float:
        project = kwargs.get('project')
        proj_id = project.id if project else None
        search_target = kwargs['search_target']

        if search_target == 'document':
            count = Document.objects.all().count() if not proj_id \
                else Document.objects.filter(project_id=proj_id).count()
            estimated_time = 0.0005 * count * count + 0.0527 * count + 0.0054
        else:
            # unit_text_regex = DocumentChunkSimilarityProcessor.unit_text_regex
            unit_query = make_text_units_query(proj_id)
            count = unit_query.count()
            estimated_time = 0.0006 * count**1.2446
        return estimated_time


class DocumentChunkSimilarityProcessor:
    """
    The class is used in ChunkSimilarity task for full text searching
    similar Document-s or TextUnit-s. As the class is used in task,
    it receives a task as an argument
    """
    TERM_TYPE_WORD_3GRAM = 'WORD_3GRAMS'
    TERM_TYPE_WORDS = 'WORDS'
    TERM_TYPE_CHAR_NGRAM = 'CHAR_NGRAMS'

    LOG_FLOOD_INTERVAL_SECONDS = 60 * 5

    n_features = 100
    doc_vocabulary_chunk_size = 100
    unit_vocabulary_chunk_size = 100 * 60
    step = 2000
    reg_wordsplit = re.compile(r'[\s\.,;:-\?)(\[\]''"]+')

    def __init__(self,
                 task: ExtendedTask,  # task object to log messages and report progress
                 should_delete: bool = True,  # delete existing DocumentSimilarity entries
                 project_id: Optional[int] = None,  # optional project filter
                 search_similar_documents: bool = True,  # we either search for similar documents...
                 search_similar_text_units: bool = False,  # ... or TextUnit-s
                 # min "correlation" to consider 2 documents (or TextUnit-s) similar
                 similarity_threshold: int = 75,
                 # should we use Inverse Document Frequency to obtain (sometimes) more precise results?
                 use_idf: bool = False,
                 # process text as character ngrams, just words or word ngrams
                 term_type: str = 'WORDS',
                 # character count in character ngrams (if term_type is 'CHAR_NGRAMS')
                 char_ngrams_length: int = 6,
                 ignore_case: bool = True):
        self.task = task
        self.project_id = project_id
        self.should_delete = should_delete
        self.similarity_threshold = similarity_threshold
        self.search_similar_documents = search_similar_documents
        self.search_similar_text_units = search_similar_text_units
        self.use_idf = use_idf
        self.term_type = term_type
        self.char_ngrams_length = char_ngrams_length
        self.ignore_case = ignore_case

        # min term frequency, integer value is for absolute occurrence count,
        # float value is for relative occurrence (per total entries count)
        # Used while building vocabulary
        self.min_df = 2
        # same as min_df, but for upper limit
        self.max_df = 0.5
        # documents count, used when search_similar_documents is True
        self.documents_count = 0
        # text units count, used when search_similar_text_units is True
        self.units_count = 0
        # buffer to accumulate storing DocumentSimilarity items for bulk insert operation
        self.docsim_store_buffer = []  # type:List[DocumentSimilarity]
        # buffer to accumulate storing TextUnitSimilarity items for bulk insert operation
        self.unsim_store_buffer = []  # type:List[TextUnitSimilarity]
        # flush buffer when it reaches the limit
        self.store_buf_flush_count = 1000
        # used for logging time spent for each stage of the task's calculations
        self.timings = []  # type:List[Tuple[str, datetime.datetime]]
        # used when search_similar_documents is True - all documents or
        # just the documents of the specified project
        self.doc_query = Document.objects.all().order_by('pk') if not self.project_id \
            else Document.objects.filter(project_id=self.project_id).order_by('pk')
        # used when search_similar_text_units is True - all text units or
        # just the text units of the specified project
        self.text_unit_query = None
        # time_logged prevents logging to frequent
        self.time_logged = {}  # type: Dict[str, time]
        if search_similar_text_units:
            self.text_unit_query = make_text_units_query(self.project_id)

    def process_pack(self) -> None:
        """
        A simple switch between search_similar_documents and search_similar_text_units
        """
        # similar Documents
        if self.search_similar_documents:
            self.do_search_similar_documents()

        # similar Text Units
        if self.search_similar_text_units:
            self.do_search_similar_textunits()

    def do_search_similar_documents(self) -> None:
        """
        Full text search for similar documents by comparing
        documents' feature matrices, built by TfidfVectorizer
        """
        self.push_time('', True)
        self.documents_count = self.doc_query.count()
        # x1 for building vocabulary, x2 for building matrices
        self.task.set_push_steps(math.ceil(
            self.documents_count / self.doc_vocabulary_chunk_size) * 2)

        if self.should_delete:
            DocumentSimilarity.objects.all().delete()
        self.push_time('deleting')

        vocabulary = self.build_doclevel_vocabulary()
        self.task.task.update_progress(33)
        self.push_time('build_vocabulary')
        if not vocabulary:
            return

        dtm_chunked = self.build_doclevel_matrices(vocabulary)
        self.push_time('build_matricies')
        self.task.task.update_progress(60)

        self.log_check_flood('vstack', 'matrices are being stacked')
        X = sparse.vstack(dtm_chunked)
        self.log_check_flood('vstack', 'matrices are stacked')
        self.push_time('sparse.vstack(matricies)')

        # step #4
        self.log_check_flood('cosine_similarity', 'cosine_similarity is being executed')
        similarity_matrix = cosine_similarity(X) * 100
        self.task.task.update_progress(66)
        self.log_check_flood('cosine_similarity', 'cosine_similarity is executed')
        pks = list(self.doc_query.values_list('pk', flat=True))
        self.push_time('post-process matrix')

        docs_sim_range = len(pks) - 1
        for x in range(docs_sim_range):
            document_a = pks[x]
            self.log_check_flood('similarity check', f'similarity({x} of {docs_sim_range})')
            # use it to search for unique a<>b relations
            # for y, document_b in enumerate(Document.objects.all()[x + 1:], start=x + 1):
            for y in range(x + 1, len(pks)):
                document_b = pks[y]
                similarity = similarity_matrix[x, y]
                if similarity < self.similarity_threshold:
                    continue
                ds = DocumentSimilarity(
                    document_a_id=document_a,
                    document_b_id=document_b,
                    similarity=similarity)
                self.store_doc_similarity_issues(ds)

        self.store_doc_similarity_issues(None, True)
        self.push_time('searching by matrix')
        self.log_timing('DocumentChunkSimilarityProcessor(doc level)')

    def do_search_similar_textunits(self) -> None:
        """
        Text search for text units (sentences or paragraph) by comparing
        text units' feature matrices, built by TfidfVectorizer
        """
        self.push_time('', True)
        pks = list(self.text_unit_query.values_list('pk', flat=True))
        self.units_count = len(pks)
        # x1 for building vocabulary, x2 for building matrices, x3 for storing similar entities
        self.task.set_push_steps(math.ceil(
            self.units_count / self.unit_vocabulary_chunk_size) * 2 + 1)

        if self.should_delete:
            TextUnitSimilarity.objects.all().delete()
        self.push_time('deleting')

        self.log_check_flood('vocabulary', 'building vocabulary')
        vocabulary = self.build_unitlevel_vocabulary()
        self.log_check_flood('vocabulary', 'completed building vocabulary')
        self.task.task.update_progress(33)

        self.push_time('build_vocabulary')
        if not vocabulary:
            return

        self.log_check_flood('matrices', 'building matrices')
        dtm_chunked = self.build_unitlevel_matrices(vocabulary)
        self.task.task.update_progress(60)
        self.log_check_flood('matrices', 'completed building matrices')
        self.push_time('build_matricies')

        self.log_check_flood('vstack', 'staking matrices')
        X = sparse.vstack(dtm_chunked)
        self.task.task.update_progress(66)
        self.log_check_flood('vstack', 'completed staking matrices')
        self.push_time('sparse.vstack(matricies)')

        for i in range(0, self.units_count, self.step):
            self.log_check_flood('sim_matrix',
                                 f'building similiarity matrix: ({i} of {self.units_count} are completed)')
            for j in range(i + 1, self.units_count, self.step):
                similarity_matrix = cosine_similarity(
                    X[i:min([i + self.step, self.units_count])],
                    X[j:min([j + self.step, self.units_count])]) * 100
                for g in range(similarity_matrix.shape[0]):
                    similarities = []
                    for h in range(g + 1, similarity_matrix.shape[1]):
                        if similarity_matrix[g, h] < self.similarity_threshold:
                            continue
                        similarities.append(TextUnitSimilarity(
                            text_unit_a_id=pks[i + g],
                            text_unit_b_id=pks[j + h],
                            similarity=similarity_matrix[g, h]))
                    if similarities:
                        self.store_unit_similarity_issues(similarities)

        self.store_unit_similarity_issues([], True)
        self.push_time('searching by matrix')
        self.log_timing('DocumentChunkSimilarityProcessor(text unit level)')

    def store_doc_similarity_issues(self,
                                    doc_sim: Optional[DocumentSimilarity],
                                    flush: bool = False) -> None:
        """
        Store DocumentSimilarity objects in buffer for future saving them
        in bulk update / insert operation
        :param doc_sim: item to store
        :param flush: flush buffer
        """
        if doc_sim:
            self.docsim_store_buffer.append(doc_sim)
        if len(self.docsim_store_buffer) < self.store_buf_flush_count and not flush:
            return
        if self.docsim_store_buffer:
            DocumentSimilarity.objects.bulk_create(self.docsim_store_buffer, ignore_conflicts=True)
            self.docsim_store_buffer = []

    def store_unit_similarity_issues(self,
                                     un_sims: List[TextUnitSimilarity],
                                     flush: bool = False) -> None:
        """
        Store TextUnitSimilarity objects in buffer for future saving them
        in bulk update / insert operation
        :param un_sims: items to store
        :param flush: flush buffer
        """
        if un_sims:
            self.unsim_store_buffer += un_sims
        if len(self.unsim_store_buffer) < self.store_buf_flush_count and not flush:
            return
        if self.unsim_store_buffer:
            TextUnitSimilarity.objects.bulk_create(self.unsim_store_buffer, ignore_conflicts=True)
        self.unsim_store_buffer = []

    def build_unitlevel_vocabulary(self) -> List[str]:
        return self.build_vocabulary(self.get_unit_vocabulary_textset,
                                     self.unit_vocabulary_chunk_size,
                                     self.units_count)

    def build_doclevel_vocabulary(self) -> List[str]:
        return self.build_vocabulary(self.get_doc_vocabulary_textset,
                                     self.doc_vocabulary_chunk_size,
                                     self.documents_count)

    def build_vocabulary(self,
                         get_textset,
                         chunk_size: int,
                         total: int) -> List[str]:
        """

        :param get_textset: query that return text data - strings, probably, multilines
        :param chunk_size: chunk size - count of string objects to read at once
        :param total: total records to read
        :return: sorted list of unique ngrams
        """
        term_by_doc = {}  # type:Dict[str, int]
        start = 0
        while start < total:
            end = start + chunk_size
            end = min(end, total)
            texts_set = get_textset(start, end)  # type: List[str]
            ngrams = self.get_ngrams(texts_set)
            for ngram in ngrams:
                if ngram in term_by_doc:
                    term_by_doc[ngram] = term_by_doc[ngram] + 1
                else:
                    term_by_doc[ngram] = 1
            start = end
            self.task.push()

        # filter by min_df / max_df
        un_count = self.units_count if self.search_similar_text_units else self.documents_count
        up_margin = math.floor(self.max_df * un_count)
        lw_margin = self.min_df if isinstance(self.min_df, int) else math.ceil(self.min_df * un_count)
        key_list = []  # type: List[str]
        for key in term_by_doc:
            count = term_by_doc[key]
            if count < lw_margin or count > up_margin:
                continue
            key_list.append(key)
        key_list.sort()
        return key_list

    def build_doclevel_matrices(self, vocabulary: List[str]):
        return self.build_matrices(vocabulary,
                                   self.get_doc_vocabulary_textset,
                                   self.doc_vocabulary_chunk_size,
                                   self.documents_count)

    def build_unitlevel_matrices(self, vocabulary: List[str]):
        return self.build_matrices(vocabulary,
                                   self.get_unit_vocabulary_textset,
                                   self.unit_vocabulary_chunk_size,
                                   self.units_count)

    def build_matrices(self,
                       vocabulary: List[str],
                       get_textset,
                       chunk_size: int,
                       total: int) -> List[csr_matrix]:
        """
        Calculate terms (ngrams) - document matrices for all documents or
        text units, reading their text from DB by chunks
        :param vocabulary: list of unique terms, sorted
        :param get_textset: query that return text data - strings, probably, multilines
        :param chunk_size: chunk size - count of string objects to read at once
        :param total: total records to read
        :return: term distribution matrices
        """
        ngram_range = (1, 3,) if self.term_type == self.TERM_TYPE_WORD_3GRAM \
            else (1, 1,) if self.term_type == self.TERM_TYPE_WORDS \
            else (self.char_ngrams_length, self.char_ngrams_length,)
        analyzer = 'char' if self.term_type == self.TERM_TYPE_CHAR_NGRAM else 'word'
        model = TfidfVectorizer(
            ngram_range=ngram_range,
            analyzer=analyzer,
            stop_words='english',
            vocabulary=vocabulary,
            use_idf=self.use_idf)

        dtm_chunked = []
        start = 0
        while start < total:
            end = start + chunk_size
            end = min(end, total)
            texts_set = get_textset(start, end)  # type:List[str]
            dtm_chunked.append(model.fit_transform(texts_set))
            start = end
            self.task.push()
            self.log_check_flood('build_matrices',
                                 f'build_matrices({start} of {total} processed)')

        return dtm_chunked

    def get_doc_vocabulary_textset(self, start: int, end: int) -> List[str]:
        """
        Gets text (string objects) for start ... end of documents from the source query
        (either all documents or some project's documents)
        :param start: start of the fragment
        :param end: end of the fragment
        :return: string lists by document
        """
        text_query = self.doc_query[start:end]
        text_list = [d.full_text.lower() for d in text_query] if self.ignore_case \
            else [d.full_text for d in text_query]
        return text_list

    def get_unit_vocabulary_textset(self, start: int, end: int) -> List[str]:
        """
        Gets text (string objects) for start ... end of TextUnit corpus from the source query
        (either all units or some project's units)
        :param start: start of the fragment
        :param end: end of the fragment
        :return: TestUnits' text (string) list
        """
        text_query = self.text_unit_query[start:end]
        texts_set = [t.lower() for t in text_query.values_list('textunittext__text', flat=True)] \
            if self.ignore_case else list(text_query.values_list('textunittext__text', flat=True))
        return texts_set

    @staticmethod
    def get_chunks(iterable: List[str], chunk_size: int) -> Generator[List[str], None, None]:
        """
        Yield [chunk_size] records from a list of strings
        :param iterable: list of strings
        :param chunk_size: chunk size
        :return: yield returns [chunk_size], [chunk_size], ... [] records
        """
        size = len(iterable)
        if size < chunk_size:
            yield iterable
        chunks_nb = int(size / chunk_size)
        iter_ints = range(0, chunks_nb)
        for i in iter_ints:
            j = i * chunk_size
            if i + 1 < chunks_nb:
                k = j + chunk_size
                yield iterable[j:k]
            else:
                yield iterable[j:]

    def get_ngrams(self, texts: List[str]) -> Iterable[str]:
        """
        Make 3-word corteges out of words' list if self.term_type is 'WORD_3GRAMS'
        return words from text if self.term_type == 'WORDS'
        else return ngrams from characters 'CHAR_NGRAMS'
        :param texts: words' list
        :return: list of 1...3-word corteges: {'word_1', 'word_1 word_2', 'word_1 word_2 word_3', 'word_4', ...}
        """
        all_ngrams = []

        if self.term_type == self.TERM_TYPE_CHAR_NGRAM:
            for text in texts:
                word_set = set()  # type: Set[str]
                wrd = ''
                for c in text:
                    wrd += c
                    if len(wrd) > self.char_ngrams_length:
                        wrd = wrd[1:]
                    word_set.add(wrd)
                for ngram in word_set:
                    all_ngrams.append(ngram)
            return all_ngrams

        if self.term_type == self.TERM_TYPE_WORDS:
            all_words = []
            for text in texts:
                word_set = set()  # type: Set[str]
                for wrd in self.reg_wordsplit.split(text):
                    if wrd:
                        word_set.add(wrd)
                for wrd in word_set:
                    all_words.append(wrd)
            return all_words

        # if self.term_type == self.TERM_TYPE_WORD_3GRAM:
        # This EOF is here because we produce ngrams on a bunch of documents in a
        # single time. So when we will produce our vocabulary after that we want to
        # be able to avoid associating terms that are not really associated.
        for text in texts:
            allterms = self.reg_wordsplit.split(text)
            ngram_set = set()  # type:Set[str]
            # create 1-grams, 2-grams and 3-grams and zip() them all.
            for g in zip(ngrams(allterms, 1), ngrams(allterms, 2), ngrams(allterms, 3)):
                for w in map(lambda wrd: ' '.join(wrd), g):
                    ngram_set.add(w)
            for w in ngram_set:
                all_ngrams.append(w)
        return all_ngrams

    def push_time(self, time_tag: str, purge: bool = False) -> None:
        """
        Store time + tag for future profiling in log_timing
        :param time_tag: time tag (stage, function called etc)
        :param purge: clear exising records
        """
        if purge:
            self.timings = []
        self.timings.append((time_tag, datetime.datetime.now(),))

    def log_timing(self, prefix: str) -> None:
        """
        Prints time diffs between self.timings tagged moments
        :param prefix: a line to print before the rest of the data
        """
        if not self.timings or len(self.timings) == 1:
            return
        text = f'{prefix} took {self.timings[-1][1] - self.timings[0][1]}:'
        for i in range(1, len(self.timings)):
            delta = self.timings[i][1] - self.timings[i - 1][1]
            text += f'\n{self.timings[i][0]} - {delta}'
        self.task.log_debug(text)

    def log_check_flood(self, log_key: str, log_msg: str) -> None:
        now = datetime.datetime.now()
        last_logged = self.time_logged.get(log_key)
        if last_logged:
            seconds_passed = (now - last_logged).total_seconds()
            if seconds_passed < self.LOG_FLOOD_INTERVAL_SECONDS:
                return
        self.time_logged[log_key] = now
        self.task.log_info(log_msg)
