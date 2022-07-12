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

import os

from django.core.files.uploadedfile import UploadedFile
from django.core.exceptions import ValidationError
from django.conf.urls import url, include
from django.urls import path
from django.utils.datastructures import MultiValueDict

from rest_framework.permissions import IsAuthenticated
from rest_framework_tus.views import *

from apps.project.models import UploadSession
from apps.tus.schemas import TusUploadViewSetSchema

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2022, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class TusPermissions(IsAuthenticated):
    def has_permission(self, request, view):
        user = request.user
        # otherwise schema generations fails
        if 'upload_session_id' in view.kwargs:
            session = UploadSession.objects.get(pk=view.kwargs['upload_session_id'])
            return user.has_perm('project.add_project_document', session.project)
        return user.has_perm('project.add_uploadsession')


class TusUploadViewSet(UploadViewSet):
    """
    Patched UploadViewSet to handle custom storages and upload_session_id
    """
    permission_classes = (TusPermissions,)
    schema = TusUploadViewSetSchema()
    # PATCHED: otherwise url route fails
    versioning_class = None

    def create(self, request, *args, **kwargs):
        """
        Create an Upload
        INFO: patched initial method to make a check
        """
        # Get file size from request
        upload_length = getattr(request, constants.UPLOAD_LENGTH_FIELD_NAME, -1)

        # Get metadata from request
        upload_metadata = getattr(request, constants.UPLOAD_METADATA_FIELD_NAME, {})

        # Get data from metadata
        filename = upload_metadata.get(tus_settings.TUS_FILENAME_METADATA_FIELD, '')

        # PATCHED - do file check for exists/empty/delete_pending/processing status
        from apps.project.api.v1 import UploadSessionViewSet
        project = UploadSession.objects.get(pk=self.kwargs['upload_session_id']).project

        can_upload_status = UploadSessionViewSet.can_upload_file(
            project, filename, upload_length, kwargs['upload_session_id'])

        from apps.document.app_vars import ALLOW_DUPLICATE_DOCS
        force_rename = request.POST.get('force') == 'true' or \
                       request.META.get('HTTP_FORCE') == 'true' or \
                       ALLOW_DUPLICATE_DOCS.val(project_id=project.id)

        if not force_rename and can_upload_status is not True:
            return Response(data={'status': can_upload_status}, status=status.HTTP_400_BAD_REQUEST)
        # end patch

        return super().create(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        """
        Transfer file data
        """

        # PATCHED: Validate upload session url kwarg
        upload_session_id = kwargs.get('upload_session_id')
        try:
            UploadSession.objects.get(pk=upload_session_id)
        except (UploadSession.DoesNotExist, ValidationError):
            return Response('Wrong upload session uid.', status=status.HTTP_400_BAD_REQUEST)

        # Validate tus header
        if not has_required_tus_header(request):
            return Response('Missing "{}" header.'.format('Tus-Resumable'), status=status.HTTP_400_BAD_REQUEST)

        # Validate content type
        if not self._is_valid_content_type(request):
            return Response('Invalid value for "Content-Type" header: {}. Expected "{}".'.format(
                request.META['CONTENT_TYPE'], TusUploadStreamParser.media_type), status=status.HTTP_400_BAD_REQUEST)

        # Retrieve object
        upload = self.get_object()

        # Get upload_offset
        upload_offset = getattr(request, constants.UPLOAD_OFFSET_NAME)

        # Validate upload_offset
        if upload_offset != upload.upload_offset:
            raise Conflict

        # Make sure there is a tempfile for the upload
        assert upload.get_or_create_temporary_file()

        # Change state
        if upload.state == states.INITIAL:
            upload.start_receiving()
            upload.save()

        # Get chunk from request
        chunk_bytes = self.get_chunk(request)

        # Check for data
        if not chunk_bytes:
            return Response('No data.', status=status.HTTP_400_BAD_REQUEST)

        # Check checksum  (http://tus.io/protocols/resumable-upload.html#checksum)
        upload_checksum = getattr(request, constants.UPLOAD_CHECKSUM_FIELD_NAME, None)
        if upload_checksum is not None:
            if upload_checksum[0] not in tus_api_checksum_algorithms:
                return Response('Unsupported Checksum Algorithm: {}.'.format(
                    upload_checksum[0]), status=status.HTTP_400_BAD_REQUEST)
            if not checksum_matches(
                    upload_checksum[0], upload_checksum[1], chunk_bytes):
                return Response('Checksum Mismatch.', status=460)

        # Run chunk validator
        chunk_bytes = self.validate_chunk(upload_offset, chunk_bytes)

        # Check for data
        if not chunk_bytes:
            return Response('No data. Make sure "validate_chunk" returns data.', status=status.HTTP_400_BAD_REQUEST)

        # Write file
        chunk_size = int(request.META.get('CONTENT_LENGTH', 102400))
        try:
            upload.write_data(chunk_bytes, chunk_size)
        except Exception as e:
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)

        headers = {
            'Upload-Offset': upload.upload_offset,
        }

        response_data = None

        if upload.upload_length == upload.upload_offset:
            # PATCHED: re-send request to our native upload() method
            from apps.project.api.v1 import UploadSessionViewSet

            file = UploadedFile(file=open(upload.temporary_file_path, 'rb'),
                                name=upload.filename,
                                size=upload.upload_length)
            request._files = MultiValueDict()
            request._files['file'] = file

            try:
                directory_path = os.path.dirname(json.loads(upload.upload_metadata)['relativePath'])
            except (KeyError, TypeError, json.JSONDecodeError):
                directory_path = None

            response = UploadSessionViewSet(
                request=request,
                format_kwarg=upload_session_id,
                action='upload',
                kwargs={'pk': upload_session_id}).upload(request=request,
                                                         pk=upload_session_id,
                                                         review_file=False,
                                                         directory_path=directory_path)
            if response.status_code != 200:
                return response
            response_data = response.data

            # Trigger signal
            signals.received.send(sender=upload.__class__, instance=upload)

        # Add upload expiry to headers
        add_expiry_header(upload, headers)

        return Response(data=response_data, headers=headers, status=status.HTTP_204_NO_CONTENT)

        # # By default, don't include a response body
        # if not tus_settings.TUS_RESPONSE_BODY_ENABLED:
        #     return Response(headers=headers, status=status.HTTP_204_NO_CONTENT)
        #
        # # Create serializer
        # serializer = self.get_serializer(instance=upload)
        #
        # return Response(serializer.data, headers=headers, status=status.HTTP_204_NO_CONTENT)

    def get_success_headers(self, data):
        try:
            # PATCHED: changed url name and added upload_session_id to it
            return {'Location': reverse('v1:tus:upload',
                                        kwargs={'upload_session_id': self.kwargs['upload_session_id'],
                                                'guid': data['guid']})}
        except (TypeError, KeyError):
            return {}


tus_api_urlpatterns = [
    path('upload-session/<str:upload_session_id>/upload/',
         TusUploadViewSet.as_view({'post': 'create'}), name='init_upload'),

    path('upload-session/<str:upload_session_id>/upload/<str:guid>/',
         TusUploadViewSet.as_view({'patch': 'partial_update'}), name='upload')
]

urlpatterns = [
    url('', include((tus_api_urlpatterns, 'tus'), namespace='tus'))
]
