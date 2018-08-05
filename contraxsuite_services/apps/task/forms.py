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

# Standard imports
import os

# Third-party imports
from constance import config

# Django imports
from django import forms
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

# Project imports
from apps.common.widgets import LTRRadioField
from apps.common.forms import checkbox_field
from apps.analyze.models import TextUnitClassification, TextUnitClassifier
from apps.document.models import DocumentProperty, TextUnitProperty, DocumentType
from apps.project.models import Project
from apps.task.models import Task

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2018, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.1.2/LICENSE"
__version__ = "1.1.2"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"

path_help_text_sample = '''
Relative path to a file with {}. A file should be in "&lt;ROOT_DIR&gt;/data/"
 or "&lt;APPS_DIR&gt;/media/%s" folder.''' % settings.FILEBROWSER_DIRECTORY


class LoadDocumentsForm(forms.Form):
    header = 'Parse documents to create Documents and Text Units.'
    project = forms.ModelChoiceField(queryset=Project.objects.all(), required=False)
    source_path = forms.CharField(
        max_length=1000,
        required=True,
        help_text='''
        Relative path to a folder with uploaded files. For example, "new" or "/".<br />
        You can choose any folder or file in "/media/%s" folder.<br />
        Create new folders and upload new documents if needed.
        ''' % settings.FILEBROWSER_DIRECTORY)
    source_type = forms.CharField(
        max_length=100,
        required=False)
    document_type = forms.ModelChoiceField(queryset=DocumentType.objects.all(), required=False)
    detect_contract = checkbox_field("Detect if a document is contract", initial=True)
    delete = checkbox_field("Delete existing Documents")
    run_standard_locators = checkbox_field("Run Standard Locators", initial=False)


class BatchLoadDocumentsForm(forms.Form):
    header = 'Parse documents to create Documents and Text Units. <br />' \
             'Assign Documents to a Project.<br />' \
             'Run standard locators.'
    project = forms.ModelChoiceField(queryset=Project.objects.all(), required=True)
    source_path = forms.CharField(
        max_length=1000,
        required=True,
        help_text='''
        Relative path to a folder with uploaded files. For example, "new" or "/".<br />
        You can choose any folder under "{}".
        '''.format(os.path.join(settings.MEDIA_ROOT,
                                settings.FILEBROWSER_DIRECTORY)))
    # run_standard_locators = checkbox_field("Run Standard Locators", initial=False)


# sample form for custom task
class LocateTermsForm(forms.Form):
    header = 'Locate Terms in existing Text Units.'
    delete = checkbox_field("Delete existing Term Usages", initial=True)


def locate_field(label, parent_class='checkbox-parent'):
    return checkbox_field(label, input_class=parent_class)


def child_field(delete_tip=None, label='Delete existing usages', child_class='checkbox-child'):
    if delete_tip:
        label = "Delete existing %s Usages" % delete_tip
    return checkbox_field(label, input_class=child_class, label_class='checkbox-small level-1')


class LocateForm(forms.Form):
    header = 'Locate specific terms in existing text units.'

    locate_all = checkbox_field(
        label="Locate all items / Reverse choice",
        label_class='main-label')

    geoentity_locate = locate_field("Geo Entities and Geo Aliases", parent_class='')
    geoentity_priority = child_field(
        label="Use first entity occurrence to resolve ambiguous entities",
        child_class='')
    geoentity_delete = child_field(
        label="Delete existing Geo Entity Usages and Geo Alias Usages",
        child_class='')

    date_locate = locate_field(label='Dates', parent_class='')
    date_strict = child_field(label="Strict", child_class='')
    date_delete = child_field("Date", child_class='')

    amount_locate = locate_field('Amounts')
    amount_delete = child_field("Amount")

    citation_locate = locate_field("Citations")
    citation_delete = child_field("Citation")

    copyright_locate = locate_field("Copyrights")
    copyright_delete = child_field("Copyright")

    court_locate = locate_field('Courts')
    court_delete = child_field('Court')

    currency_locate = locate_field('Currencies')
    currency_delete = child_field('Currency')

    duration_locate = locate_field('Date Durations')
    duration_delete = child_field('Date Duration')

    definition_locate = locate_field('Definitions')
    definition_delete = child_field('Definition')

    distance_locate = locate_field('Distances')
    distance_delete = child_field('Distance')

    party_locate = locate_field('Parties')
    party_delete = child_field('Parties and Party Usages')

    percent_locate = locate_field('Percents')
    percent_delete = child_field('Percent')

    ratio_locate = locate_field('Ratios')
    ratio_delete = child_field('Ratio')

    regulation_locate = locate_field('Regulations')
    regulation_delete = child_field('Regulation')

    term_locate = locate_field('Terms')
    term_delete = child_field('Term')

    trademark_locate = locate_field('Trademarks')
    trademark_delete = child_field('Trademark')

    url_locate = locate_field('Urls')
    url_delete = child_field('Url')

    parse = LTRRadioField(
        choices=(('paragraphs', 'Parse Text Units with "paragraph" type'),
                 ('sentences', 'Parse Text Units with both "paragraph" and "sentence" types')),
        help_text='Warning! Parsing both "paragraph" and "sentence" Text Unit types'
                  ' will take much more time',
        initial='paragraphs',
        required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in list(self.fields.keys()):
            if field in ['parse', 'locate_all']:
                continue
            field_name = field.split('_')[0]
            available_locators = list(settings.REQUIRED_LOCATORS) + list(
                config.standard_optional_locators)
            if field_name not in available_locators:
                del self.fields[field]


class ExistedClassifierClassifyForm(forms.Form):
    header = 'Classify Text Units using an existing Classifier.'
    classifier = forms.ChoiceField(
        choices=[(c.pk, c.name) for c in TextUnitClassifier.objects.filter(is_active=True)],
        widget=forms.widgets.Select(attrs={'class': 'chosen'}),
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
    delete_suggestions = checkbox_field(
        "Delete ClassifierSuggestions of Classifier specified above.")


options_field_kwargs = dict(
    widget=forms.CheckboxInput(attrs={
        'class': 'bt-switch',
        'data-on-text': 'Default',
        'data-off-text': 'Advanced',
        'data-on-color': 'info',
        'data-off-color': 'success',
        'data-size': 'small'}),
    initial=True,
    required=False,
    help_text='Show advanced options.')


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
        choices=[('terms', 'Terms'),
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
    options = forms.BooleanField(**options_field_kwargs)
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
    use_tfidf = checkbox_field(
        "Use TF-IDF to normalize data")
    delete_classifier = checkbox_field(
        "Delete existing Classifiers of class name specified above.")
    delete_suggestions = checkbox_field(
        "Delete ClassifierSuggestions of class name specified above.")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['class_name'] = forms.ChoiceField(
            choices=[(class_name, class_name) for class_name in
                     set(TextUnitClassification.objects.values_list('class_name', flat=True))],
            required=True,
            help_text='Text Unit class name')


class ClusterForm(forms.Form):
    header = 'Clustering Documents and/or Text Units by Terms, Entities or Parties.'
    do_cluster_documents = checkbox_field(
        "Cluster Documents", initial=True, input_class='min-one-of')
    do_cluster_text_units = checkbox_field(
        "Cluster Text Units", input_class='min-one-of')
    cluster_by = forms.MultipleChoiceField(
        widget=forms.SelectMultiple(attrs={'class': 'chosen'}),
        choices=[('date', 'Dates'),
                 ('duration', 'Date Durations'),
                 ('term', 'Terms'),
                 ('party', 'Parties'),
                 ('entity', 'Geo Entities'),
                 ('court', 'Courts'),
                 ('currency_name', 'Currency Name'),
                 ('currency_value', 'Currency Value'),
                 ('metadata', 'Document Metadata'),
                 ('document_type', 'Document Type'),
                 ('source_type', 'Document Source Type')],
        required=True,
        help_text='Cluster by terms, parties or other fields.')
    using = forms.ChoiceField(
        label='Algorithm',
        choices=[('MiniBatchKMeans', 'MiniBatchKMeans'),
                 ('KMeans', 'KMeans'),
                 ('Birch', 'Birch'),
                 ('DBSCAN', 'DBSCAN'),
                 ('LabelSpreading', 'LabelSpreading')],
        required=True,
        initial='MiniBatchKMeans',
        help_text='Clustering algorithm model name.')
    name = forms.CharField(
        max_length=100,
        required=True)
    description = forms.CharField(
        max_length=200,
        required=False)
    options = forms.BooleanField(**options_field_kwargs)
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
    ls_documents_property = forms.Field()
    ls_text_units_property = forms.Field()
    ls_max_iter = forms.IntegerField(
        label='max_iter',
        min_value=1,
        initial=5,
        required=True,
        help_text='Maximum number of iterations allowed.')
    # use_idf = checkbox_field("Use TF-IDF to normalize data")
    delete_type = checkbox_field(
        'Delete existed Clusters of the "Cluster By" and "Algorithm" specified above',
        input_class='max-one-of')
    delete = checkbox_field("Delete all existed Clusters", input_class='max-one-of')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if TextUnitProperty.objects.exists():
            choices = [(p, p) for p in sorted(
                set(TextUnitProperty.objects.values_list('key', flat=True)),
                key=lambda i: i.lower())]
            self.fields['ls_text_units_property'] = forms.ChoiceField(
                label='Text Unit Property Name',
                widget=forms.widgets.Select(attrs={'class': 'chosen'}),
                choices=choices,
                required=True,
                initial=choices[0][0])
        else:
            del self.fields['ls_text_units_property']
        if DocumentProperty.objects.exists():
            choices = [(p, p) for p in sorted(
                set(DocumentProperty.objects.values_list('key', flat=True)),
                key=lambda i: i.lower())]
            self.fields['ls_documents_property'] = forms.ChoiceField(
                label='Document Property Name',
                widget=forms.widgets.Select(attrs={'class': 'chosen'}),
                choices=choices,
                required=True,
                initial=choices[0][0])
        else:
            del self.fields['ls_documents_property']
        if not DocumentProperty.objects.exists() and not TextUnitProperty.objects.exists():
            self.fields['using'].choices = self.fields['using'].choices[:-1]

    def clean(self):
        cleaned_data = super().clean()
        do_cluster_documents = cleaned_data.get("do_cluster_documents")
        do_cluster_text_units = cleaned_data.get("do_cluster_text_units")
        if not any([do_cluster_documents, do_cluster_text_units]):
            self.add_error('do_cluster_documents', 'Please choose either Documents or Text Units')
            self.add_error('do_cluster_text_units', 'Please choose either Documents or Text Units')


class SimilarityForm(forms.Form):
    header = 'Identify similar Documents and/or Text Units.'
    search_similar_documents = checkbox_field(
        "Identify similar Documents.",
        input_class='min-one-of',
        initial=True)
    search_similar_text_units = checkbox_field(
        "Identify similar Text Units.",
        input_class='min-one-of')
    similarity_threshold = forms.IntegerField(
        min_value=50,
        max_value=100,
        initial=75,
        required=True,
        help_text=_("Min. Similarity Value 50-100%")
    )
    use_idf = checkbox_field("Use TF-IDF to normalize data")
    delete = checkbox_field("Delete existing Similarity objects.", initial=True)


class PartySimilarityForm(forms.Form):
    header = 'Identify similar Parties.'
    case_sensitive = checkbox_field('Case Sensitive', initial=True)
    similarity_type = forms.ChoiceField(
        choices=[('token_set_ratio', 'token_set_ratio'),
                 ('token_sort_ratio', 'token_sort_ratio')],
        required=True,
        initial='token_set_ratio')
    similarity_threshold = forms.IntegerField(
        min_value=0,
        max_value=100,
        initial=90,
        required=True,
        help_text=_("Min. Similarity Value 0-100%."))
    delete = checkbox_field("Delete existing PartySimilarity objects.", initial=True)


class UpdateElasticSearchForm(forms.Form):
    header = 'The update index command will freshen all of the content ' \
             'in Elasticsearch index. Use it after loading new documents.'


class TotalCleanupForm(forms.Form):
    header = 'Delete all existing Projects, Documents, Tasks, etc.'


class TaskDetailForm(forms.Form):
    name = forms.CharField(disabled=True)
    log = forms.CharField(widget=forms.Textarea, disabled=True)

    def __init__(self, prefix, instance: Task, initial):
        super().__init__()
        self.fields['name'].initial = instance.name
        self.fields['log'].initial = instance.get_task_log_from_elasticsearch()
