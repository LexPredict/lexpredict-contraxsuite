# -*- coding: utf-8 -*-

# Django imports
from django import forms
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

# Project imports
from apps.common.widgets import LTRCheckboxField, LTRCheckboxWidget
from apps.analyze.models import TextUnitClassification, TextUnitClassifier

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2017, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.0/LICENSE.pdf"
__version__ = "1.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@lexpredict.com"


path_help_text_sample = '''
Relative path to a file with {}. A file should be in "&lt;ROOT_DIR&gt;/data/"
 or "&lt;APPS_DIR&gt;/media/%s" folder.''' % settings.FILEBROWSER_DIRECTORY


class LoadDocumentsForm(forms.Form):
    header = 'Parse documents to create create Documents and Text Units.'
    source_path = forms.CharField(
        max_length=1000,
        required=True,
        help_text='''
        Relative path to a folder with uploaded files.\n
        You can choose any folder or file in "/media/%s" folder.\n
        For example, "new" or "/".\n
        Create new folders and upload new documents if needed.'''
                  % settings.FILEBROWSER_DIRECTORY)
    source_type = forms.CharField(
        max_length=100,
        required=True)
    document_type = forms.CharField(
        max_length=100,
        required=True)
    delete = LTRCheckboxField(
        label=_("Delete existing Documents"),
        required=False)


class LoadTermsForm(forms.Form):
    header = 'Load terms from a dictionary sample.'
    dictionary_path = forms.CharField(
        max_length=1000,
        required=True,
        help_text=path_help_text_sample.format('dictionary sample'))
    delete = LTRCheckboxField(
        label=_("Delete existing Legal Terms"),
        initial=True,
        required=False)


class LoadGeoEntitiesForm(forms.Form):
    header = 'Load Geo Entities, Geo Relations, and Geo Aliases.'
    geo_entities_path = forms.CharField(
        max_length=1000,
        required=True,
        initial='geo_entities.csv',
        help_text=path_help_text_sample.format('Geo Entities'))
    geo_relations_path = forms.CharField(
        max_length=1000,
        required=True,
        initial='geo_relations.csv',
        help_text=path_help_text_sample.format('Geo Relations'))
    geo_aliases_path = forms.CharField(
        max_length=1000,
        required=True,
        initial='geo_aliases.csv',
        help_text=path_help_text_sample.format('Geo Aliases'))
    delete = LTRCheckboxField(
        label=_("Delete existing Geo Entities, Geo Relations, and Geo Aliases"),
        initial=True,
        required=False)


class LoadCourtsForm(forms.Form):
    header = 'Load courts from a dictionary sample.'
    dictionary_path = forms.CharField(
        max_length=1000,
        initial='us_courts.csv',
        required=True,
        help_text=path_help_text_sample.format('dictionary sample'))
    delete = LTRCheckboxField(
        label=_("Delete existing Courts"),
        initial=True,
        required=False)


class LocateGeoEntitiesForm(forms.Form):
    header = 'Locate Geo Entities and Geo Aliases in existing Text Units.'
    priority = LTRCheckboxField(
        label=_("Use first entity occurrence to resolve ambiguous entities"),
        initial=True,
        required=False)
    delete = LTRCheckboxField(
        label=_("Delete existing Geo Entity Usages and Geo Alias Usages"),
        initial=True,
        required=False)


class LocateTermsForm(forms.Form):
    header = 'Locate Legal Terms in existing Text Units.'
    delete = LTRCheckboxField(
        label=_("Delete existing Term Usages"),
        initial=True,
        required=False)


class LocatePartiesForm(forms.Form):
    header = 'Locate Parties in existing documents.'
    delete = LTRCheckboxField(
        label=_("Delete existing Parties and Party Usages"),
        initial=True,
        required=False)


class LocateDatesForm(forms.Form):
    header = 'Locate Dates in existing documents.'
    delete = LTRCheckboxField(
        label=_("Delete existing Date Usages"),
        initial=True,
        required=False)


class LocateDateDurationsForm(forms.Form):
    header = 'Locate Date Durations in existing documents.'
    delete = LTRCheckboxField(
        label=_("Delete existing Date Duration Usages"),
        initial=True,
        required=False)


class LocateDefinitionsForm(forms.Form):
    header = 'Locate Definitions in existing text units.'
    delete = LTRCheckboxField(
        label=_("Delete existing Definition Usages"),
        initial=True,
        required=False)


class LocateCourtsForm(forms.Form):
    header = 'Locate Courts in existing text units.'
    delete = LTRCheckboxField(
        label=_("Delete existing Court Usages"),
        initial=True,
        required=False)


class LocateCurrenciesForm(forms.Form):
    header = 'Locate Currencies in existing text units.'
    use_symbols = LTRCheckboxField(
        label=_("Use symbols"),
        widget=LTRCheckboxWidget(attrs={'class': 'min-one-of'}),
        initial=True,
        required=False)
    use_short_names = LTRCheckboxField(
        label=_("Use short names"),
        widget=LTRCheckboxWidget(attrs={'class': 'min-one-of'}),
        initial=True,
        required=False)
    use_abbreviations = LTRCheckboxField(
        label=_("Use abbreviations"),
        widget=LTRCheckboxWidget(attrs={'class': 'min-one-of'}),
        initial=True,
        required=False)
    delete = LTRCheckboxField(
        label=_("Delete existing Currency Usages"),
        initial=True,
        required=False)


class ExistedClassifierClassifyForm(forms.Form):
    header = 'Classify Text Units using an existing Classifier.'
    classifier = forms.ChoiceField(
        choices=[(c.pk, c.name) for c in TextUnitClassifier.objects.filter(is_active=True)],
        required=True)
    sample_size = forms.IntegerField(
        min_value=1,
        required=False,
        help_text='Number of Documents to process. Leave blank to process all Documents.')
    min_confidence = forms.IntegerField(
        min_value=0,
        max_value=100,
        initial=90,
        required=True,
        help_text='Store values with confidence greater than (%).')
    delete_suggestions = LTRCheckboxField(
        label=_("Delete ClassifierSuggestions of Classifier specified above."),
        required=False)


class CreateClassifierClassifyForm(forms.Form):
    header = 'Classify Text Units by creating a new Classifier.'
    CLASSIFIER_NAME_CHOICES = (
        ('LogisticRegressionCV', 'LogisticRegressionCV'),
        ('MultinomialNB', 'MultinomialNB'),
        ('ExtraTreesClassifier', 'ExtraTreesClassifier'),
        ('RandomForestClassifier', 'RandomForestClassifier'),
        ('SVC', 'SVC'),
    )
    classify_by = forms.ChoiceField(
        choices=[('terms', 'Legal Terms'),
                 ('parties', 'Parties'),
                 ('entities', 'Geo Entities')],
        required=True,
        help_text='Classify using terms, parties or geo entities.')
    algorithm = forms.ChoiceField(
        choices=CLASSIFIER_NAME_CHOICES,
        required=True,
        initial='LogisticRegressionCV',
        help_text='Text Unit Classifier name')
    class_name = forms.ChoiceField(
        choices=[(class_name, class_name) for class_name in
                 set(TextUnitClassification.objects.values_list('class_name', flat=True))],
        required=True,
        help_text='Text Unit class name')
    sample_size = forms.IntegerField(
        min_value=1,
        required=False,
        help_text='Number of Documents to process. Leave blank to process all Documents.')
    min_confidence = forms.IntegerField(
        min_value=0,
        max_value=100,
        initial=90,
        required=True,
        help_text='Store values with confidence greater than (%).')
    options = forms.BooleanField(
        widget=forms.CheckboxInput(attrs={
            'class': 'bt-switch',
            'data-on-text': 'Default',
            'data-off-text': 'Advanced',
            'data-on-color': 'default',
            'data-off-color': 'success',
            'data-size': 'small'}),
        initial=True,
        required=False,
        help_text='Show advanced options.')
    svc_c = forms.FloatField(
        label='C',
        min_value=0,
        initial=1.0,
        required=True,
        help_text='Penalty parameter C of the error term.')
    svc_kernel = forms.ChoiceField(
        label='kernel',
        choices=[('rbf', 'rbf'),
                 ('linear', 'linear'),
                 ('poly', 'poly'),
                 ('sigmoid', 'sigmoid'),
                 ('precomputed', 'precomputed')],
        required=True,
        initial='rbf',
        help_text='Specifies the kernel type to be used in the algorithm.')
    svc_gamma = forms.FloatField(
        label='gamma',
        min_value=0,
        required=False,
        help_text='Kernel coefficient for ‘rbf’, ‘poly’ and ‘sigmoid’. '
                  'If gamma is ‘auto’ then 1/n_features will be used instead.')
    mnb_alpha = forms.FloatField(
        label='alpha',
        min_value=0,
        initial=1.0,
        required=True,
        help_text='Additive (Laplace/Lidstone) smoothing parameter (0 for no smoothing).')
    rfc_etc_n_estimators = forms.IntegerField(
        label='n_estimators',
        min_value=1,
        initial=10,
        required=True,
        help_text='The number of trees in the forest.')
    rfc_etc_criterion = forms.ChoiceField(
        label='criterion',
        choices=[('gini', 'gini'),
                 ('entropy', 'entropy')],
        required=True,
        initial='gini',
        help_text='The function to measure the quality of a split.')
    rfc_etc_max_features = forms.IntegerField(
        label='max_features',
        min_value=1,
        required=False,
        help_text='The number of features to consider when looking for the best split.'
                  ' Integer or blank for "auto".')
    rfc_etc_max_depth = forms.IntegerField(
        label='max_depth',
        min_value=1,
        required=False,
        help_text='The maximum depth of the tree.'
                  ' If None, then nodes are expanded until all leaves are pure'
                  ' or until all leaves contain less than min_samples_split samples.')
    rfc_etc_min_samples_split = forms.IntegerField(
        label='min_samples_split',
        min_value=1,
        initial=2,
        required=True,
        help_text='The minimum number of samples required to split an internal node.')
    rfc_etc_min_samples_leaf = forms.IntegerField(
        label='min_samples_leaf',
        min_value=1,
        initial=1,
        required=True,
        help_text='The minimum number of samples required to be at a leaf node.')
    lrcv_cs = forms.IntegerField(
        label='cs',
        min_value=1,
        initial=10,
        required=True,
        help_text='Each of the values in Cs describes the inverse of regularization strength.')
    lrcv_fit_intercept = forms.BooleanField(
        label='fit_intercept',
        required=False,
        help_text='Specifies if a constant (a.k.a. bias or intercept)'
                  ' should be added to the decision function.')
    lrcv_multi_class = forms.ChoiceField(
        label='multi_class',
        choices=[('ovr', 'ovr'),
                 ('multinomial', 'multinomial')],
        required=True,
        initial='ovr',
        help_text='If the option chosen is ‘ovr’, then a binary problem is fit for each label. '
                  'Else the loss minimised is the multinomial loss fit across the '
                  'entire probability distribution. '
                  'Works only for the ‘newton-cg’, ‘sag’ and ‘lbfgs’ solver.')
    lrcv_solver = forms.ChoiceField(
        label='solver',
        choices=[('lbfgs', 'lbfgs'),
                 ('newton-cg', 'newton-cg'),
                 ('liblinear', 'liblinear'),
                 ('sag', 'sag')],
        required=True,
        initial='lbfgs',
        help_text='Algorithm to use in the optimization problem.')
    use_tfidf = LTRCheckboxField(
        label=_("Use TF-IDF to normalize data"),
        widget=LTRCheckboxWidget(),
        required=False)
    delete_classifier = LTRCheckboxField(
        label=_("Delete existing Classifiers of class name specified above."),
        required=False)
    delete_suggestions = LTRCheckboxField(
        label=_("Delete ClassifierSuggestions of class name specified above."),
        required=False)


class ClusterForm(forms.Form):
    header = 'Clustering Documents and/or Text Units by Legal Terms, Entities or Parties.'
    do_cluster_documents = LTRCheckboxField(
        label=_("Cluster Documents"), initial=True,
        widget=LTRCheckboxWidget(attrs={'class': 'min-one-of'}),
        required=False)
    do_cluster_text_units = LTRCheckboxField(
        label=_("Cluster Text Units"),
        widget=LTRCheckboxWidget(attrs={'class': 'min-one-of'}),
        required=False)
    cluster_by = forms.ChoiceField(
        choices=[('terms', 'Legal Terms'),
                 ('parties', 'Parties'),
                 ('entities', 'Geo Entities')],
        required=True,
        help_text='Cluster by terms, parties or geo entities.')
    using = forms.ChoiceField(
        label='Algorithm',
        choices=[('MiniBatchKMeans', 'MiniBatchKMeans'),
                 ('KMeans', 'KMeans'),
                 ('Birch', 'Birch'),
                 ('DBSCAN', 'DBSCAN')],
        required=True,
        initial='MiniBatchKMeans',
        help_text='Clustering algorithm model name.')
    name = forms.CharField(
        max_length=100,
        required=True)
    description = forms.CharField(
        max_length=200,
        required=False)
    options = forms.BooleanField(
        widget=forms.CheckboxInput(attrs={
            'class': 'bt-switch',
            'data-on-text': 'Simple',
            'data-off-text': 'Advanced',
            'data-on-color': 'info',
            'data-off-color': 'success',
            'data-size': 'small'}),
        initial=True,
        required=False,
        help_text='Show advanced options.')
    n_clusters = forms.IntegerField(
        label='n_clusters',
        min_value=1,
        initial=3,
        required=True,
        help_text='Number of clusters.')
    kmeans_max_iter = forms.IntegerField(
        label='max_iter',
        min_value=1,
        initial=100,
        required=True,
        help_text='Maximum number of iterations for a single run.')
    kmeans_n_init = forms.IntegerField(
        label='n_init',
        min_value=1,
        initial=10,
        required=True,
        help_text='Number of time the k-means algorithm will be run with different centroid seeds. '
                  'The final results will be the best output of n_init consecutive runs in '
                  'terms of inertia.')
    mb_kmeans_batch_size = forms.IntegerField(
        label='batch_size',
        min_value=1,
        initial=100,
        required=True,
        help_text='Size of the mini batches.')
    birch_threshold = forms.FloatField(
        label='threshold',
        min_value=0,
        initial=0.5,
        required=True,
        help_text='The radius of the subcluster obtained by merging a new sample and the closest '
                  'subcluster should be lesser than the threshold.'
                  ' Otherwise a new subcluster is started.')
    birch_branching_factor = forms.IntegerField(
        label='branching_factor',
        min_value=1,
        initial=50,
        required=True,
        help_text='Maximum number of CF subclusters in each node.')
    dbscan_eps = forms.FloatField(
        label='eps',
        min_value=0,
        initial=0.5,
        required=True,
        help_text='The maximum distance between two samples for them to be considered '
                  'as in the same neighborhood.')
    dbscan_leaf_size = forms.IntegerField(
        label='leaf_size',
        min_value=1,
        initial=30,
        required=True,
        help_text='Leaf size passed to BallTree or cKDTree. '
                  'This can affect the speed of the construction and query, '
                  'as well as the memory required to store the tree.')
    dbscan_p = forms.FloatField(
        label='p',
        min_value=0,
        required=False,
        help_text='Leaf size passed to BallTree or cKDTree. '
                  'This can affect the speed of the construction and query, '
                  'as well as the memory required to store the tree.')
    use_idf = LTRCheckboxField(
        label=_("Use TF-IDF to normalize data"),
        widget=LTRCheckboxWidget(),
        required=False)
    delete_type = LTRCheckboxField(
        label=_('Delete existed Clusters of the "Cluster By" and "Algorithm" specified above'),
        widget=LTRCheckboxWidget(attrs={'class': 'max-one-of'}),
        required=False)
    delete = LTRCheckboxField(
        label=_("Delete all existed Clusters"),
        widget=LTRCheckboxWidget(attrs={'class': 'max-one-of'}),
        required=False)

    def clean(self):
        cleaned_data = super().clean()
        do_cluster_documents = cleaned_data.get("do_cluster_documents")
        do_cluster_text_units = cleaned_data.get("do_cluster_text_units")
        if not any([do_cluster_documents, do_cluster_text_units]):
            self.add_error('do_cluster_documents', 'Please choose either Documents or Text Units')
            self.add_error('do_cluster_text_units', 'Please choose either Documents or Text Units')


class SimilarityForm(forms.Form):
    header = 'Identify similar Documents and/or Text Units.'
    search_similar_documents = LTRCheckboxField(
        label=_("Identify similar Documents."),
        initial=True,
        widget=LTRCheckboxWidget(attrs={'class': 'min-one-of'}),
        required=False)
    search_similar_text_units = LTRCheckboxField(
        label=_("Identify similar Text Units."),
        widget=LTRCheckboxWidget(attrs={'class': 'min-one-of'}),
        required=False)
    min_similarity = forms.IntegerField(
        min_value=50, max_value=100, initial=90,
        label=_("Min. Similarity Value %")
    )
    delete = LTRCheckboxField(
        label=_("Delete existing Similarity objects."),
        initial=True,
        required=False)


class PartySimilarityForm(forms.Form):
    header = 'Identify similar Parties.'
    case_sensitive = LTRCheckboxField(
        label=_('Case Sensitive'),
        initial=True,
        required=False)
    similarity_type = forms.ChoiceField(
        choices=[('token_set_ratio', 'token_set_ratio'),
                 ('token_sort_ratio', 'token_sort_ratio')],
        required=True,
        initial='token_set_ratio')
    similarity_threshold = forms.IntegerField(
        min_value=0, max_value=100, initial=90,
        help_text=_("Min. Similarity Value 0-100%.")
    )
    delete = LTRCheckboxField(
        label=_("Delete existing PartySimilarity objects."),
        initial=True,
        required=False)
