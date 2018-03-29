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

# Third-party imports
from rest_framework import routers, viewsets

# Project imports
from apps.common.mixins import JqMixin, SimpleRelationSerializer
from apps.users.models import User

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2018, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.0.5/LICENSE"
__version__ = "1.0.8"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


# --------------------------------------------------------
# User Views
# --------------------------------------------------------

class UserSerializer(SimpleRelationSerializer):

    class Meta:
        model = User
        fields = ['id', 'username', 'last_name', 'first_name',
                  'email', 'is_superuser', 'is_staff', 'is_active',
                  'name', 'role', 'organization']

    def get_fields(self):
        if not self.context['request'].user.is_superuser:
            return ['username', 'first_name', 'last_name', 'name']
        return super().get_fields()


class UserViewSet(JqMixin, viewsets.ModelViewSet):
    """
    list: User List\n
        GET params:
            - first_name: str
            - last_name: str
            - name: str
            - email: str
            - role: str
            - organization: str
    create: Create User
    retrieve: Retrieve User
    update: Update User
    partial_update: Partial Update User
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    http_method_names = ['get', 'post', 'put', 'patch']


router = routers.DefaultRouter()
router.register(r'users', UserViewSet, 'user')
