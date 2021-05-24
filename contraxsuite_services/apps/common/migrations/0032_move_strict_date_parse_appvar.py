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


from django.conf import settings
from django.db import migrations

NEW_DESC_STRICT_PARSE = """<ul><li><code>true</code>: skip values like "C-4-30"</li></ul>"""

NEW_DESC_SIMPLE_TOK = """<ul>
          <li><code>true</code>: use regex tokenization when locating Courts and GeoEntities,</li>
          <li><code>false</code>: use ML based tokenization (slightly more accurate, significantly slower).</li>
       </ul>""".replace('\n', ' ')

NEW_DESC_MAIL_SERVER = """<ul>
        <li><code>"default":</code>: change to ''default'' once you have updated smtp information in 
           order for emails to go out. Uses default ContraxSuite Mail sender class</li>
        <li><code>"log"</code>: don''t send emails, log the messages instead</li>
        <li><code>"&lt;fully.qualified.class.name&gt;"</code>: use specific Mail sender 
            class, specify the class by fully qualified name</li>
    </ul>""".replace('\n', ' ')


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('common', '0031_smtp_backend_appvar_description'),
    ]

    operations = [
        migrations.RunSQL(
            f'''UPDATE common_appvar SET "category" = 'Extract' 
            WHERE "name" = 'strict_parse_dates' AND "category" = 'Document';
            
            UPDATE common_appvar SET description='{NEW_DESC_STRICT_PARSE}'
            WHERE "name" = 'strict_parse_dates' and "category" = 'Extract';
            
            UPDATE common_appvar SET description='{NEW_DESC_SIMPLE_TOK}'
            WHERE "name" = 'simple_locator_tokenization' and "category" = 'Extract';
            
            UPDATE common_appvar SET description='{NEW_DESC_MAIL_SERVER}'
            WHERE "name" = 'email_backend' and "category" = 'Mail server';
            ''',

            reverse_sql='''UPDATE common_appvar SET "category" = 'Document' 
            WHERE "name" = 'strict_parse_dates' AND "category" = 'Extract';
            
            UPDATE common_appvar SET description='Skip values like "C-4-30" if strict mode (True) is on'
            WHERE "name" = 'strict_parse_dates' and "category" = 'Document';
            
            UPDATE common_appvar SET description='Don''t use NLTK when checking dictionary entries while locating Courts and GeoEntities in the document.'
            WHERE "name" = 'simple_locator_tokenization' and "category" = 'Extract';
            '''),
    ]
