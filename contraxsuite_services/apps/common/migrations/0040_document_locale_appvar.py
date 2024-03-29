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
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.9.0/LICENSE"
__version__ = "1.9.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('common', '0039_auto_20210311_0543'),
    ]

    operations = [
        migrations.RunSQL('''UPDATE common_appvar SET name = 'document_locale' WHERE name = 'ocr_language';'''),
        migrations.RunSQL('''UPDATE common_appvar SET description = 'Sets default document locale.' 
WHERE name = 'document_locale';'''),
        migrations.RunSQL('''UPDATE common_appvar SET value = NULL 
WHERE name = 'document_locale' AND project_id IS NULL;'''),
        migrations.RunSQL('''DELETE FROM common_appvar WHERE name = 'locate_day_first';'''),
    ]
