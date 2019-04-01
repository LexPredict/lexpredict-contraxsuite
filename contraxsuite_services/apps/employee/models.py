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

from django.db import models
from apps.document.models import Document, TextUnit
from apps.extract.models import Usage

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2018, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.2.0/LICENSE"
__version__ = "1.2.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class Employer(models.Model):

    name = models.CharField(max_length=1024, db_index=True)


class EmployerUsage(Usage):

    employer = models.ForeignKey(Employer, db_index=True)

    class Meta:
        ordering = ['-count']


class Employee(models.Model):

    document = models.ForeignKey(Document, db_index=True)
    name = models.CharField(max_length=1024, db_index=True)
    employer = models.ForeignKey(Employer, db_index=True, blank=True, null=True)
    annual_salary = models.FloatField(blank=True, null=True)
    salary_currency = models.CharField(max_length=10, blank=True, null=True)
    vacation_yearly = models.CharField(max_length=1024, db_index=True, null=True)
    effective_date = models.DateField(blank=True, null=True)
    governing_geo = models.CharField(max_length=1024, null=True, blank=True)
    has_noncompete = models.BooleanField(default=False)
    has_termination = models.BooleanField(default=False)
    has_benefits = models.BooleanField(default=False)
    has_severance=models.BooleanField(default=False)

    class Meta:
        unique_together = (("name", "document"),)
        verbose_name_plural = 'Employees'
        ordering = ('name',)

    def __str__(self):
        return "Employee (" \
               "doc_id= {0}," \
               "name={0}," \
               "salary={2})" \
            .format(self.document.id, self.name, self.annual_salary)


class Provision(models.Model):

    text_unit = models.ForeignKey(TextUnit)
    similarity = models.DecimalField(max_digits=5, decimal_places=2)
    employee = models.ForeignKey(Employee)
    document = models.ForeignKey(Document)
    type = models.TextField(max_length=255)    # noncompete, termination

