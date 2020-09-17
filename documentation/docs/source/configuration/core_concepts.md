Core Concepts
-------------

ContraxSuite's software is [containerized](https://en.wikipedia.org/wiki/Containerization), which allows for nimble deployment and auto-scaling of computing resources. We use the leading industry-standard containerization service, [Docker](https://www.docker.com/), the de facto standard to build and share containerized apps - from desktop, to the cloud.

ContraxSuite incorporates leading open source tools to create a secure, user-friendly experience. Our user interface is built using the [React JavaScript library (ReactJS)](https://reactjs.org/), with the [Django REST framework](https://www.django-rest-framework.org/) for backend development.

[Elasticsearch](https://www.elastic.co/elasticsearch/) is a distributed, RESTful search and analytics engine capable of addressing many use cases.

[Kibana](https://www.elastic.co/kibana) is a free and open user interface that lets you visualize your Elasticsearch data and navigate the Elastic Stack

[Logstash](https://www.elastic.co/logstash) is a free and open server-side data processing pipeline that ingests data from a multitude of sources, allowing for fast and easy sending of data.

#### Document Processing

ContraxSuite uses many open source software packages and toolkits for optical character recognition (OCR), database management, worker node scaling, and other processes. Documents uploaded to ContraxSuite undergo OCR in order to become fully machine-readable. For OCR, ContraxSuite uses Apache Tika and Google Tesseract.

[Apache Tika](https://tika.apache.org/1.23/gettingstarted.html) is an OCR toolkit that detects and extracts metadata and text from many common file types (*e.g.*, PPT, XLS, RTF, PDF). Documents uploaded into ContraxSuite are scanned by Tika so that the documents are machine-readable.

[Tesseract](https://github.com/tesseract-ocr/tesseract) supports unicode (UTF-8), and can also recognize more than 100 languages. Tesseract supports various output formats: plain text, hOCR (HTML), PDF, invisible-text-only PDF, TSV.

#### Python Data Science Libraries

[NLTK](https://www.nltk.org/): Natural Language Toolkit (NLTK) is the leading platform for building Python programs to work with human language data.

[Scikit-learn](https://scikit-learn.org/stable/): scikit-learn features various classification, regression, and clustering algorithms, including support vector machines (SVM), random forests, gradient boosting, k-means and DBSCAN. It is designed to interoperate with the Python numerical and scientific libraries [NumPy](https://numpy.org/) and [SciPy](https://www.scipy.org/).

[LexNLP](../introduction/overview.html#lexnlp): LexNLP is the open source legal domain-specific natural language processing library. For documentation on LexNLP, [click here](http://publicdocs.contraxsuite.com/lexnlp/index.html).

#### Database Management

ContraxSuite uses [PostgreSQL](https://www.postgresql.org/), the world's most advanced open source relational database management system (RDBMS). The flexibility of Postgres allows ContraxSuite to be deployed on-premise, in the cloud, or in hybrid deployments.

---

#### How ContraxSuite Manages Data

ContraxSuite labels documents as "binary," "multi-class," and/or "multi-label".
* Binary: a document is either labeled as "Contract" **or** "NOT Contract"
* Binary: a document is either labeled "Amendment/Modification" **or** "Original"
* Multi-Class: a document is either "Draft" **or** "Signed" **or** "Executed"
* Multi-Class: a document is either "License" **or** "Lease" **or** "Employment" **or** "Other"
* Multi-Label: a document is "License" **and/or** "Lease" **and/or** Employment"
* ContraxSuite can also connect and order amendments to their originals, based on parties + historically referenced effective dates

ContraxSuite can also identify the internal structure of a document:
* Titles of documents, plus any "attached" ancillaries, such as Exhibits, Appendices, Addenda
* Tables of contents
* Sections, with properly captured hierarchies (*e.g.*, "Section 3, Subsection 3.A")
* Signature blocks
* Individual text units at the level of sentences, paragraphs, sections, and clauses (*see ["Identification Methods"](./core_concepts.html#identification-methods), below*)

ContraxSuite can find clauses in a document:
* Clauses that occur once in every document (**exactly** 1 match per document)
* Any clauses that may occur 0 or more times in a document (0+ matches per document)

ContraxSuite can extract facts from a document:
* Facts that occur once in every document (exactly 1 match per document). *E.g.*, Effective Dates
* Facts that may occur 0 or more times in a document (**0+** matches per document). *E.g.*, Prices for multiple items
* Any additional items and text units that [LexNLP can find](../introduction/overview.html#lexnlp).

#### Language and Content Detection

After OCR is conducted on a document, ContraxSuite can recognize the language(s) used in the document, as well as the language(s) of individual text units. Almost all subsequent processing will depend on the language of the content, such as sentence segmentation, part-of-speech tagging, clause classifiers, date location/extraction, *etc.*

After OCR and language detection, ContraxSuite detects what type of content each individual document contains. This analysis is based on file type, text unit length, word use, *etc*. Content type detection depends a great deal on whether the content is written in a formal style (like most contracts), or an informal style (such as emails). This stage is also when the detected content can be labeled as, for example, a financial contract versus an employment contract.

#### Structured Information Detection

ContraxSuite converts unstructured sequences of tokens into structured data types, such as dates, durations, or monetary amounts. This structuring can be done using techniques like [regular expressions](https://en.wikipedia.org/wiki/Regular_expression), or Python methods.

The goal of LexNLP, and of machine learning sequence classification, is to:
* Allow users to locate structured information without extracting structure
* Reduce the number of passes through entire documents
* Separate location logic from extraction logic so that multiple structuring approaches can be used, not just regular expressions

ContraxSuite determines whether a text unit contains zero or more types of structured information by classifying a sequence of tokens, either as a whole sequence or at the token level, through [I-O-B tagging](https://en.wikipedia.org/wiki/Inside%E2%80%93outside%E2%80%93beginning_(tagging)).

**Example:**
* Sentence A: Sequence-level classification
    * Contains a date (90%)
    * Contains a duration (90%)
    <br>
* Sentence A: Token-level IOB on a sentence that contains the following date and duration information:
    * B = 27th
    * I = of
    * I = December
    * I = 2019
    * B = six
    * I = months

The goal is for all locators to run in parallel, sharing the same feature vectors, through a multi-label classification model. The locators themselves do not structure the information, but they can identify whether and where structured information exists. This allows subsequent structured information extraction code to run efficiently over small subsets of text instead of entire documents.

Simple character frequency and token frequency techniques analyze the incidence of things like commas, periods, and bulleted lists, in order to inform the content type detection and data extraction processes. For example, documents typically have very few dates in them, so locators are written to identify the small number of sentences where dates do occur. Then, a regular expression engine parses an entire document - even if zero dates occur, this pass for regular expressions will not be re-used for any other tasks like durations, monetary amounts, *etc*.

#### Identification Methods

**Basic Match Types**
* Term match: for example, finding the word "insolvency" from the stem/lemma ("insolven"), or via word2vec
* Definition match: for example, finding the definition of "Lessor" and "Lessee" in a contract
* Regular expression (regexp) match: for example, a document that has "Purchase Order [0-9]+"
* Pre-trained [scikit-learn](https://scikit-learn.org/stable/) classifier match: a document has a classifier score > 0.5 (not retrained on user input)
* Can also support pre-trained external model classifier matches that may be more efficient than scikit-learn models

**Complex Match Types**
* Basic Match + Fact Present: for example, document has "insolvency" stem/lemma ("insolven") **and** a LexNLP percentage
* Multiple Basic Matches: for example, document has "insolvency" stem/lemma ("insolven") **and** regular expression "Purchase Order [0-9]+"
* Dynamic/online scikit-learn classifier match: for example, a document has a classifier score > 0.5 **and** is re-trained on user inputExtraction methods
* Filtering: for example, an overinclusive regex match **and then** a classifier score > 0.5 to narrow down results
* Prioritize multiple Match Types: *e.g.* try X first, then if nothing is found, try Y
* Find and Map: Finding a geographical value **and then** matching it to its country, or finding a company value **and then** matching it back to its parent company

**Basic Extraction Types**
* Take first/last/Nth (returns exactly **one** value)
* Take Mth, Nth (returns 2 or more values)
* Take greatest (last date, biggest amount, *etc.*)
* Take least (first date, smallest amount, *etc.*)
* Take the closest to some pre-determined value

**Conditional Types**
* Currency Filter: *e.g.* USD only
* Company Filter: *e.g.* LLC only
* Amounts Filter: *e.g.* Units = "pounds (lbs.)" only
* "Found In" Filter: *e.g.* first N pages, first N paragraphs, TOC, definitions

*See ["Creating Field Detectors"](../user_guides/power_users/create_field_detectors) page for more on customizing conditional data extraction*

**Token Classifiers**
* Take a token or token sequence with, *e.g.*, a score > 0.5
