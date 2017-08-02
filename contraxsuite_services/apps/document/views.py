# -*- coding: utf-8 -*-

# Future imports
from __future__ import absolute_import, unicode_literals

# Standard imports
import datetime
import os
import urllib
import pandas as pd

# Django imports
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.db.models import Count, F, Prefetch
from django.shortcuts import get_object_or_404, redirect
from django.shortcuts import render
from django.views.generic import DetailView

# EL imports
from haystack.query import SearchQuerySet

# Project imports
from apps.analyze.models import (
    TextUnitClassification, TextUnitClassifierSuggestion)
from apps.document.models import (
    Document, DocumentProperty, DocumentRelation, DocumentNote,
    TextUnit, TextUnitProperty, TextUnitNote, TextUnitTag)
from apps.extract.models import (
    LegalTerm, LegalTermUsage, GeoAlias, GeoEntity, GeoRelation,
    GeoAliasUsage, GeoEntityUsage, Party, PartyUsage)
from apps.common.mixins import (
    CustomUpdateView, CustomCreateView, CustomDeleteView,
    JqPaginatedListView, PermissionRequiredMixin, SubmitView, TypeaheadView)
from apps.project.models import TaskQueue
from apps.project.views import ProjectListView, TaskQueueListView
from apps.task.views import TaskListView
from apps.users.models import User

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2017, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.0/LICENSE.pdf"
__version__ = "1.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@lexpredict.com"


def search(request):
    """
    Search dispatcher.
    :param request:
    :return:
    """
    # Check for term redirect
    if request.GET.get("elastic_search", "").strip() or \
            request.GET.get("text_search", "").strip():
        view_name = "document:text-unit-list"

    # Check for term redirect
    elif request.GET.get("term_search", "").strip():
        view_name = "extract:legal-term-usage-list"

    # Check for term redirect
    elif request.GET.get("entity_search", "").strip():
        view_name = "extract:geo-entity-usage-list"

    # Redirect others to Document List page
    else:
        view_name = "document:document-list"

    return redirect('{}?{}'.format(reverse(view_name), request.GET.urlencode()))


class DocumentListView(JqPaginatedListView):
    """DocumentListView

    CBV for list of Document records.
    """
    model = Document
    json_fields = ['name', 'document_type', 'description',
                   'properties', 'relations', 'text_units']
    limit_reviewers_qs_by_field = ""
    field_types = dict(
        properties=int,
        relations=int,
        text_units=int
    )

    def get_queryset(self):
        qs = super().get_queryset()

        description_search = self.request.GET.get("description_search")
        if description_search:
            qs = qs.filter(description__icontains=description_search)

        name_search = self.request.GET.get("name_search")
        if name_search:
            qs = qs.filter(name__icontains=name_search)

        if 'party_pk' in self.request.GET:
            qs = qs.filter(textunit__partyusage__party__pk=self.request.GET['party_pk'])

        # Populate with child counts
        qs = qs.annotate(
            properties=Count('documentproperty', distinct=True),
            text_units=F('paragraphs') + F('sentences'),
            num_relation_a=Count('document_a_set', distinct=True),
            num_relation_b=Count('document_b_set', distinct=True),
        ).annotate(relations=F('num_relation_a') + F('num_relation_b'))
        return qs

    def get_json_data(self, **kwargs):
        data = super().get_json_data()
        if "party_pk" in self.request.GET:
            tu_list_view = TextUnitListView(request=self.request)
            tu_data = tu_list_view.get_json_data()['data']
        for item in data['data']:
            item['url'] = reverse('document:document-detail', args=[item['pk']])
            if "party_pk" in self.request.GET:
                item['text_unit_data'] = [i for i in tu_data
                                          if i['document__pk'] == item['pk']]
        return data

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data()
        params = dict(urllib.parse.parse_qsl(self.request.GET.urlencode()))
        ctx.update(params)
        return ctx


class DocumentPropertyCreateView(CustomCreateView):
    """DocumentListView

    CBV for list of Document records.
    """
    model = DocumentProperty
    fields = ('document', 'key', 'value')

    def has_permission(self):
        if self.kwargs.get('pk'):
            document = get_object_or_404(Document, pk=self.kwargs['pk'])
            return self.request.user.can_view_document(document)
        return True

    def get_initial(self):
        initial = super().get_initial()
        if not self.object and self.kwargs.get('pk'):
            initial['document'] = Document.objects.get(pk=self.kwargs['pk'])
        return initial

    def get_success_url(self):
        return self.request.POST.get('next') or reverse('document:document-property-list')


class DocumentPropertyUpdateView(DocumentPropertyCreateView, CustomUpdateView):

    def has_permission(self):
        document = self.get_object().document
        return self.request.user.can_view_document(document)


class DocumentPropertyListView(JqPaginatedListView):
    model = DocumentProperty
    limit_reviewers_qs_by_field = 'document'
    json_fields = ['key', 'value', 'document__pk', 'document__name',
                   'document__document_type', 'document__description']

    def get_queryset(self):
        qs = super().get_queryset()

        if "document_pk" in self.request.GET:
            qs = qs.filter(document__pk=self.request.GET['document_pk'])

        key_search = self.request.GET.get('key_search')
        if key_search:
            qs = qs.filter(key__icontains=key_search)
        qs = qs.select_related('document')
        return qs

    def get_json_data(self, **kwargs):
        data = super().get_json_data()
        for item in data['data']:
            item['url'] = reverse('document:document-detail', args=[item['document__pk']])
            item['edit_url'] = reverse('document:document-property-update', args=[item['pk']])
            item['delete_url'] = reverse('document:document-property-delete', args=[item['pk']])
        return data

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['key_search'] = self.request.GET.get('key_search')
        return ctx


class DocumentPropertyDeleteView(CustomDeleteView):
    model = DocumentProperty
    document = None

    def get_success_url(self):
        return self.request.POST.get('next') or reverse('document:document-detail',
                                                        args=[self.document.pk])

    def has_permission(self):
        self.document = self.get_object().document
        return self.request.user.can_view_document(self.document)


class DocumentRelationListView(JqPaginatedListView):
    model = DocumentRelation
    json_fields = ['relation_type',
                   'document_a__pk', 'document_a__name',
                   'document_a__document_type', 'document_a__description',
                   'document_b__pk', 'document_b__name',
                   'document_b__document_type', 'document_b__description']
    limit_reviewers_qs_by_field = ['document_a', 'document_b']

    def get_json_data(self, **kwargs):
        data = super().get_json_data()
        for item in data['data']:
            item['url_a'] = reverse('document:document-detail', args=[item['document_a__pk']])
            item['url_b'] = reverse('document:document-detail', args=[item['document_b__pk']])
        return data

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.select_related('document_a', 'document_b')
        return qs


class DocumentDetailView(PermissionRequiredMixin, DetailView):
    model = Document
    raise_exception = True

    def has_permission(self):
        return self.request.user.can_view_document(self.get_object())

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        document = self.object

        # Fetch related lists
        party_usage_list = PartyUsage.objects\
            .filter(text_unit__document=document)\
            .values("party__name")\
            .annotate(count=Count("id")).order_by("-count")
        party_list = party_usage_list.values_list('party__name', flat=True)

        task_queue_list = document.taskqueue_set.all()
        extra_task_queue_list = TaskQueue.objects.exclude(
            id__in=task_queue_list.values_list('pk', flat=True))

        ctx.update({"document": document,
                    "party_list": list(party_list),
                    "extra_task_queue_list": extra_task_queue_list,
                    "highlight": self.request.GET.get("highlight", "")})
        return ctx


class DocumentSourceView(DocumentDetailView):
    template_name = "document/document_source.html"

    def get_context_data(self, **kwargs):
        # TODO: detect protocol, don't hardcode
        rel_url = os.path.join('/media', self.object.description.lstrip('/'))
        attachment = dict(
            name=self.object.name,
            path='https://{host}{rel_url}'.format(
                host=Site.objects.get_current().domain, rel_url=rel_url),
            extension=os.path.splitext(self.object.description)[1][1:].lower()
        )
        ctx = {'attachment': attachment}
        return ctx


class DocumentNoteListView(JqPaginatedListView):
    model = DocumentNote
    json_fields = ['note', 'timestamp', 'document__pk',
                   'document__name', 'document__document_type',
                   'document__description']
    limit_reviewers_qs_by_field = 'document'
    ordering = ['-timestamp']

    def get_json_data(self, **kwargs):
        data = super().get_json_data()
        history = list(
            DocumentNote.history
            .filter(document_id__in=list(self.get_queryset()
                                         .values_list('document__pk', flat=True)))
            .values('id', 'document_id', 'history_date', 'history_user__username', 'note'))

        for item in data['data']:
            item['url'] = reverse('document:document-detail', args=[item['document__pk']])
            item['delete_url'] = reverse('document:document-note-delete', args=[item['pk']])
            item_history = [i for i in history if i['id'] == item['pk']]
            if item_history:
                item['history'] = item_history
                item['user'] = sorted(item_history,
                                      key=lambda i: i['history_date'])[-1]['history_user__username']
        return data

    def get_queryset(self):
        qs = super().get_queryset()
        if "document_pk" in self.request.GET:
            qs = qs.filter(document__pk=self.request.GET['document_pk'])
        return qs


class DocumentEnhancedView(DocumentDetailView):
    template_name = "document/document_enhanced_view.html"

    def get_context_data(self, **kwargs):
        document = self.object
        paragraph_list = document.textunit_set \
            .filter(unit_type="paragraph") \
            .order_by("id")\
            .prefetch_related(
                Prefetch(
                    'legaltermusage_set',
                    queryset=LegalTermUsage.objects.order_by('term__term').select_related('term'),
                    to_attr='ltu'))
        ctx = {"document": document,
               "party_list": list(PartyUsage.objects.filter(
                   text_unit__document=document).values_list('party__name', flat=True)),
               "highlight": self.request.GET.get("highlight", ""),
               "paragraph_list": paragraph_list}
        return ctx


class TextUnitDetailView(PermissionRequiredMixin, DetailView):
    """
    Used DetailView instead of CustomDetailView to overwrite
    admin permissions
    """
    model = TextUnit
    template_name = "document/text_unit_detail.html"
    raise_exception = True

    def has_permission(self):
        return self.request.user.can_view_document(self.get_object().document)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        text_unit = self.object
        document = text_unit.document

        # Find identical text unit matches
        identical_text_unit_list = TextUnit.objects.filter(text_hash=text_unit.text_hash) \
            .select_related('document')

        ctx.update({"document": document,
                    "highlight": self.request.GET.get("highlight", ""),
                    "text_unit": text_unit,
                    "identical_text_unit_list": identical_text_unit_list})
        return ctx


class TextUnitListView(JqPaginatedListView):
    model = TextUnit
    json_fields = ['unit_type', 'language', 'text', 'text_hash',
                   'document__pk', 'document__name',
                   'document__document_type', 'document__description']
    limit_reviewers_qs_by_field = 'document'

    def get_queryset(self):
        qs = super().get_queryset()

        if "elastic_search" in self.request.GET or "text_search" in self.request.GET:
            elastic_search = self.request.GET.get("elastic_search")

            # use haystack
            if elastic_search is not None:
                qs = SearchQuerySet()
                text_search = elastic_search
            # else plain django
            else:
                text_search = self.request.GET.get("text_search")

            # TODO: check effectiveness using with haystack (_and, _or, _not)
            qs = self.filter(text_search, qs, _or_lookup='text__icontains')

            # if haystack transform sqs into qs
            if elastic_search is not None:
                qs = qs.models(TextUnit)
                pks = [search_obj._pk for search_obj in qs]
                qs = TextUnit.objects.filter(pk__in=pks)
                # TODO: use? .distinct('text_hash')

        if "document_pk" in self.request.GET:
            # Document Detail view
            qs = qs.filter(document__pk=self.request.GET['document_pk'])
        elif "party_pk" in self.request.GET:
            qs = qs.filter(partyusage__party__pk=self.request.GET['party_pk'])
        elif "text_unit_hash" in self.request.GET:
            # Text Unit Detail identical text units tab
            qs = qs.filter(text_hash=self.request.GET['text_unit_hash'])\
                .exclude(pk=self.request.GET['text_unit_pk'])
        else:
            qs = qs.filter(unit_type='paragraph')
        return qs

    def get_json_data(self, **kwargs):
        data = super().get_json_data()
        for item in data['data']:
            item['url'] = reverse('document:document-detail', args=[item['document__pk']])
            item['detail_url'] = reverse('document:text-unit-detail', args=[item['pk']])
        return data

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['elastic_search'] = self.request.GET.get("elastic_search", "")
        ctx['text_search'] = self.request.GET.get("text_search", "")
        ctx['is_text_unit_list_page'] = True
        return ctx


class TextUnitPropertyListView(JqPaginatedListView):
    model = TextUnitProperty
    limit_reviewers_qs_by_field = 'text_unit__document'
    json_fields = ['key', 'value',
                   'text_unit__document__pk', 'text_unit__document__name',
                   'text_unit__document__document_type', 'text_unit__document__description',
                   'text_unit__unit_type', 'text_unit__language',
                   'text_unit__pk']

    def get_queryset(self):
        qs = super().get_queryset()

        if "text_unit_pk" in self.request.GET:
            qs = qs.filter(text_unit__pk=self.request.GET['text_unit_pk'])

        key_search = self.request.GET.get('key_search')
        if key_search:
            qs = qs.filter(key__icontains=key_search)
        return qs

    def get_json_data(self, **kwargs):
        data = super().get_json_data()
        for item in data['data']:
            item['url'] = reverse('document:document-detail',
                                  args=[item['text_unit__document__pk']])
            item['text_unit_url'] = reverse('document:text-unit-detail',
                                            args=[item['text_unit__pk']])
            item['delete_url'] = reverse('document:text-unit-property-delete', args=[item['pk']])
        return data

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['key_search'] = self.request.GET.get('key_search')
        return ctx


class TextUnitPropertyDeleteView(CustomDeleteView):
    model = TextUnitProperty

    def get_success_url(self):
        return self.request.POST.get('next') or reverse('document:tex-unit-detail',
                                                        args=[self.text_unit.pk])

    def has_permission(self):
        document = self.get_object().text_unit.document
        return self.request.user.can_view_document(document)


class TextUnitNoteListView(JqPaginatedListView):
    model = TextUnitNote
    json_fields = ['note', 'timestamp', 'text_unit__document__pk',
                   'text_unit__document__name', 'text_unit__document__document_type',
                   'text_unit__document__description', 'text_unit__pk',
                   'text_unit__unit_type', 'text_unit__language']
    limit_reviewers_qs_by_field = 'text_unit__document'

    def get_json_data(self, **kwargs):
        data = super().get_json_data()
        history = list(
            TextUnitNote.history
            .filter(text_unit__document_id__in=list(
                self.get_queryset().values_list('text_unit__document__pk', flat=True)))
            .values('id', 'text_unit_id', 'history_date', 'history_user__username', 'note'))

        for item in data['data']:
            item['url'] = reverse('document:document-detail',
                                  args=[item['text_unit__document__pk']])
            item['detail_url'] = reverse('document:text-unit-detail', args=[item['text_unit__pk']])
            item['delete_url'] = reverse('document:text-unit-note-delete', args=[item['pk']])
            item_history = [i for i in history if i['id'] == item['pk']]
            if item_history:
                item['history'] = item_history
                item['user'] = sorted(item_history,
                                      key=lambda i: i['history_date'])[-1]['history_user__username']
        return data

    def get_queryset(self):
        qs = super().get_queryset()
        if "text_unit_pk" in self.request.GET:
            qs = qs.filter(text_unit__pk=self.request.GET['text_unit_pk'])
        return qs


class TextUnitNoteDeleteView(CustomDeleteView):
    model = TextUnitNote

    def get_success_url(self):
        return reverse('document:text-unit-detail', args=[self.object.text_unit.pk])

    def has_permission(self):
        document = self.get_object().text_unit.document
        return self.request.user.can_view_document(document)


class DocumentNoteDeleteView(CustomDeleteView):
    model = DocumentNote

    def get_success_url(self):
        return self.request.POST.get('next') or reverse('document:document-detail',
                                                        args=[self.object.document.pk])

    def has_permission(self):
        document = self.get_object().document
        return self.request.user.can_view_document(document)


class TextUnitTagListView(JqPaginatedListView):
    model = TextUnitTag
    json_fields = ['tag', 'timestamp', 'user__username', 'text_unit__document__pk',
                   'text_unit__document__name', 'text_unit__document__document_type',
                   'text_unit__document__description', 'text_unit__pk',
                   'text_unit__unit_type', 'text_unit__language']
    limit_reviewers_qs_by_field = 'text_unit__document'

    def get_json_data(self, **kwargs):
        data = super().get_json_data()
        for item in data['data']:
            item['url'] = reverse('document:document-detail',
                                  args=[item['text_unit__document__pk']])
            item['detail_url'] = reverse('document:text-unit-detail', args=[item['text_unit__pk']])
            item['delete_url'] = reverse('document:text-unit-tag-delete', args=[item['pk']])
        return data

    def get_queryset(self):
        qs = super().get_queryset()
        tag_search = self.request.GET.get('tag_search')
        if tag_search:
            qs = qs.filter(tag=tag_search)
        text_unit_id = self.request.GET.get('text_unit_id')
        if text_unit_id:
            qs = qs.filter(text_unit__id=text_unit_id)
        qs = qs.select_related('text_unit', 'text_unit__document')
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["tag_search"] = self.request.GET.get('tag_search')
        return ctx


class TextUnitTagDeleteView(CustomDeleteView):
    model = TextUnitTag

    def get_success_url(self):
        return self.request.POST.get('next') or reverse('document:text-unit-tag-list')

    def has_permission(self):
        document = self.get_object().text_unit.document
        return self.request.user.can_view_document(document)


class TypeaheadDocumentDescription(TypeaheadView):
    model = Document
    search_field = 'description'
    limit_reviewers_qs_by_field = ''


class TypeaheadDocumentName(TypeaheadDocumentDescription):
    search_field = 'name'


class TypeaheadTextUnitTag(TypeaheadView):
    model = TextUnitTag
    search_field = 'tag'
    limit_reviewers_qs_by_field = 'text_unit__document'


class TypeaheadDocumentPropertyKey(TypeaheadView):
    model = DocumentProperty
    search_field = 'key'
    limit_reviewers_qs_by_field = 'document'


class SubmitNoteView(SubmitView):
    notes_map = dict(
        document=dict(
            owner_model=Document,
            note_model=DocumentNote,
            owner_field='document'
        ),
        text_unit=dict(
            owner_model=TextUnit,
            note_model=TextUnitNote,
            owner_field='text_unit'
        )
    )
    success_message = 'Note was successfully saved'

    @staticmethod
    def get_owner(request, owner_model=TextUnit):
        try:
            owner = owner_model.objects.get(id=request.POST["owner_id"])
            document = owner if owner_model == Document else owner.document
            if not request.user.can_view_document(document):
                # TODO: specify error message
                return None
        except owner_model.DoesNotExist:
            return None
        return owner

    def process(self, request):
        note_prop = self.notes_map[request.POST.get("owner_name", "text_unit")]
        owner = self.get_owner(request, note_prop['owner_model'])
        note_model = note_prop['note_model']
        if owner is None:
            return self.failure()
        if request.POST.get("note_id"):
            try:
                obj = note_model.objects.get(pk=request.POST["note_id"])
            except note_model.DoesNotExist:
                return self.failure()
        else:
            obj = note_model()
            setattr(obj, note_prop['owner_field'], owner)
        obj.note = request.POST["note"]
        obj.save()
        return self.success()


class SubmitTextUnitTagView(SubmitView):
    owner = None

    def dispatch(self, request, *args, **kwargs):
        self.owner = self.get_owner(request)
        return super().dispatch(request, *args, **kwargs)

    def get_success_message(self):
        return "Successfully added tag /%s/ for %s" % (
            self.request.POST["tag"],
            str(self.owner))

    @staticmethod
    def get_owner(request):
        try:
            text_unit = TextUnit.objects.get(id=request.POST["text_unit_id"])
            if not request.user.can_view_document(text_unit.document):
                    # TODO: specify error message
                return None
        except TextUnit.DoesNotExist:
            return None
        return text_unit

    def process(self, request):
        if self.request.POST.get('tag_pk'):
            obj, created = TextUnitTag.objects.update_or_create(
                pk=self.request.POST['tag_pk'],
                defaults=dict(
                    text_unit=self.owner,
                    tag=request.POST['tag'],
                    user=request.user,
                    timestamp=datetime.datetime.now(),
                )
            )
        else:
            obj = TextUnitTag.objects.create(
                text_unit=self.owner,
                tag=request.POST['tag'],
                user=request.user,
                timestamp=datetime.datetime.now()
            )
            created = True
        action = 'created' if created else 'updated'
        return {'message': 'Text Unit Tag %s was successfully %s' % (str(obj), action),
                'status': 'success'}


class SubmitTextUnitPropertyView(SubmitTextUnitTagView):

    def get_success_message(self):
        return "Successfully added property for %s" % str(self.owner)

    def process(self, request):
        defaults = dict(
            text_unit=self.owner,
            key=request.POST['key'],
            value=request.POST['value']
        )
        if self.request.POST.get('property_pk'):
            _, created = TextUnitProperty.objects.update_or_create(
                pk=self.request.POST['property_pk'],
                defaults=defaults)
        else:
            TextUnitProperty.objects.create(**defaults)
            created = True
        action = 'created' if created else 'updated'
        return {'message': 'Text Unit Property was successfully %s' % action,
                'status': 'success'}


def view_stats(request):
    """
    Display overall statistics.
    :param request:
    :return:
    """
    admin_task_df = pd.DataFrame(TaskListView(request=request).get_json_data()['data'])
    admin_task_total_count = admin_task_df.shape[0]
    admin_task_by_status_count = dict(admin_task_df.groupby(['status']).size())\
        if not admin_task_df.empty else 0

    project_df = pd.DataFrame(ProjectListView(request=request).get_json_data()['data'])
    project_df['completed'] = project_df['completed'].astype(int)
    project_total_count = project_df.shape[0]
    project_df_sum = project_df.sum()
    project_completed_count = project_df_sum.completed
    project_completed_weight = round(project_completed_count / project_total_count * 100, 1)
    project_progress_avg = round(project_df.mean().progress, 1)
    project_documents_total_count = project_df_sum.total_documents_count
    project_documents_unique_count = Document.objects.filter(taskqueue__project__isnull=False)\
        .distinct().count()

    task_queue_df = pd.DataFrame(TaskQueueListView(request=request).get_json_data()['data'])
    task_queue_df['completed'] = task_queue_df['completed'].astype(int)
    task_queue_total_count = task_queue_df.shape[0]
    task_queue_df_sum = task_queue_df.sum()
    task_queue_completed_count = task_queue_df_sum.completed
    task_queue_completed_weight = round(
        task_queue_completed_count / task_queue_total_count * 100, 1)
    task_queue_progress_avg = round(task_queue_df.mean().progress, 1)
    task_queue_documents_total_count = task_queue_df_sum.total_documents_count
    task_queue_documents_unique_count = Document.objects.filter(taskqueue__isnull=False)\
        .distinct().count()
    task_queue_reviewers_unique_count = User.objects.filter(taskqueue__isnull=False)\
        .distinct().count()

    geo_entity_count = GeoEntity.objects.count()
    geo_alias_count = GeoAlias.objects.count()
    geo_relation_count = GeoRelation.objects.count()

    if request.user.is_reviewer:
        document_count = Document.objects.filter(
            taskqueue__reviewers=request.user).count()
        document_property_count = DocumentProperty.objects.filter(
            document__taskqueue__reviewers=request.user).count()
        document_note_count = DocumentNote.objects.filter(
            document___taskqueue__reviewers=request.user).count()
        document_relation_count = DocumentRelation.objects.filter(
            document_a__taskqueue__reviewers=request.user,
            document_b__taskqueue__reviewers=request.user).count()
        text_unit_count = TextUnit.objects.filter(
            document__taskqueue__reviewers=request.user).count()
        text_unit_tag_count = TextUnitTag.objects.filter(
            text_unit__document__taskqueue__reviewers=request.user).count()
        text_unit_property_count = TextUnitProperty.objects.filter(
            text_unit__document__taskqueue__reviewers=request.user).count()
        text_unit_classification_count = TextUnitClassification.objects.filter(
            text_unit__document__taskqueue__reviewers=request.user).count()
        text_unit_classification_suggestion_count = TextUnitClassifierSuggestion.objects.filter(
            text_unit__document__taskqueue__reviewers=request.user).count()
        tuc_suggestion_type_count = \
            TextUnitClassifierSuggestion.objects \
            .filter(text_unit__document__taskqueue__reviewers=request.user)\
            .distinct('class_name').count()
        text_unit_note_count = TextUnitNote.objects.filter(
            text_unit__document__taskqueue__reviewers=request.user).count()
        legal_term_count = LegalTerm.objects.count()
        legal_term_usage_count = LegalTermUsage.objects.count()
        geo_entity_usage_count = GeoEntityUsage.objects.filter(
            text_unit__document__taskqueue__reviewers=request.user).count()
        geo_alias_usage_count = GeoAliasUsage.objects.filter(
            text_unit__document__taskqueue__reviewers=request.user).count()
        party_count = Party.objects.count()
        party_usage_count = PartyUsage.objects.filter(
            text_unit__document__taskqueue__reviewers=request.user).count()

    else:
        document_count = Document.objects.count()
        document_property_count = DocumentProperty.objects.count()
        document_note_count = DocumentNote.objects.count()
        document_relation_count = DocumentRelation.objects.count()
        text_unit_count = TextUnit.objects.count()
        text_unit_tag_count = TextUnitTag.objects.count()
        text_unit_property_count = TextUnitProperty.objects.count()
        text_unit_classification_count = TextUnitClassification.objects.count()
        text_unit_classification_suggestion_count = TextUnitClassifierSuggestion.objects.count()
        tuc_suggestion_type_count = TextUnitClassifierSuggestion.objects.distinct(
            'class_name').count()
        text_unit_note_count = TextUnitNote.objects.count()
        legal_term_count = LegalTerm.objects.count()
        legal_term_usage_count = LegalTermUsage.objects.count()
        geo_entity_usage_count = GeoEntityUsage.objects.count()
        geo_alias_usage_count = GeoAliasUsage.objects.count()
        party_count = Party.objects.count()
        party_usage_count = PartyUsage.objects.count()

    context = {
        "document_count": document_count,
        "document_property_count": document_property_count,
        "document_note_count": document_note_count,
        "document_relation_count": document_relation_count,
        "text_unit_count": text_unit_count,
        "text_unit_tag_count": text_unit_tag_count,
        "text_unit_property_count": text_unit_property_count,
        "text_unit_classification_count": text_unit_classification_count,
        "text_unit_classification_suggestion_count": text_unit_classification_suggestion_count,
        "text_unit_classification_suggestion_type_count": tuc_suggestion_type_count,
        "text_unit_note_count": text_unit_note_count,
        "geo_entity_count": geo_entity_count,
        "geo_alias_count": geo_alias_count,
        "geo_relation_count": geo_relation_count,
        "geo_entity_usage_count": geo_entity_usage_count,
        "geo_alias_usage_count": geo_alias_usage_count,
        "party_count": party_count,
        "party_usage_count": party_usage_count,
        "legal_term_count": legal_term_count,
        "legal_term_usage_count": legal_term_usage_count,
        "project_total_count": project_total_count,
        "project_completed_count": project_completed_count,
        "project_completed_weight": project_completed_weight,
        "project_progress_avg": project_progress_avg,
        "project_documents_total_count": project_documents_total_count,
        "project_documents_unique_count": project_documents_unique_count,
        "task_queue_total_count": task_queue_total_count,
        "task_queue_completed_count": task_queue_completed_count,
        "task_queue_completed_weight": task_queue_completed_weight,
        "task_queue_progress_avg": task_queue_progress_avg,
        "task_queue_documents_total_count": task_queue_documents_total_count,
        "task_queue_documents_unique_count": task_queue_documents_unique_count,
        "task_queue_reviewers_unique_count": task_queue_reviewers_unique_count,
        "admin_task_total_count": admin_task_total_count,
        "admin_task_by_status_count": admin_task_by_status_count,
    }

    return render(request, "document/stats.html", context)
