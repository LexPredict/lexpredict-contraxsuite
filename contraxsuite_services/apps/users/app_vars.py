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

# Project imports
from apps.common.models import AppVar
from django.conf import settings

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2020, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.8.0/LICENSE"
__version__ = "1.8.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


ALLOWED_EMAIL_DOMAINS = AppVar.set(
    'User', 'allowed_email_domains', '*',
    '''Allowed for social registration email domains, comma separated, 
       with optional wildcard characters''')

AUTO_REG_EMAIL_DOMAINS = AppVar.set(
    'User', 'auto_reg_email_domains', '',
    '''User whose email belongs to one of these domains will be automatically
       registered after signing in from a social application. The string contains
       email domains, comma separated, with optional wildcard characters''')

ACCOUNT_ALLOW_REGISTRATION = AppVar.set(
    'User', 'account_allow_registration',
    False,
    '''Allow user registration through regular sign up form.''')

SOCIAL_ACCOUNT_ALLOW_REGISTRATION = AppVar.set(
    'User', 'social_account_allow_registration',
    True,
    '''Allow user registration through social applications.''')

AZURE_AD_ALLOW_SWITCH_TENANT = AppVar.set(
    'User', 'azure_ad_allow_switch_tenant', True,
    '''Allow switching tenant on Azure AD login page.''')

SOCIALACCOUNT_EMAIL_VERIFIED_ONLY = AppVar.set(
    'User', 'socialaccount_email_verified_only', True,
    '''Allow only social accounts with verified email address.''')

READ_AZURE_AD_PRINCIPAL_EMAIL = AppVar.set(
    'User', 'read_azure_ad_principal_email', True,
    '''Try getting email address from Azure AD principal.'''
)
