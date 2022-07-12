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


__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2022, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


import os.path
from io import BytesIO

import regex as re
from django import forms
from django.core.files.uploadedfile import TemporaryUploadedFile
from django.db.models import F
from django.contrib import admin
from django.conf import settings
from django.http import JsonResponse
from django.urls import path, reverse

from apps.analyze.models import (
    DocumentCluster, TextUnitCluster,
    SimilarityRun, DocumentSimilarity, TextUnitSimilarity, PartySimilarity,
    DocumentClassification, DocumentClassifier, DocumentClassifierSuggestion,
    TextUnitClassification, TextUnitClassifier, TextUnitClassifierSuggestion,
    DocumentVector, TextUnitVector, MLModel)
from apps.common.file_storage import get_file_storage
from apps.project.models import Project


file_storage = get_file_storage()


class DocumentClusterAdmin(admin.ModelAdmin):
    list_display = ('cluster_id', 'name', 'self_name', 'cluster_by', 'using')
    search_fields = ('name', 'self_name')


class TextUnitClusterAdmin(DocumentClusterAdmin):
    raw_id_fields = ('text_units',)


class SimilarityRunAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'feature_source', 'created_date', 'created_by')
    search_fields = ('name', 'feature_source')


class DocumentSimilarityAdmin(admin.ModelAdmin):
    list_display = ('document_a', 'document_b', 'similarity', 'run')
    search_fields = ('document_a__name', 'document_b__name')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.select_related('document_a', 'document_b', 'run') \
            .only('document_a__name', 'document_b__name', 'similarity', 'run')
        return qs


class PartySimilarityAdmin(admin.ModelAdmin):
    list_display = ('party_a', 'party_b', 'similarity', 'run')
    search_fields = ('party_a__name', 'party_b__name', 'run')


class TextUnitSimilarityAdmin(admin.ModelAdmin):
    list_display = ('similarity',
                    'document_a_name', 'text_unit_a_id',
                    'document_b_name', 'text_unit_b_id', 'run')
    search_fields = ('document_a_name', 'document_b_name',
                     'text_unit_a_id__exact', 'text_unit_b_id__exact')
    raw_id_fields = ('text_unit_a', 'text_unit_b')

    def document_a_name(self, obj):
        return obj.document_a_name

    def document_b_name(self, obj):
        return obj.document_b_name

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.annotate(document_a_name=F('text_unit_a__document__name'),
                         document_b_name=F('text_unit_b__document__name'))
        return qs.select_related('text_unit_a__document', 'text_unit_b__document', 'run').only(
            'similarity', 'document_a__name', 'text_unit_a_id',
            'document_b__name', 'text_unit_b_id', 'run')

    def get_search_fields(self, request):
        q = request.GET.get('q')
        if q and q.isdigit():
            return 'text_unit_a_id__exact', 'text_unit_b_id__exact'
        return 'document_a_name', 'document_b_name'


class DocumentClassificationAdmin(admin.ModelAdmin):
    list_display = ('document_id', 'document', 'class_name', 'class_value')
    search_fields = ('document__name', 'class_name')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.select_related('document') \
            .only('document_id', 'document__name', 'class_name', 'class_value')
        return qs


class DocumentClassifierAdmin(admin.ModelAdmin):
    list_display = ('name', 'version', 'class_name')
    search_fields = ('name', 'version', 'class_name')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.only('name', 'version', 'class_name')
        return qs


class DocumentClassifierSuggestionAdmin(admin.ModelAdmin):
    list_display = ('classifier_id', 'document_id', 'classifier_run', 'classifier_confidence', 'class_name')
    search_fields = ('classifier__name', 'classifier__version', 'classifier_run', 'classifier_id',
                     'classifier_confidence', 'class_name')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.select_related('classifier', 'document') \
            .only('classifier_id', 'classifier__name', 'document_id',
                  'classifier_run', 'classifier_confidence', 'class_name')
        return qs


class TextUnitClassificationAdmin(admin.ModelAdmin):
    list_display = ('text_unit_id', 'class_name', 'class_value')
    search_fields = ('text_unit__unit_type', 'class_name')
    raw_id_fields = ('text_unit',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.select_related('text_unit') \
            .only('text_unit_id', 'class_name', 'class_value')
        return qs


class TextUnitClassifierAdmin(admin.ModelAdmin):
    list_display = ('name', 'version', 'class_name')
    search_fields = ('name', 'version', 'class_name')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.only('name', 'version', 'class_name')
        return qs


class TextUnitClassifierSuggestionAdmin(admin.ModelAdmin):
    list_display = ('classifier_id', 'text_unit_id', 'classifier_run', 'classifier_confidence', 'class_name')
    search_fields = ('classifier__name', 'classifier__version', 'classifier_run', 'classifier_id',
                     'classifier_confidence', 'class_name')
    raw_id_fields = ('text_unit',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.select_related('classifier', 'text_unit') \
            .only('classifier_id', 'classifier__name', 'text_unit_id',
                  'classifier_run', 'classifier_confidence', 'class_name')
        return qs


class DocumentVectorAdmin(admin.ModelAdmin):
    list_display = ('pk', 'vector_name', 'transformer_name', 'document', 'project', 'timestamp')
    search_fields = ('vector_name', 'transformer__name', 'document__name')

    def transformer_name(self, obj):
        return obj.transformer.name
    transformer_name.short_description = 'Transformer'
    transformer_name.admin_order_field = 'transformer__name'

    def project(self, obj):
        return obj.document.project.name
    project.short_description = 'Project'
    project.admin_order_field = 'document__project__name'

    def get_queryset(self, request):
        return super().get_queryset(request) \
            .select_related('transformer', 'document', 'document__project') \
            .only('pk', 'vector_name', 'transformer__name', 'document__name',
                  'document__project__name', 'timestamp') \
            .order_by('document_id', 'timestamp')


class TextUnitVectorAdmin(admin.ModelAdmin):
    list_display = ('pk', 'vector_name', 'transformer_name', 'text_unit_id', 'document', 'project', 'timestamp')
    search_fields = ('vector_name', 'text_unit_id', 'text_unit__document__name', 'text_unit__document__project__name')
    raw_id_fields = ('text_unit',)

    def transformer_name(self, obj):
        return obj.transformer.name
    transformer_name.short_description = 'Transformer'
    transformer_name.admin_order_field = 'transformer__name'

    def document(self, obj):
        return obj.text_unit.document.name
    document.short_description = 'Document'
    document.admin_order_field = 'text_unit__document__name'

    def project(self, obj):
        return obj.text_unit.project.name
    project.short_description = 'Project'
    project.admin_order_field = 'text_unit__project__name'

    def get_queryset(self, request):
        return super().get_queryset(request)\
            .select_related('transformer', 'text_unit__document', 'text_unit__project') \
            .only('pk', 'vector_name', 'transformer__name', 'text_unit_id',
                  'text_unit__document__name', 'text_unit__project__name', 'timestamp') \
            .order_by('text_unit_id', 'timestamp')


class MLModelChangeForm(forms.ModelForm):
    class Meta:
        model = MLModel
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['project'].queryset = Project.objects.order_by('-pk')

    def clean(self):
        pass
        # something = self.cleaned_data.get('schedule')
        # raise forms.ValidationError('')


class MLModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'version', 'target_entity', 'apply_to', 'language', 'project', 'default')
    search_fields = ('name', 'version', 'target_entity', 'apply_to', 'language', 'project')

    form = MLModelChangeForm
    change_form_template = 'admin/analyze/mlmodel/change_form.html'

    actions = ['delete_with_files']

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['codebase_version'].initial = settings.VERSION_NUMBER
        form.base_fields['user_modified'].initial = True
        return form

    def delete_with_files(self, request, queryset):
        # delete the model objects and stored files
        objects = list(queryset)
        for model in objects:  # type: MLModel
            try:
                content = file_storage.check_path(model.model_path)
                if not content['exists']:
                    continue
                # delete the folder (if content['is_folder']) and all the files within
                # or just the file
                file_storage.delete_file(model.model_path)
            except Exception as e:
                raise Exception(f'There were error while deleting path {model.model_path}: {e}')
            model.delete()

    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        context['check_path_exists_url'] = reverse('admin:check_path_exists_view')
        context['file_upload_url'] = reverse('admin:file_upload_view')
        context['create_folder_url'] = reverse('admin:create_folder_view')
        return super().render_change_form(request, context, add, change, form_url, obj)

    def file_upload_view(self, request, **kwargs):
        file: TemporaryUploadedFile = request.FILES.get('model-file')
        if not file:
            return JsonResponse({'success': True})
        model_name = request.POST.get('model-name')
        model_path = request.POST.get('model-path')

        if not model_name or not model_path:
            errors = ['model name is not provided' if not model_name else '',
                      'target path is not provided' if not model_path else '']
            error_str = ', '.join([e for e in errors if e])
            return JsonResponse({'success': False,
                                 'errors': error_str})

        # try uploading the file into the WebDav folder
        target_file_name = file.name
        model_folder = model_path
        content = file_storage.check_path(model_path)

        # user specified the full path to the file
        if not content['is_folder']:
            target_file_name = os.path.basename(model_path)
            model_folder = os.path.dirname(model_path)

        target_path = os.path.join(model_folder, target_file_name)
        content = file_storage.check_path(target_path)
        if content['exists']:
            # delete the file prior to uploading
            try:
                file_storage.delete_file(target_path)
            except Exception as e:
                print(e)
                return JsonResponse({'success': False,
                                     'errors': "Can't delete the existing file"})

        try:
            byte_data = file.read()
            file_storage.write_file(target_path, byte_data, file.size)
        except Exception as e:
            print(e)
            return JsonResponse({'success': False,
                                 'errors': "Can't upload the file"})

        # save the model - user updated flag + current CS version
        model: MLModel = MLModel.objects.filter(name=model_name).first()
        if model:
            model.user_modified = True
            model.codebase_version = settings.VERSION_NUMBER
            model.save()

        return JsonResponse({'success': True})

    def check_path_exists_view(self, request, **kwargs):
        webdav_path = request.POST.get('webdav_path')
        # context: { 'exists': True, 'is_folder': True, 'not_empty': False }
        content = file_storage.check_path(webdav_path)
        return JsonResponse(content)

    def create_folder_view(self, request, **kwargs):
        webdav_path = request.POST.get('webdav_path').strip()
        if not webdav_path:
            return JsonResponse({'success': False, 'errors': ['Folder is empty string']})
        folders = [f.strip() for f in webdav_path.strip('/').split('/')]
        if not all(folders):
            return JsonResponse({'success': False, 'errors': ['There are empty path parts between "/" symbols']})
        for i, folder in enumerate(folders):
            if not file_storage.RE_VALID_SUBFOLDER.fullmatch(folder):
                normalized_folder = file_storage.normalize_folder_name(folder)
                if not normalized_folder:
                    return JsonResponse({'success': False,
                                         'errors': [f'Path part "{folder}" is not a valid folder name']})
                folders[i] = normalized_folder
                norm_path = os.path.join(*folders)
                return JsonResponse({'success': False,
                                     'errors': [f'Path part "{folder}" is not a valid folder name. \n' +
                                                f'Suggested folder name is "{norm_path}"']})

        for i in range(len(folders)):
            sub_path = '/'.join(folders[:i + 1])
            content = file_storage.check_path(sub_path)
            if content['exists'] and not content['is_folder']:
                return JsonResponse({'success': False,
                                     'errors': [f'Path part "{sub_path}" is an existing file']})

        for i in range(len(folders)):
            sub_path = '/'.join(folders[:i + 1])
            content = file_storage.check_path(sub_path)
            if content['exists']:
                continue
            try:
                file_storage.mkdir(sub_path)
            except Exception as e:
                return JsonResponse({'success': False,
                                     'errors': [f'Error while creating folder "{sub_path}": {e}']})
        return JsonResponse({'success': True, 'errors': []})

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('check_path_exists_view/',
                 self.check_path_exists_view,
                 name='check_path_exists_view'),
            path('create_folder_view/',
                 self.create_folder_view,
                 name='create_folder_view'),
            path('file_upload_view/',
                 self.file_upload_view,
                 name='file_upload_view')]
        return my_urls + urls


admin.site.register(DocumentCluster, DocumentClusterAdmin)
admin.site.register(TextUnitCluster, TextUnitClusterAdmin)

admin.site.register(SimilarityRun, SimilarityRunAdmin)
admin.site.register(DocumentSimilarity, DocumentSimilarityAdmin)
admin.site.register(TextUnitSimilarity, TextUnitSimilarityAdmin)
admin.site.register(PartySimilarity, PartySimilarityAdmin)

admin.site.register(DocumentClassification, DocumentClassificationAdmin)
admin.site.register(DocumentClassifier, DocumentClassifierAdmin)
admin.site.register(DocumentClassifierSuggestion, DocumentClassifierSuggestionAdmin)
admin.site.register(TextUnitClassification, TextUnitClassificationAdmin)
admin.site.register(TextUnitClassifier, TextUnitClassifierAdmin)
admin.site.register(TextUnitClassifierSuggestion, TextUnitClassifierSuggestionAdmin)

admin.site.register(DocumentVector, DocumentVectorAdmin)
admin.site.register(TextUnitVector, TextUnitVectorAdmin)
admin.site.register(MLModel, MLModelAdmin)
