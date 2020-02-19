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

# build_classifier_binary()
# build_classifier_multi()

# TermUsage models
# TODO: Implement build_classifier_text_unit_termusage_model
# TODO: Implement build_classifier_document_termusage_model
# TODO: Implement build_classifier_project_text_unit_termusage_model
# TODO: Implement build_classifier_project_document_termusage_model
# TODO: Implement run_classifier_text_unit_termusage_model
# TODO: Implement run_classifier_document_termusage_model
# TODO: Implement run_classifier_project_text_unit_termusage_model
# TODO: Implement run_classifier_project_document_termusage_model

# TextUnitVector/DocumentVector models, e.g., doc2vec
# TODO: Implement build_classifier_text_unit_vector_model
# TODO: Implement build_classifier_document_vector_model
# TODO: Implement build_classifier_project_text_unit_vector_model
# TODO: Implement build_classifier_project_document_vector_model
# TODO: Implement run_classifier_text_unit_vector_model
# TODO: Implement run_classifier_document_vector_model
# TODO: Implement run_classifier_project_text_unit_vector_model
# TODO: Implement run_classifier_project_document_vector_model

# Raw text models
# TODO: Implement build_classifier_text_unit_text_model
# TODO: Implement build_classifier_document_text_model
# TODO: Implement build_classifier_project_text_unit_text_model
# TODO: Implement build_classifier_project_document_text_model
# TODO: Implement run_classifier_text_unit_text_model
# TODO: Implement run_classifier_document_text_model
# TODO: Implement run_classifier_project_text_unit_text_model
# TODO: Implement run_classifier_project_document_text_model

import datetime
import inspect
import pickle
import sys

import sklearn.feature_extraction
from sklearn.ensemble import ExtraTreesClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegressionCV
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import SVC

from apps.analyze.models import (
    TextUnitClassification, TextUnitClassifier, TextUnitClassifierAssessment,
    DocumentClassification, DocumentClassifier, DocumentClassifierAssessment,
    DocumentClassifierSuggestion, TextUnitClassifierSuggestion)
from apps.document.models import Document, TextUnit
from apps.analyze.ml.features import DocumentFeatures, TextUnitFeatures

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2020, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.5.0/LICENSE"
__version__ = "1.5.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class ClassifierEngine:
    """
    Base class to configure Classifier algorithm with default options
    and callable methods depending of algorithm class itself
    :Example:
        >>> engine_wrapper = RandomForestEngine(use_tfidf=True, **classifier_options)
        >>> classifier_model = engine_wrapper.get_model())
    Returns ClassifierEngine instance with attributes listed in __init__
    """
    engine = None
    option_prefix = None

    def __init__(self):
        """
        Inject class instance attributes to return after classifying
        """
        pass

    def __call__(self, use_tfidf: bool = True, **options):
        """
        Just call activated class instance to classify data.
        :param use_tfidf: bool - whether to use TF IDF Transformer
        :param options: **dict - unpacked classifier algorithm options
        :return: ClassifyEngine instance with attributes listed in __init__
        """
        self.use_tfidf = use_tfidf
        self.user_options = options
        self.model = self.get_model()
        return self.model

    def get_engine_options(self):
        """
        Get default classifying algorithm options from class attributes and substitute them with
        incoming user-defined options if they are, otherwise use defaults.
        Checks if get_some_callable_option method exists and uses it instead of class attribute.
        :return: dict - engine options dictionary
        """
        engine_options = dict()
        allowed_engine_option_names = inspect.getfullargspec(self.engine.__init__).args[1:]
        for option_name in allowed_engine_option_names:

            # get class attribute-option
            if hasattr(self, option_name):
                engine_options[option_name] = getattr(self, option_name)

            # get user option from incoming kwargs
            if option_name in self.user_options:
                engine_options[option_name] = self.user_options[option_name]
            elif self.option_prefix and self.option_prefix + option_name in self.user_options:
                engine_options[option_name] = self.user_options[self.option_prefix + option_name]

            # init callable option
            option_method = getattr(self, 'get_' + option_name, None)
            if option_method and callable(option_method):
                option_value = engine_options.get(option_name)
                engine_options[option_name] = option_method(option_value)

        return engine_options

    def get_some_callable_option(self, option_value=None):
        """
        Just a sample to show a signature of callable algorithm method
        """
        pass

    def get_model(self):
        """
        Activates classifier model with filled options
        :return: activated classifier model like RandomForestClassifier(**options)
        """
        options = self.get_engine_options()
        pipeline_seq = [('classifier', self.engine(**options))]
        if self.use_tfidf:
            pipeline_seq = [('tfidf', sklearn.feature_extraction.text.TfidfTransformer())] + pipeline_seq
        classifier_model = sklearn.pipeline.Pipeline(pipeline_seq)
        return classifier_model


class RandomForestClassifierEngine(ClassifierEngine):
    option_prefix = 'rfc_etc_'
    name = 'RandomForestClassifier'
    engine = RandomForestClassifier
    max_features = 'auto'
    n_estimators = 100
    min_samples_leaf = 2
    criterion = 'gini'


class ExtraTreesClassifierEngine(ClassifierEngine):
    option_prefix = 'rfc_etc_'
    name = 'ExtraTreesClassifier'
    engine = ExtraTreesClassifier
    max_features = 'auto'
    n_estimators = 100
    min_samples_leaf = 2
    criterion = 'gini'


class MultinomialNBEngine(ClassifierEngine):
    option_prefix = 'mnb_'
    name = 'MultinomialNB'
    engine = MultinomialNB
    alpha = 1


class SVCEngine(ClassifierEngine):
    option_prefix = 'svc_'
    name = 'SVC'
    engine = SVC
    kernel = 'rbf'
    gamma = 'auto'
    C = 1
    probability = True


class LogisticRegressionCVEngine(ClassifierEngine):
    option_prefix = 'lgcv_'
    name = 'LogisticRegressionCV'
    engine = LogisticRegressionCV
    Cs = 10
    multi_class = 'ovr'
    solver = 'lbfgs'


class ClassifyDocuments:
    """
    Classify documents/text units:
    - either use existing DocumentClassifier/TextUnitClassifier and create Classification objects
    - or create new Classifier based on existing Classification objects
      and then create Classification objects

    :Example: - #1 - build classifier using existing Classification objects of given "class_name"
                     and train_project_id and then classify items in test_project_id,
                     use features based on ['term', 'date'],
                     use LogisticRegressionCV classifier options passed as kwargs
                     (optionally with "lgcv_" prefix)
        >>> engine = ClassifyTextUnits()
        >>> classifier = engine.build_classifier(
        >>>           train_project_id=36, class_name='is_staff',
        >>>           classifier_assessment=False, classifier_algorithm='LogisticRegressionCV',
        >>>           classifier_name='New Name', classify_by=['term', 'date'],
        >>>           Cs=20, multi_class='ovr', lgcv_solver='lbfgs')
        >>> count = eng.run_classifier(
        >>>           classifier, test_project_id=36, min_confidence=80)

    :Example: - #2 - just run existing classifier on test_project_id text units - sentences
        >>> classifier = TextUnitClassifier.objects.get(pk=1)
        >>> engine = ClassifyTextUnits()
        >>> count = engine.run_classifier(classifier, test_project_id=36,
        >>>                               min_confidence=80, unit_type='sentence')
    """

    source_db_model = Document
    features_engine_class = DocumentFeatures
    classification_db_model = DocumentClassification
    classifier_db_model = DocumentClassifier
    assessment_db_model = DocumentClassifierAssessment
    suggestion_db_model = DocumentClassifierSuggestion
    target_id_name = 'document_id'

    def get_engine_wrapper(self, classifier_algorithm):
        """
        Get classify engine representing wrapper around classifying algorithm
        :param classifier_algorithm: str
        :return: ClassifyEngine()
        """
        this_module_classes = inspect.getmembers(sys.modules[__name__], inspect.isclass)
        engine_wrappers = {obj.name: obj for name, obj in this_module_classes
                           if issubclass(obj, ClassifierEngine) and obj != ClassifierEngine}
        if classifier_algorithm in engine_wrappers:
            return engine_wrappers[classifier_algorithm]()
        raise RuntimeError(
            "Classifier algorithm {} not implemented; must be one of {}".format(
                classifier_algorithm, str(list(engine_wrappers))))

    def build_classifier(self,
                         class_name,
                         train_queryset=None,
                         train_project_id=None,
                         unit_type='sentence',
                         class_missing='ignore',
                         classifier_algorithm='RandomForestClassifier',
                         classifier_assessment=True,
                         classifier_name=None,
                         metric_pos_label=None,
                         classify_by='term',
                         use_tfidf=True,
                         **classifier_options):
        """
        Build a text unit classifier for text units in `project_id` based on TextUnitClassification records with
        `class_name`, optionally normalizing with TF-IDF, using user-specified classification algorithm.
        Text units that do not have a TextUnitClassification are ignored by default; if `class_missing` is set to
        "negative", then
        :param class_name: str - classification name
        :param train_queryset: Document/TextUnit queryset to train classifier
        :param train_project_id: int - to train classifier
        :param unit_type: str - one of "sentence", "paragraph"
        :param class_missing: str['ignore', 'negative']
        :param classifier_algorithm: str - one of ['RandomForestClassifier',]
        :param classifier_assessment: bool - whether to create assessments
        :param classifier_options: **kwargs - options for a classifier engine
        :param classifier_name: str - classifier custom name OR None to use just defaults
        :param metric_pos_label: str - pos_label value for f1, precision, recall metrics
        :param classify_by: str or list[str] - source name - e.g. "term", or ["term", "date"]
        :param use_tfidf: bool - whether use TF IDF normalizer
        :return: classifier db object
        """
        # pre-initialize feature engine to get initial queryset
        feature_engine = self.features_engine_class(
            queryset=train_queryset,
            project_id=train_project_id,
            feature_source=classify_by,
            unit_type=unit_type,
            drop_empty_rows=True,
            drop_empty_columns=True,
        )
        target_qs = feature_engine.get_queryset()
        target_qs_ids = target_qs.values_list('pk', flat=True)

        # Get DocumentClassification/TextUnitClassification objects map ids to class values
        target_id_name__in = self.target_id_name + '__in'
        class_obj_map = dict(
            self.classification_db_model.objects
                .filter(**{'class_name': class_name, target_id_name__in: target_qs_ids})
                .values_list(self.target_id_name, 'class_value'))
        if not class_obj_map:
            raise RuntimeError('Empty Classification list of class_name="{}"'.format(class_name))

        # Document/TextUnit ids
        class_target_ids = class_obj_map.keys()

        # Keep outer branching on `class_missing`,
        # as data retrieval strategies are markedly different.
        if class_missing == "ignore":
            feature_engine.queryset = target_qs.filter(id__in=class_target_ids)

        elif class_missing == "negative":
            # In this case, we retrieve the complete project term-frequency matrix first,
            # then assign zero-initialized
            # target vector with equal size, only setting non-zero'd elements.
            pass

        # Get term frequency matrix
        feature_obj = feature_engine.get_features()

        # Now place the coded TUC values into the correct element of the target vector.
        target_vector = [class_obj_map[i] for i in feature_obj.item_index]

        # Build model
        engine_wrapper = self.get_engine_wrapper(classifier_algorithm)
        classifier_model = engine_wrapper(use_tfidf=use_tfidf, **classifier_options)

        # Train model
        classifier_model.fit(feature_obj.feature_df, target_vector)
        # Store additional params into model object
        # TODO: store in a classifier model?
        classifier_model.feature_names = feature_obj.feature_names
        classifier_model.use_tfidf = use_tfidf
        classifier_model.classify_by = classify_by
        classifier_model.unit_type = unit_type

        # Save model
        classify_by_str = ', '.join(classify_by) if isinstance(classify_by, (list, tuple))\
            else classify_by
        classifier = self.classifier_db_model(
            name="{}class={} algo={} tfidf={} by={}".format(
                'name={} '.format(classifier_name) if classifier_name else '',
                class_name, classifier_algorithm, use_tfidf, classify_by_str),
            version=datetime.datetime.now().isoformat(),
            class_name=class_name,
            is_active=True)
        classifier.model_object = pickle.dumps(classifier_model, protocol=pickle.HIGHEST_PROTOCOL)
        classifier.save()

        # Store assessments from in-sample performance
        if classifier_assessment:
            target_predicted = classifier_model.predict(feature_obj.feature_df)
            metric_names = ('accuracy', 'precision', 'recall', 'f1')
            ca_list = []
            for metric_name in metric_names:
                # get metric function and extra kwargs
                metric_func = getattr(sklearn.metrics, metric_name + '_score')
                metric_kwargs = dict()
                if 'pos_label' in inspect.getfullargspec(metric_func).args[1:]:
                    if metric_pos_label is None:
                        # TODO: raise exception or log
                        print('"pos_label" argument for "{}" metric is not defined, skipping.'
                              .format(metric_name))
                        continue
                    else:
                        metric_kwargs = {'pos_label': metric_pos_label}

                ca = self.assessment_db_model()
                ca.assessment_name = metric_name
                ca.assessment_value = metric_func(target_vector, target_predicted, **metric_kwargs)
                ca.classifier = classifier
                ca_list.append(ca)
            self.assessment_db_model.objects.bulk_create(ca_list)

        return classifier

    def run_classifier(self,
                       classifier,
                       test_queryset=None,
                       test_project_id=None,
                       unit_type='sentence',
                       min_confidence=50):
        """
        Run classifier model on provided data:
        test_queryset, test_project_id, classify_by, unit_type
        using min_confidence
        :param classifier: Document/TextUnitClassifier db object
        :param test_queryset: Document/TextUnit queryset  to get classification
        :param test_project_id: int -  to get classification
        :param unit_type: str - one of "sentence", "paragraph"
        :param min_confidence: int 0-100
        :return: number of created ClassifierSurrestion db objects
        """
        # get model
        clf_model = pickle.loads(classifier.model_object)
        min_confidence /= 100

        # get features according to model feature names
        feature_engine = self.features_engine_class(
            queryset=test_queryset,
            project_id=test_project_id,
            feature_source=clf_model.classify_by,
            unit_type=unit_type,
            drop_empty_rows=True,
            drop_empty_columns=True,
            external_feature_names=clf_model.feature_names
        )
        feature_obj = feature_engine.get_features()
        test_features_df = feature_obj.feature_df

        # predict/calculate proba
        proba_scores = clf_model.predict_proba(test_features_df)
        predicted = clf_model.predict(test_features_df)
        cs_list = []

        # create Suggestion objects
        run_date = datetime.datetime.now().isoformat()
        for item_no, _ in enumerate(feature_obj.item_index):
            confidence = max(proba_scores[item_no])
            if confidence < min_confidence:
                continue
            cs = self.suggestion_db_model()
            cs.classifier = classifier
            cs.classifier_run = run_date
            cs.classifier_confidence = max(proba_scores[item_no])
            setattr(cs, self.target_id_name, feature_obj.item_index[item_no])
            cs.class_name = classifier.class_name
            cs.class_value = predicted[item_no]
            cs_list.append(cs)
        self.suggestion_db_model.objects.bulk_create(cs_list)
        return len(cs_list)


class ClassifyTextUnits(ClassifyDocuments):
    source_db_model = TextUnit
    features_engine_class = TextUnitFeatures
    classification_db_model = TextUnitClassification
    classifier_db_model = TextUnitClassifier
    assessment_db_model = TextUnitClassifierAssessment
    suggestion_db_model = TextUnitClassifierSuggestion
    target_id_name = 'text_unit_id'
