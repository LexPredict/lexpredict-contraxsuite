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
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.0.0/LICENSE"
__version__ = "2.0.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


import regex as re
from typing import Optional, List, Tuple, Union, Any

from django.db.models import QuerySet


class ProjectsNameFilter:
    reg_variables = re.compile(r'\!*\"[^\"]+\"')

    @classmethod
    def filter_objects_by_name(cls,
                               model_class,
                               name_pattern: Optional[str] = None) -> Optional[List[int]]:
        """
        Returns project ids for the projects whose names match filter
        filter examples:
        1) "test_project"
        2) lit_%
        3) "test" or ("lit_%" and !"lit_unknown")
        :param model_class: model class, like 'Project'
        :param name_pattern: project name filter expression
        :return: list of project ids
        """
        name_pattern = name_pattern.strip()
        if not name_pattern:
            return []
        query = cls.make_query(model_class, name_pattern)
        return [p.pk for p in query]

    @classmethod
    def make_query(cls, model_class: Any, name_pattern: str) -> Union[QuerySet, List[Any]]:
        variables = []  # type: List[Tuple[bool, str]]

        for match in cls.reg_variables.finditer(name_pattern):
            var_val = match.group(0)
            neg = var_val.startswith('!')
            var_val = var_val.strip('!"')
            variables.append((neg, var_val,))

        if not variables:
            return model_class.objects.raw(
                f'SELECT id FROM {model_class._meta.db_table} WHERE name LIKE %s;',
                [name_pattern])

        sql = ''
        last_pos = 0
        var_counter = 0
        for match in cls.reg_variables.finditer(name_pattern):
            # ms, me = (match.start(), match.end(),)
            sql += name_pattern[last_pos:match.start()]
            neg, var_val = variables[var_counter]
            var_counter += 1
            predicate = 'name NOT LIKE %s' if neg else 'name LIKE %s'
            sql += predicate
            last_pos = match.end()

        if last_pos < len(name_pattern):
            sql += name_pattern[last_pos:]

        var_values = [v for n, v in variables]

        return model_class.objects.raw(
            f'SELECT id FROM {model_class._meta.db_table} WHERE {sql};',
            var_values)
