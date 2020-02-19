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

# Django imports
from django import forms
from django.core.validators import MinValueValidator, MaxValueValidator

# Project imports
from apps.analyze.ml.features import DocumentFeatures
from apps.analyze.models import DocumentClassifier, TextUnitClassifier, \
    DocumentClassification, TextUnitClassification
from apps.common.forms import checkbox_field
from apps.project.models import Project

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2020, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.5.0/LICENSE"
__version__ = "1.5.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class TrainDocumentDoc2VecTaskForm(forms.Form):
    header = 'Train doc2vec model from Document queryset.'

    source = forms.CharField(initial='document', widget=forms.HiddenInput())
    transformer_name = forms.CharField(max_length=200, required=False)
    vector_size = forms.IntegerField(initial=100, required=False)
    window = forms.IntegerField(initial=10, required=False)
    min_count = forms.IntegerField(initial=10, required=False)
    dm = forms.IntegerField(initial=1, required=False, validators=(MinValueValidator(0),
                                                                   MaxValueValidator(1)))
    project = forms.ModelMultipleChoiceField(
        queryset=Project.objects.all(),
        widget=forms.SelectMultiple(
            attrs={'class': 'chosen compact'}),
        required=False)

    def clean(self):
        cleaned_data = super().clean()
        cleaned_data['project_ids'] = list(cleaned_data['project'].values_list('pk', flat=True)) \
            if cleaned_data['project'] is not None else None
        del cleaned_data['project']


class TrainTextUnitDoc2VecTaskForm(TrainDocumentDoc2VecTaskForm):
    header = 'Train doc2vec model from Text Unit queryset.'

    source = forms.CharField(initial='text_unit', widget=forms.HiddenInput())
    text_unit_type = forms.ChoiceField(choices=(('sentence', 'sentence'),
                                                ('paragraph', 'paragraph')),
                                       required=True)


class BaseRunClassifierForm(forms.Form):
    min_confidence = forms.IntegerField(
        min_value=0,
        max_value=100,
        initial=90,
        required=True,
        help_text='Store values with confidence greater than (%).')
    delete_suggestions = checkbox_field(
        "Delete ClassifierSuggestions of Classifier specified above.")
    project = forms.ModelChoiceField(queryset=Project.objects.order_by('-pk'),
                                     widget=forms.widgets.Select(attrs={'class': 'chosen'}),
                                     required=True,
                                     label='Restrict to project')
    field_order = ['classifier', 'project', 'min_confidence', 'delete_suggestions']


class RunTextUnitClassifierForm(BaseRunClassifierForm):
    header = 'Classify Text Units using an existing Classifier.'
    classifier = forms.ModelChoiceField(
        queryset=TextUnitClassifier.objects.filter(is_active=True).order_by('name'),
        widget=forms.widgets.Select(attrs={'class': 'chosen'}),
        required=True)
    target = forms.CharField(max_length=20, initial='text_unit', widget=forms.HiddenInput())
    unit_type = forms.ChoiceField(
        choices=[('sentence', 'sentence'), ('paragraph', 'paragraph')],
        required=True,
        initial='sentence',
        help_text='Text Unit type.')


class RunDocumentClassifierForm(BaseRunClassifierForm):
    header = 'Classify Documents using an existing Classifier.'
    target = forms.CharField(max_length=20, initial='document', widget=forms.HiddenInput())
    classifier = forms.ModelChoiceField(
        queryset=DocumentClassifier.objects.filter(is_active=True),
        widget=forms.widgets.Select(attrs={'class': 'chosen'}),
        required=True)


options_field_kwargs = dict(
    label='Advanced Options',
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


CLASSIFIER_NAME_CHOICES = (
    ('ExtraTreesClassifier', 'ExtraTreesClassifier'),
    ('LogisticRegressionCV', 'LogisticRegressionCV'),
    ('MultinomialNB', 'MultinomialNB'),
    ('RandomForestClassifier', 'RandomForestClassifier'),
    ('SVC', 'SVC'),
)


class BaseTrainClassifierForm(forms.Form):
    options = forms.BooleanField(**options_field_kwargs)
    svc_C = forms.FloatField(
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
    svc_gamma = forms.CharField(
        label='gamma',
        max_length=6,
        initial='scale',
        required=False,
        help_text="{'scale', 'auto'} or float, optional (default='scale')."
                  " Kernel coefficient for 'rbf', 'poly' and 'sigmoid'.")
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
    lrcv_Cs = forms.IntegerField(
        label='Cs',
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

    class_name = forms.ChoiceField(
        choices=[],
        required=True,
        help_text='Classifier class name')
    classifier_name = forms.CharField(
        max_length=100,
        required=True,
        help_text='Classifier name')
    use_tfidf = checkbox_field(
        "Use TF-IDF to normalize data")
    delete_classifier = checkbox_field(
        "Delete existing Classifiers of class name specified above.")
    project = forms.ModelChoiceField(
        queryset=Project.objects.order_by('-pk'),
        widget=forms.widgets.Select(attrs={'class': 'chosen'}),
        required=True,
        label='Restrict to project')
    classify_by = forms.MultipleChoiceField(
        widget=forms.SelectMultiple(attrs={'class': 'chosen'}),
        choices=[(i, i) for i in DocumentFeatures.source_fields],
        initial='term',
        required=True,
        help_text='Classify by terms, parties or other fields.')
    algorithm = forms.ChoiceField(
        choices=CLASSIFIER_NAME_CHOICES,
        required=True,
        initial='RandomForestClassifier',
        help_text='Classifier algorithm name.')
    metric_pos_label = forms.CharField(
        max_length=100,
        required=False,
        help_text='Positive label for "f1", "precision", "recall" accuracy metrics.')
    unit_type = forms.ChoiceField(
        choices=[('sentence', 'sentence'), ('paragraph', 'paragraph')],
        required=True,
        initial='sentence',
        help_text='Text Unit type.')
    field_order = ['project', 'unit_type', 'algorithm', 'use_tfidf', 'class_name',
                   'classify_by', 'classifier_name', 'metric_pos_label', 'delete_classifier']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['class_name'] = forms.ChoiceField(
            choices=[(class_name, class_name) for class_name in
                     set(self.classification_db_model.objects.values_list('class_name', flat=True))],
            required=True,
            help_text='Classification class name')

    def clean_svc_gamma(self):
        svc_gamma = self.cleaned_data['svc_gamma']
        try:
            svc_gamma = float(svc_gamma)
        except ValueError:
            pass
        return svc_gamma


class TrainTextUnitClassifierForm(BaseTrainClassifierForm):
    header = 'Train Text Unit Classifier.'
    classification_db_model = TextUnitClassification
    target = forms.CharField(max_length=20, initial='text_unit', widget=forms.HiddenInput())


class TrainDocumentClassifierForm(BaseTrainClassifierForm):
    header = 'Train Document Classifier.'
    classification_db_model = DocumentClassification
    target = forms.CharField(max_length=20, initial='document', widget=forms.HiddenInput())
    unit_type = forms.CharField(max_length=20, initial='sentence', widget=forms.HiddenInput())


class ClusterForm(forms.Form):
    header = 'Clustering Documents and/or Text Units by Terms, Entities or Parties.'
    do_cluster_documents = checkbox_field(
        "Cluster Documents", initial=True, input_class='max-one-of')
    do_cluster_text_units = checkbox_field(
        "Cluster Text Units", input_class='max-one-of')
    project = forms.ModelChoiceField(
        queryset=Project.objects.order_by('-pk'),
        widget=forms.widgets.Select(attrs={'class': 'chosen'}),
        required=True,
        label='Restrict to project')
    cluster_by = forms.MultipleChoiceField(
        widget=forms.SelectMultiple(attrs={'class': 'chosen'}),
        choices=[(i, i) for i in DocumentFeatures.source_fields],
        initial='term',
        required=True,
        help_text='Cluster by terms, parties or other fields.')
    using = forms.ChoiceField(
        label='Algorithm',
        choices=[('minibatchkmeans', 'MiniBatchKMeans'),
                 ('kmeans', 'KMeans'),
                 ('birch', 'Birch'),
                 ('dbscan', 'DBSCAN'),
                 # ('LabelSpreading', 'LabelSpreading')
                 ],
        required=True,
        initial='minidatchkmeans',
        help_text='Clustering algorithm model name.')
    n_clusters = forms.IntegerField(
        label='n_clusters',
        min_value=1,
        initial=3,
        required=True,
        help_text='Number of clusters.')
    name = forms.CharField(
        max_length=100,
        required=True)
    description = forms.CharField(
        max_length=200,
        required=False)
    options = forms.BooleanField(**options_field_kwargs)
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
    minibatchkmeans_batch_size = forms.IntegerField(
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
    # ls_documents_property = forms.Field()
    # ls_text_units_property = forms.Field()
    # ls_max_iter = forms.IntegerField(
    #     label='max_iter',
    #     min_value=1,
    #     initial=5,
    #     required=True,
    #     help_text='Maximum number of iterations allowed.')

    # delete_type = checkbox_field(
    #     'Delete existed Clusters of the "Cluster By" and "Algorithm" specified above',
    #     input_class='max-one-of')
    # delete = checkbox_field("Delete all existed Clusters", input_class='max-one-of')

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     if TextUnitProperty.objects.exists():
    #         choices = [(p, p) for p in sorted(
    #             set(TextUnitProperty.objects.values_list('key', flat=True)),
    #             key=lambda i: i.lower())]
    #         self.fields['ls_text_units_property'] = forms.ChoiceField(
    #             label='Text Unit Property Name',
    #             widget=forms.widgets.Select(attrs={'class': 'chosen'}),
    #             choices=choices,
    #             required=True,
    #             initial=choices[0][0])
    #     else:
    #         del self.fields['ls_text_units_property']
    #     if DocumentProperty.objects.exists():
    #         choices = [(p, p) for p in sorted(
    #             set(DocumentProperty.objects.values_list('key', flat=True)),
    #             key=lambda i: i.lower())]
    #         self.fields['ls_documents_property'] = forms.ChoiceField(
    #             label='Document Property Name',
    #             widget=forms.widgets.Select(attrs={'class': 'chosen'}),
    #             choices=choices,
    #             required=True,
    #             initial=choices[0][0])
    #     else:
    #         del self.fields['ls_documents_property']
    #     if not DocumentProperty.objects.exists() and not TextUnitProperty.objects.exists():
    #         self.fields['using'].choices = self.fields['using'].choices[:-1]

    def clean(self):
        cleaned_data = super().clean()
        do_cluster_documents = cleaned_data.get("do_cluster_documents")
        do_cluster_text_units = cleaned_data.get("do_cluster_text_units")
        if not any([do_cluster_documents, do_cluster_text_units]):
            self.add_error('do_cluster_documents', 'Please choose either Documents or Text Units')
            self.add_error('do_cluster_text_units', 'Please choose either Documents or Text Units')
