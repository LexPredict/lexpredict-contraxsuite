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
__version__ = "1.5.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


from django.db import migrations, connection

# We set Mail backend to "log" option if the mail server hasn't been configured
# We suppose the server wasn't configured if no email_host_user value is provided


def do_migrate(_apps, _schema_editor):
    mail_user = ''
    with connection.cursor() as cursor:
        cursor.execute('''SELECT "value" FROM common_appvar WHERE 
            "category" = 'Mail server' and "name" = 'email_host_user';''')
        for row in cursor.fetchall():
            mail_user = row[0]

        if mail_user:
            # we believe the user
            return

        cursor.execute('''UPDATE common_appvar SET "value" = to_json('log'::TEXT) WHERE "name" = 'email_backend';''')


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0044_update_appvar_duplicate_docs'),
    ]

    operations = [
        migrations.RunPython(do_migrate, reverse_code=migrations.RunPython.noop),
    ]
