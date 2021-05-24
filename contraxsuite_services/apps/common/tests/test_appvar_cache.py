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

from tests.django_test_case import *

from typing import Optional, Dict, Any, Tuple, Callable

from apps.common.models import AppVar, AppVarStorage, ProjectAppVar

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.0.0/LICENSE"
__version__ = "2.0.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class AppVarMock(AppVarStorage):
    # {category: {name: {project_id: value}}}
    DB_VALUES: Dict[str, Dict[str, Dict[Optional[int], Any]]] = {}

    REDIS_VALUES: Dict[str, Any] = {}

    on_db_read: Optional[Callable[[], None]] = None

    class Meta:
        managed = False

    @classmethod
    def clear_test_data(cls):
        cls.DB_VALUES = {}
        cls.REDIS_VALUES = {}

    @classmethod
    def _should_return_mock(cls) -> bool:
        return False

    @classmethod
    def _read_db_values(cls,
                        category: str,
                        name: str,
                        project_id: Optional[int]) -> Dict[Optional[int], Any]:
        if cls.on_db_read:
            cls.on_db_read()
        cat_values = cls.DB_VALUES.get(category)
        if not cat_values:
            return {}
        name_values = cat_values.get(name)
        if not name_values:
            return {}

        values = {}
        if project_id in name_values:
            values[project_id] = name_values[project_id]
        if None in name_values:
            values[None] = name_values[None]
        return values

    @classmethod
    def _get_project_db_app_vars(cls, project_id: int, user=None):
        if cls.on_db_read:
            cls.on_db_read()
        a_vars = []
        for category in cls.DB_VALUES:
            cat_values = cls.DB_VALUES[category]
            for name in cat_values:
                for p_id in cat_values[name]:
                    if p_id is not None and project_id != p_id:
                        continue
                    apv = AppVar()
                    apv.category = category
                    apv.name = name
                    apv.value = cat_values[name][p_id]
                    apv.project_id = p_id
                    a_vars.append(apv)
        return a_vars

    @classmethod
    def _cache(cls, category: str, name: str, access_type: str, project_id: Optional[int], value: Any):
        key = cls._make_cache_key(category, name, access_type, project_id)
        cls.REDIS_VALUES[key] = value

    @classmethod
    def _read_cached(cls, category: str, name: str, access_type: str, project_id: Optional[int]) -> Any:
        key = cls._make_cache_key(category, name, access_type, project_id)
        return cls.REDIS_VALUES.get(key)

    @classmethod
    def _save_app_var_in_db(cls,
                            category: str,
                            description: str,
                            name: str,
                            access_type: str,
                            project_id: Optional[int],
                            value: Any,
                            user_id: Optional[int] = None) -> Tuple['AppVar', bool]:
        cat_values = cls.DB_VALUES.get(category)
        if not cat_values:
            cat_values = {}
            cls.DB_VALUES[category] = cat_values

        name_values = cat_values.get(name)
        if not name_values:
            name_values = {}
            cat_values[name] = name_values

        created = project_id in name_values
        name_values[project_id] = value

        apv = AppVarMock()
        apv.category = category
        apv.name = name
        apv.description = description
        apv.access_type = access_type
        apv.project_id = project_id
        apv.value = value
        apv.user_id = user_id
        return apv, created

    @classmethod
    def _check_app_var_in_db(
            cls,
            category: str,
            description: str,
            name: str,
            access_type: str,
            project_id: Optional[int],
            value: Any,
            user_id: Optional[int] = None) -> Tuple['AppVar', bool]:
        cat_values = cls.DB_VALUES.get(category)
        if not cat_values:
            cat_values = {}
            cls.DB_VALUES[category] = cat_values

        name_values = cat_values.get(name)
        if not name_values:
            name_values = {}
            cat_values[name] = name_values

        created = project_id not in name_values
        if created:
            name_values[project_id] = value

        apv = AppVarMock()
        apv.category = category
        apv.name = name
        apv.description = description
        apv.access_type = access_type
        apv.project_id = project_id
        apv.value = name_values[project_id]
        apv.user_id = user_id
        return apv, created

    @classmethod
    def _save_app_var_db_record(cls, app_var):
        pass

    @classmethod
    def _delete_app_var_rows(cls, project_id: int, category: str, name: str):
        if category not in cls.DB_VALUES:
            return
        cat_values = cls.DB_VALUES[category]
        if name not in cat_values:
            return
        if project_id in cat_values[name]:
            del cat_values[name][project_id]

    @classmethod
    def clear_key(cls, category: str, name: str, access_type: str, project_id: Optional[int] = None):
        cache_key = cls._make_cache_key(category, name, access_type, project_id)
        if cache_key in cls.REDIS_VALUES:
            del cls.REDIS_VALUES[cache_key]


class TestAppVarCache(TestCase):
    def setUp(self) -> None:
        AppVarMock.clear_test_data()
        super().setUp()

    def test_set_read(self):
        db_reads = 0

        def increase_reads():
            nonlocal db_reads
            db_reads += 1
        AppVarMock.on_db_read = increase_reads
        AppVarMock.clear_test_data()
        app_var = AppVarMock.set('test', 'fruit', 'apple')
        db_reads = 0

        val = AppVarMock.val(
            app_var.category, app_var.name, app_var.description, app_var.access_type, app_var.value, None)
        self.assertEqual('apple', val)
        self.assertEqual(0, db_reads)

        for _ in range(2):
            val = AppVarMock.val(app_var.category, app_var.name, app_var.description, app_var.access_type, app_var.value, 104)
            self.assertEqual('apple', val)
        self.assertEqual(1, db_reads)

    def test_prefer_project_level(self):
        app_var = AppVarMock.set('test', 'fruit', 'apple', project_id=104)

        val = AppVarMock.val(
            app_var.category, app_var.name, app_var.description, app_var.access_type, app_var.value, None)
        self.assertEqual('apple', val)

        val = AppVarMock.val(app_var.category, app_var.name, app_var.description, app_var.access_type, app_var.value, 104)
        self.assertEqual('apple', val)

    def test_read_db_once(self):
        db_reads = 0

        def increase_reads():
            nonlocal db_reads
            db_reads += 1

        AppVarMock.on_db_read = increase_reads

        app_var = AppVarMock.set('test', 'fruit', 'apple')
        AppVarMock.REDIS_VALUES = {}  # clear "cache"

        val = AppVarMock.val(
            app_var.category, app_var.name, app_var.description, app_var.access_type, app_var.value, None)
        self.assertEqual('apple', val)

        for project_id in [104, None, None, None, 104, 104]:
            val = AppVarMock.val(app_var.category, app_var.name, app_var.description, app_var.access_type, app_var.value, project_id)
            self.assertEqual('apple', val)

        # there may be one or two DB reads
        # first we search for system level appvar, we get it in the DB only and we cache it (wo project_id)
        # second, we search for project level appvar. We get it in the DB and we cache it.
        self.assertLess(db_reads, 3)

    def test_read_unknown_project(self):
        app_var = AppVarMock.set('test', 'fruit', 'apple', project_id=104)

        val = AppVarMock.val(
            app_var.category, app_var.name, app_var.description, app_var.access_type, app_var.value, 103)
        self.assertEqual('apple', val)

        val = AppVarMock.val(app_var.category, app_var.name, app_var.description, app_var.access_type, app_var.value, None)
        self.assertEqual('apple', val)

    def test_get_project_appvars(self):
        AppVarMock.set('test', 'fruit', 'apple', description='Some fruit')
        AppVarMock.set('test', 'fruit', 'pineapple', project_id=101)
        AppVarMock.set('test', 'fruit', 'pine', project_id=102)
        AppVarMock.set('test', 'veg', 'carrot', description='Some veg')
        AppVarMock.set('test', 'diary', 'cream', description='Some diary', project_id=101)
        AppVarMock.set('test', 'plant', 'corn', description='Some plant', project_id=102)

        proj_vars = AppVarMock.get_project_app_vars(101, None, False)
        self.assertEqual(3, len(proj_vars))
        var_values = ','.join(sorted([v.value or v.system_value for v in proj_vars]))
        self.assertEqual('carrot,cream,pineapple', var_values)

        veg_var = [v for v in proj_vars if v.name == 'veg'][0]
        self.assertIsNone(veg_var.value)
        self.assertEqual('carrot', veg_var.system_value)
        self.assertTrue(veg_var.use_system)

    def test_apply_project_appvars(self):
        AppVarMock.set('test', 'fruit', 'apple', description='Some fruit')
        AppVarMock.set('test', 'fruit', 'pineapple', project_id=101)
        AppVarMock.set('test', 'fruit', 'pine', project_id=102)
        AppVarMock.set('test', 'veg', 'carrot', description='Some veg')
        AppVarMock.set('test', 'diary', 'cream', description='Some diary', project_id=101)
        AppVarMock.set('test', 'plant', 'corn', description='Some plant', project_id=102)

        AppVarMock.apply_project_app_vars(
            101,
            [
                ProjectAppVar('test', 'fruit', 'auth', '', None, True, 'apple'),  # clear project value
                ProjectAppVar('test', 'veg', 'auth', '', 'beetroot', False, 'carrot'),  # replace system value
                ProjectAppVar('test', 'plant', 'auth', '', 'popcorn', False, '')  # add new value
            ], None)
        proj_vars = AppVarMock.get_project_app_vars(101, None, False)
        self.assertEqual(4, len(proj_vars))
        var_values = ','.join(sorted([v.value or v.system_value for v in proj_vars]))
        self.assertEqual('apple,beetroot,cream,popcorn', var_values)
