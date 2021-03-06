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
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.8.0/LICENSE"
__version__ = "1.8.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


from tests.django_test_case import *
from django.test import TestCase

from apps.analyze.ml.utils import ProjectsNameFilter
from apps.project.models import Project


class TestProjectsNameFilter(TestCase):
    def test_simple_query(self):
        query = ProjectsNameFilter.make_query(Project, 'lit_%')
        self.assertEqual('SELECT id FROM project_project WHERE name LIKE %s;',
                         query.query.sql)
        self.assertEqual(['lit_%'], query.query.params)

    def test_complex_query(self):
        query = ProjectsNameFilter.make_query(Project, '"test" or ("lit_%" and !"lit_unknown")')
        self.assertEqual('SELECT id FROM project_project WHERE name LIKE %s or (name LIKE %s and name NOT LIKE %s);',
                         query.query.sql)
        self.assertEqual(['test', 'lit_%', 'lit_unknown'], query.query.params)

    def non_test_get_ids(self):
        ids = ProjectsNameFilter.filter_objects_by_name(Project, 'lit_%')
        self.assertEqual([66, 67, 68, 71, 72], ids)

        ids = ProjectsNameFilter.filter_objects_by_name(Project, '"lit_%" and !"lit_selected"')
        self.assertEqual([66, 67, 71, 72], ids)
