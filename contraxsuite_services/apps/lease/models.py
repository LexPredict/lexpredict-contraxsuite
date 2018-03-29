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

from django.db import models

from apps.document.models import Document, TextUnit
from apps.extract.models import Party

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2018, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.0.5/LICENSE"
__version__ = "1.0.8"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class LeaseDocument(Document):
    """
    Lease Document Model.
    The model is in de-normalized state until I understand how to better manage it.
    Storing date in-place makes it easier to edit and search but makes the DB model worse.
    References from terms e.t.c. to lease documents will work anyway.
    """
    class_code = "lease.LeaseDocument"

    lessee = models.CharField(max_length=1024, blank=True, null=True)

    lessor = models.CharField(max_length=1024, blank=True, null=True)

    commencement_date = models.DateField(blank=True, null=True)
    expiration_date = models.DateField(blank=True, null=True)

    lease_type = models.CharField(max_length=20, blank=True, null=True)

    property_type = models.CharField(max_length=200, blank=True, null=True)

    permitted_uses = models.TextField(blank=True, null=True)

    prohibited_uses = models.TextField(blank=True, null=True)

    renew_non_renew_notice_duration = models.DurationField('renew / non-renew notice period',
                                                           blank=True, null=True)

    auto_renew = models.BooleanField(blank=True, default=False)

    address = models.CharField(max_length=1024, blank=True, null=True)

    address_country = models.CharField(max_length=512, blank=True, null=True)

    address_state_province = models.CharField(max_length=1024, blank=True, null=True)

    address_longitude = models.FloatField(blank=True, null=True)

    address_latitude = models.FloatField(blank=True, null=True)

    area_size_sq_ft = models.FloatField('square ft.', blank=True, null=True)

    alterations_allowed = models.TextField(blank=True, null=True)

    security_deposit = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True)

    rent_due_frequency = models.CharField(max_length=50, blank=True, null=True)

    total_rent_amount = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True)

    mean_rent_per_month = models.DecimalField(max_digits=19, decimal_places=4, blank=True,
                                              null=True)

    period_rent_amount = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True)

    construction_allowance = models.BooleanField(blank=True, default=False)

    CONSTRUCTION_ALLOWANCE_TYPE_CHOICES = (
        ('C', 'Cash'),
        ('RR', 'Rent Reduction')
    )

    construction_allowance_type = models.CharField(max_length=5,
                                                   choices=CONSTRUCTION_ALLOWANCE_TYPE_CHOICES,
                                                   blank=True, null=True)

    construction_allowance_amount = models.DecimalField(max_digits=19, decimal_places=4, blank=True,
                                                        null=True)

    late_fee_trigger_days = models.IntegerField('late fee trigger (n days)', blank=True, null=True)

    LATE_FEE_TYPE_CHOICES = (
        ('A', 'Amount'),
        ('I', 'Interest')
    )

    late_fee_type = models.CharField(max_length=5, choices=LATE_FEE_TYPE_CHOICES, blank=True,
                                     null=True)

    late_fee_amount = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True)

    late_fee_interest_rate = models.FloatField('late fee interest rate (percent)', blank=True,
                                               null=True)

    mediation_required = models.BooleanField(blank=True, default=False)

    arbitration_clause = models.BooleanField(blank=True, default=False)

    choice_of_law_clause = models.BooleanField(blank=True, default=False)

    choice_of_law = models.CharField(max_length=100, blank=True)

    forum_selection_clause = models.BooleanField(blank=True, default=False)

    arbitration_forum = models.CharField('arbitration / forum', max_length=100, blank=True,
                                         null=True)

    # Not using references to text units here until better understanding on how to manage it.
    # + for using texts: easier full text search
    # + for using refs: stronger DB model

    insurance = models.TextField(blank=True, null=True)

    ASSIGNMENT_SUBLETTING_PERMITTED_CHOICES = (
        ('Y', 'Yes'),
        ('N', 'No'),
        ('YWR', 'Yes With Notice or Restrictions')
    )

    assignment_subletting_permitted = models.CharField('Assignment / Subletting Permitted',
                                                       max_length=5,
                                                       choices=ASSIGNMENT_SUBLETTING_PERMITTED_CHOICES,
                                                       blank=True, null=True)
    # Sale of Property (ref)
    # or "Do [Tenant/New Owner] rights and obligations surive sale?
    # …Notice/Option to exercise termination right?"

    sale_of_property_behaviour = models.TextField(
        'sale of property / do rights and obligations survive sale',
        blank=True, null=True)

    termination = models.TextField(blank=True, null=True)

    period_rent_due_date = models.DateField(blank=True, null=True)

    period_late_fee_date = models.DateField(blank=True, null=True)

    period_late_fee_amount = models.DecimalField(max_digits=19, decimal_places=4, blank=True,
                                                 null=True)

    mean_rent_per_quarter = models.DecimalField(max_digits=19, decimal_places=4, blank=True,
                                                null=True)

    mean_rent_per_year = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True)
