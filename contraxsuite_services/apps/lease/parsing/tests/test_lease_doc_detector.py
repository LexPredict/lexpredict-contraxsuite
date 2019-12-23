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

from nose.tools import assert_equal

from apps.lease.parsing.lease_doc_detector import LeaseDocDetector

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2019, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.4.0/LICENSE"
__version__ = "1.4.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


LEASE_AGREEMENT_1 = '''
Lease Agreement
 
This Lease Agreement (this “Agreement”) is made this __________ day of __________, __________, by and between __________ located at __________, __________, NY, __________ (“Landlord”) and __________, located at __________, __________, NY, __________ (“Tenant”). Each Tenant is jointly and severally liable to Landlord for payment of rent and performance in accordance with all other terms of this Agreement.
 
1. Premises. The premises is a __________ located at __________, __________, NY, __________ (the “Premises”).  
 
2. Agreement to Lease. Landlord agrees to lease to Tenant and Tenant agrees to lease from Landlord, the Premises according to the terms and conditions in this Agreement.
 
3. Term. This Lease will be for a term of __________ months beginning on __________ and ending on __________ (the “Term”).
 
4. Rent.  Tenant will pay Landlord a monthly rent of __________.  The rent is payable in advance and due on the __________ of each month during the Term. The rent will be paid to the Landlord at the Landlord's address stated above (or at another address as directed by Landlord) by mail or in person and accepted via one of the following methods: ________________________________.
The first rent payment is payable to Landlord when Tenant signs this Agreement. 
 
5. Additional Rent. There may be instances under this Agreement where Tenant may be required to pay additional charges to Landlord. All such charges are considered additional rent under this Agreement and will be paid with the next regularly scheduled rent payment. If Tenant does not pay rent , Tenant will pay a late charge in the amount of __________ of the monthly rent and such late charge will be paid as additional rent. Landlord has the same rights and Tenant has the same obligations with respect to additional rent as they do with rent.
 
6. Use of Premises. The Premises will be occupied only by the Tenant and his/her/their immediate family and used only for residential purposes.
 
7. Landlord's Failure to Give Possession. In the event Landlord is unable to give possession of the Premises to Tenant on the start date of the Term, Tenant will not be liable for rent until after Landlord gives possession of the Premises to Tenant. This does not affect the end date of the Term.
 
8. Security Deposit. At the same time Tenant signs this Agreement, Tenant will pay a security deposit in the amount of __________ to Landlord. The security deposit will be retained by Landlord as security for Tenant’s performance of obligations under this Agreement. If Tenant does not comply with any of the terms of this Agreement, Landlord may apply any or all of the security deposit in payment of any amount owed by Tenant and for any damages and costs incurred by Landlord due to Tenant’s failure to comply. Landlord will provide to Tenant written notice of use of any or all of the security deposit. Tenant will, within __________ days following receipt of such written notice, pay to Landlord the amount equal to that used by Landlord in order to restore the security deposit to its full amount. Within __________ days after the termination of this Agreement, Landlord will return the security deposit (minus any amount not applied by Landlord in accordance with this section) to Tenant. The security deposit will bear interest while held by Landlord in accordance with applicable state laws and/or local ordinances.
 
9. Utilities. Tenant is responsible for payment of all utility and other services for the Premises including ____________________________ except for the following: ____________________________, which will be paid for by Landlord.
 
10. Condition of the Premises. Tenant has examined the Premises, including the appliances, fixtures and other furnishings, acknowledges that they are in good repair and condition and accepts them in its current condition.
 
11. Maintenance and Repairs. Tenant will keep the Premises, including the grounds and all appliances, fixtures and furnishings, in clean, sanitary and good condition and repair. If repairs other than general maintenance are required, Tenant will notify Landlord for such repairs. In the event of default by Tenant, Tenant will reimburse Landlord for the cost of any repairs or replacement.
 
12. Alterations. Tenant will not make any alteration, addition or improvement to the Premises without first obtaining Landlord’s written consent. Any and all alterations, additions or improvements to the Premises are without payment to Tenant and will become Landlord’s property immediately on completion and remain on the Premises unless Landlord requests or permits removal in which Tenant will then return that part of the Premises to the same condition as existed prior to the alteration, addition or improvement. Tenant will not change any existing locks or install any additional locks on the Premises without first obtaining Landlord's written consent and without providing Landlord a copy of all keys.
 
13. Fire and Casualty. If the Premises are damaged by fire or other serious disaster or accident and the Premises become uninhabitable as a result, Tenant may immediately vacate the Premises and terminate this Agreement upon notice to Landlord. Tenant will be responsible for any unpaid rent or will receive any prepaid rent up to the day of such fire, disaster or accident. If the Premises are only partially damaged and inhabitable, Landlord may make full repairs and will do so within a prompt and reasonable amount of time. At the discretion of Landlord, the rent may be reduced while the repairs are being made.
 
14. Liability. Landlord is not responsible and liable for any loss, claim, damage or expense as a result of any accident, injury or damage to any person or property occurring anywhere on the Premises unless resulting from the negligence or willful misconduct of Landlord.
 
15. Assignment and Subletting. Tenant will not assign this Agreement as to any portion or all of the Premises or make or permit any total or partial sublease or other transfer of any portion or all of the Premises without obtaining Landlord’s prior written consent.
 
16. Insurance Requirements. Tenant will not do or permit to be done any act or thing that will increase the insurance risk under any policy of insurance covering the Premises. If the premium for such policy of insurance increases due to a breach of Tenant’s obligations under this Agreement, Tenant will pay the additional amount of premium as additional rent under this Agreement.
 
17. Right of Entry. Landlord or its agents may enter the Premises at reasonable times to inspect the Premises, to make any alternations, improvements or repairs or to show the Premises to any prospective tenant, buyer or lender. In the event of an emergency, Landlord may enter the Premises at any time.
 
18. Subordination. This Agreement and Tenant’s right under it shall be subject and subordinate to the lien, operation and effect of each existing or future mortgage, deed of trust, ground lease and/or any other similar instrument of encumbrance covering any or all of the Premises and each renewal, modification, consolidation, replacement or extension thereof.
 
19. Condemnation.
a.       Effect of Condemnation. If all or substantially all of the Premises are covered by a condemnation including the exercise of any power of eminent domain by a governmental authority, this Agreement shall terminate on the date the possession of the Premises is taken by the condemning authority, and all rent under this Agreement shall be apportioned and paid to such date.
b.      Right to Award. Landlord is entitled to collect from the condemning authority the entire amount of any award made in any proceeding. Tenant waives any right, title or interest which he/she/they may have to any such award and agrees to not make any claim for the unexpired Term of this Agreement.
 
20. Notices. All notices given under this Agreement must be in writing. A notice is effective upon receipt and shall be either delivered in person, sent by overnight courier service or sent via certified or registered mail, addressed to the Landlord or Tenant at the address stated above or to another address as Landlord may designate upon reasonable notice to Tenant.
 
21. Default and Remedies.
a.       Default. In the event of any default under this Agreement, Landlord may provide Tenant a notice of default and an opportunity to correct such default. If Tenant fails to correct the default, other than a failure to pay rent or additional rent, Landlord may terminate this Agreement by giving a __________ day written notice to Tenant via any of the following methods: ________________________________________________.
If the default is Tenant’s failure to timely pay rent or additional rent as specified in this Agreement, Landlord may terminate this Agreement by giving a __________ day written notice to Tenant. After termination of this Agreement, Tenant remains liable for any rent, additional late, costs including costs to remedy any defaults, and damages under this Agreement.
b.      Other Remedies. If this Agreement is terminated due to Tenant’s default, Landlord may, in addition to any rights and remedies available under this Agreement and applicable law, use any dispossession, eviction or other similar legal proceeding.
 
22. Surrender. Tenant will deliver and surrender to Landlord possession of the Premises immediately upon the expiration of the Term or the termination of this Agreement, clean and in as good condition and repair as the Premises were on the delivery date except for damage by fire, casualty or condemnation and ordinary wear and tear.
 
23. Quiet Enjoyment. If Tenant pays the Rent and performs all other obligations under this Agreement, Tenant may peaceably and quietly hold and enjoy the Premises during the Term.
 
24. No Waiver. Neither Landlord nor Tenant shall be deemed to have waived any provision of this Agreement or the exercise of any rights held under this Agreement unless such waiver is made expressly and in writing.
 
25. Severability. If any provision of this Agreement is held to be invalid or unenforceable in whole or in part, the remaining provisions shall not be affected and shall continue to be valid and enforceable as though the invalid or unenforceable parts had not been included in this Agreement.
 
26. Successors and Assigns. This Agreement will inure to the benefit of and be binding upon Landlord, its successors and assigns, and upon Tenant and its permitted successors and assigns.
 
27. Entire Agreement. This Agreement constitutes the entire agreement between Landlord and Tenant and supersedes all prior understandings of Landlord and Tenant, including any prior representation, statement, condition, or warranty.
 
28. Amendments. This Agreement may be amended or modified only by a written agreement signed by both Landlord and Tenant.
 
 
Additional Provisions and/or Disclosures.
________________________________________________________________________
________________________________________________________________________
________________________________________________________________________
________________________________________________________________________
________________________________________________________________________
 
SIGNATURES
 
 
___________________________________
Landlord
 
 
___________________________________
Tenant
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
This page intentionally left blank.
Form: Lease Agreement (Rev. 05-2015)

GENERAL INSTRUCTIONS
 
Regardless of whether you are the landlord renting or leasing property to a tenant or you are the tenant about to rent or lease property from a landlord, a rental or lease agreement is a crucial document that should be utilized. This document outlines the important terms of the rental or lease of residential property and protects the interests of both the landlord and tenant. If you want to know more, then read on.
 
WHAT IS A RENTAL OR LEASE AGREEMENT?
 
This is a legal document entered into by both a landlord and a tenant before the rental or lease begins. The landlord rents or leases the property to the tenant in exchange for rent paid to the landlord. In a rental agreement, the length of the rental period is generally month-to-month and is shorter in duration than a lease agreement. In a lease agreement, the length of the lease period varies but is generally 12 months or so and longer in duration than a rental agreement. The agreement formally lays out the terms and conditions of the rental or lease and describes the rights and responsibilities of both parties in relation to the rental or lease of the property. The document protects both the landlord and the tenant and both parties should keep a signed copy of the agreement, which can be referred back to in case of any issues or disputes relating to the property.
 
WHAT IS TYPICALLY INCLUDED?
 
Your document should clearly set out all of the terms and conditions associated with the rental or lease of the property. Rental and lease agreements typically include the following:
·         Details of both the landlord and the tenant. 
·         Location of the residential property and description of any items that are included or excluded from the rental or lease. 
·         Length of the rental or lease period. 
·         Amount, frequency and the method of payment of the rent. 
·         Procedures on collection and late charges, if any, if the rent is not paid on time. 
·         Details of any security deposit that the tenant must pay to the landlord. 
·         Insurance requirements for either the landlord or tenant.
·         Details about additional charges which the tenant may be responsible for during or after the end of the tenancy. 
·         Details about who is responsible for payment of utilities (e.g. electricity, gas and water). 
·         Details regarding the property in the event of a fire or other disaster. 
 
·         Large Details on the landlord’s right of entry and access to the property.
·         Maintenance and repairs of the property.
 
Depending on the discussions between the landlord and the tenant, other items may be included in the agreement, such as specific rules and regulations regarding guests, pets or smoking or procedures for renewal. While a landlord may want to use a standard agreement with a new tenant, if the tenant and landlord have verbally agreed upon certain items prior to the rental or lease, the tenant should ask for these additional provisions to be included in the agreement.
 
WHAT CANNOT BE INCLUDED?
 
The rental or lease agreement itself cannot violate nor require either party to violate any local, state or federal law. Legislation is in place to protect the rights of both landlords and tenants and the agreement cannot remove any of these basic rights even if either party agrees to it. An agreement should be entered into willingly by both parities without any coercion. For the agreement to be valid, it must be dated and signed by both the landlord and tenant. If the property is rented or leased to more than one tenant or rented or leased to joint tenants, the signature of all named tenants must be obtained on the agreement.
 
WHAT CAN A RENTAL OR LEASE AGREEMENT BE USED FOR?
 
These agreements can be used to formalize the rental or lease terms for most types of residential property to a tenant, including, houses, house boats, duplexes, lofts, apartments, rooms in larger properties, townhouses, studios, basement suites, or other such living spaces.
 
WHEN SHOULD A RENTAL OR LEASE AGREEMENT BE USED?
 
An agreement should be used every time a residential property is rented or leased to a tenant. A residential rental or lease agreement should not be used when a property is rented or leased for commercial purposes and/or the property is to be used only for commercial purposes. The agreement should be created and signed before a tenant has moved into a residential property.
 
ALTERNATE NAMES 
 
A rental or lease agreement may also be known as: Tenancy Agreement, Rental or Lease Contract, Rental or Lease Form.
Form: Lease Agreement (Rev. 05-2015)

'''


def test_lease_doc_detection():
    """
    Tests lease document detector on a totally new lease agreement template downloaded from Internet which
    did not participate in the original dataset on which the model was tested/trained.
    TODO: Add more data when this code moves to core project.
    :return:
    """
    detector = LeaseDocDetector()

    is_lease = detector.is_lease_document(LEASE_AGREEMENT_1)
    assert_equal(True, is_lease)
