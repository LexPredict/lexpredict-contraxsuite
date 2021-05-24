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
__copyright__ = "Copyright 2015-2020, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.5.0/LICENSE"
__version__ = "1.9.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


from django.conf import settings
from django.db import migrations, connection


OLD_DESCRIPTION = 'Email backend class'

NEW_DESCRIPTION = '''Email backend class:
    <ul>
        <li><code>"default":</code>: use default ContraxSuite Mail sender class</li>
        <li><code>"log"</code>: don't send emails, log the messages instead</li>
        <li><code>"&lt;fully.qualified.class.name&gt;"</code>: use specific Mail sender 
            class, specify the class by fully qualified name</li>
    </ul>'''

KNOWN_VALUES = {
        'default': 'smtp.CustomEmailBackend',
        'log': 'django.core.mail.backends.console.EmailBackend'
    }

KNOWN_ALIASES = {KNOWN_VALUES[k]: k for k in KNOWN_VALUES}


def migrate_description(_apps, _schema_editor):
    # description
    with connection.cursor() as cursor:
        cursor.execute('''
            UPDATE common_appvar SET description = %s 
            WHERE name = 'email_backend' and description = %s;''',
                       [NEW_DESCRIPTION, OLD_DESCRIPTION])
        # value (alias)
        cursor.execute('''select value from common_appvar WHERE name = 'email_backend';''')
        row = cursor.fetchone()
        if not row:
            return
        back_value = row[0]
        # replace the value by it's alias
        if back_value in KNOWN_ALIASES:
            cursor.execute('''UPDATE common_appvar SET value = to_json(%s::TEXT) 
                            WHERE name = 'email_backend';''', [KNOWN_ALIASES[back_value]])


def unmigrate_description(_apps, _schema_editor):
    # description
    with connection.cursor() as cursor:
        cursor.execute('''
            UPDATE common_appvar SET description = %s 
            WHERE name = 'email_backend' and description = %s;''',
                       [OLD_DESCRIPTION, NEW_DESCRIPTION])
        # value (alias)
        cursor.execute('''select value from common_appvar WHERE name = 'email_backend';''')
        row = cursor.fetchone()
        if not row:
            return
        back_value = row[0]
        # replace the value by it's alias
        if back_value in KNOWN_VALUES:
            cursor.execute('''UPDATE common_appvar SET value = to_json(%s::TEXT) 
                            WHERE name = 'email_backend';''', [KNOWN_VALUES[back_value]])


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('common', '0030_smtp_backend_appvar'),
    ]

    operations = [
        migrations.RunPython(migrate_description, reverse_code=unmigrate_description)
    ]
