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

import datetime
from typing import List, Dict, Tuple

from lexnlp.nlp.en.segments.sentences import get_sentence_list
from nose.tools import assert_equal, assert_dict_equal, assert_true, assert_list_equal

from apps.lease.parsing.lease_doc_properties_locator import detect_fields, detect_address_default, \
    find_numbers
from apps.lease.parsing.lease_doc_properties_locator import find_landlord_tenant

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2018, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.2.1/LICENSE"
__version__ = "1.2.1"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"

EXAMPLE_1 = '''
<PAGE>   1

                                                                   EXHIBIT 10.22


                                 LEASE AGREEMENT

                                     BETWEEN

                               KRAMER 34 HP, LTD.

                                  as Landlord,

                                       and

                        IXC COMMUNICATIONS SERVICES, INC.

                                   as Tenant,

                              Covering the Building
                            known (or to be known) as

                                    Kramer 2

                                   Located at

                       -----------------------------------

                                  Austin, Texas

'''

EXAMPLE_2 = '''
      Exhibit 10.44

                                                       English Translation

                                           Contract No.: TU201004202355IOC

                               Lease Contract

                                     for

                 North America International Business Center

                                   between

      Beijing Jindi Jiaye Real Estate Brokering Co., Ltd. (Lessor)

                                     And

      Quan Toodou Network Science and Technology Co., Ltd. (Lessee)


                                      1
   _______________________________________________________________________


                            House Lease Contract

                                   between

   Beijing Jindi Jiaye Real Estate Brokering Co., Ltd. (Lessor,
   hereinafter referred to as Party A)

                                     And

   Quan Toodou Network Science and Technology Co., Ltd. (Lessee,
   hereinafter referred to as Party B)

   This Contract is made by and between Party A and Party B through
   friendly negotiation on Party B leasing from Party A the North America
   International Business Center (hereinafter referred to as the Center)
   in accordance with the Contract Law of the Peoples Republic of China
   and relevant laws and regulations.

                  Article 1 Definitions and Interpretations

   Unless expressly required to have other interpretation by the context,
   the following terms used herein shall have the following meanings:

'''

EXAMPLE_3 = '''
 LEASE CONTRACT FOR FACTORY DORMITORY

   Lessor (hereinafter referred to as Party A): Anbao District Fuyong town
   Qiaotou Economic development Corporation
   Lessee (hereinafter referred to as Party B): Junning Ma

   In order to introduce foreign capital, develop township economy, and
   increase the income, base on the principle of mutual benefit and
   reciprocity and collaborative development,  Party A and Party B have
   reached an agreement through friendly consultation to conclude the
   following contract for factory, dormitory and dining hall.
'''

EXAMPLE_4 = '''

 Exhibit 10.1  
 LEASE    BY AND
BETWEEN    TRUSTEES OF LEXINGTON OFFICE REALTY TRUST  
 LANDLORD    AND
   CURIS, INC.  
 TENANT    4 MAGUIRE
ROAD    LEXINGTON, MASSACHUSETTS  
 
 
 LEASE  
 4 Maguire Road  
 Lexington, Massachusetts  
 ARTICLE 1  
 Reference Data  
 1.1  Introduction and Subjects Referred To .  
 This is a lease (this  Lease ) entered into by and between Trustees of Lexington Office Realty Trust, under Declaration
of Trust dated December 22, 2008 and filed with Middlesex County Registry District of the Land Court as Document No. 1488947 ( Landlord ) and Curis, Inc., a Delaware corporation ( Tenant ).  
 Each reference in this Lease to any of the following terms or phrases shall be construed to incorporate the corresponding definition
stated in this Section 1.1.      
'''


def test_find_landlord_tenant():
    landlord, tenant = find_landlord_tenant(EXAMPLE_1)
    print('Landlord: {0}'.format(landlord))
    print('Tenant: {0}'.format(tenant))

    assert_equal('HP LTD', landlord)
    assert_equal('IXC COMMUNICATIONS SERVICES INC', tenant)


def _test_field_extraction(test_data: List[Tuple[str, Dict]], detector_groups: Tuple = None):
    for text, expected in test_data:
        sentences = get_sentence_list(text)
        actual = detect_fields(sentences, groups=detector_groups)

        assert_dict_equal(actual, expected, msg='Text:\n{0}'.format(text))
        print(actual)


TERM_TEST_DATA = [
    ('''
    (g) 

Commencement Date: August 1, 2013. 




(h) 

Lease Term: Six (6) years.




(i) 

Security Deposit: $34,970.00.
    ''',
     {
         'term': ('year', 6, 365 * 6)}
     ),
    ('''
    (f) Intentionally
Omitted 
  
 (g) Target Commencement Date: 07/01/2004. 

 
 (h) Lease Term: Seven (7) years. 
  
    ''',
     # TODO Fix get_dates() to recognize date here
     {
         'term': ('year', 7.0, 7 * 365)}
     ),
    ('''
    
          l.06
  "Term":
A period of 36 months. Subject to
Section 3, the Term shall commence on February
1, 2004 (the "Commencement Date")
and, unless terminated early in accordance with this Lease end on January 31, 2007 (the "Termination Date").

    ''',
     {'commencement_date': datetime.date(2004, 2, 1),
      'term': ('month', 36.0, 36 * 30),
      'expiration_date': datetime.date(2007, 1, 31)}
     ),
    ('''
    (b) The Lease term shall be seventy two (72) months, beginning
on the later of (i) sixty (60) days after substantial completion of the Shell
Improvements (as defined on Exhibit B) or (ii) August 1, 1999 (the "COMMENCEMENT
DATE"), and ending July 31, 2005 (the "TERM", which defined term shall include
all renewals and extensions of the Term, if any). Notwithstanding the foregoing
if the Commencement Date does not occur on August 1, 1999, then the Term shall
end seventy-two (72) months after the first day of the first full calendar month
after the Commencement Date.
    ''', {'commencement_date': datetime.date(1999, 8, 1),
          'term': ('month', 72.0, 2160.0),
          'expiration_date': datetime.date(2005, 7, 31)}),
    ('''
    To have and to hold for a period of fifteen (15) and a fraction years ("the Term" or "the Original Term") 
    commencing on December 15, 2000 (being hereafter referred to as "the Commencement Date") and, unless sooner
     terminated as provided herein, ending on December 31, 2015.
    ''',
     {'commencement_date': datetime.date(2000, 12, 15),
      'expiration_date': datetime.date(2015, 12, 31)}
     ),
    ('''
    Project:                 Northwest Pointe Business Centre
                             2155 Niagara Lane North
                         Plymouth, Minnesota 55447-4699

Term:                    From 12:01 a.m. on March 1, 1999 (the "Commencement Date")
                         through 1l:59 p.m. on November 30, 2002 (the "Expiration Date")

Annual Minimum Rent
Payable by Tenant for
    ''',
     # TODO Make get_dates recognizing dates here
     {}),
    ('''
        THIS LEASE is dated the 13th day of June, 1997.
        2.2.     TERM
    
        The Term of this lease is 8 years  commencing  on July 1, 1997 and  expiring  on
        June 30, 2005.
    
    ''',
     {'commencement_date': datetime.date(1997, 7, 1),
      'expiration_date': datetime.date(2005, 6, 30),
      'term': ('year', 8.0, 365 * 8)}),
    ('''
    LEASE 
  
 OF 
  
 PART 4TH FLOOR, EUSTON HOUSE,

 24 EVERSHOLT STREET, LONDON NW1 
  
							
	 	 	TERM:	  	:	    	10 Years
	 	 	FROM	  	:	    	27 April 2005
	 	 	BASIC RENT	  	:	    	 PS181,521 Basic Rent
 Amount (subject
to review)

 Contents 
					
	Clause

	  	Page
    ''', {'commencement_date': datetime.date(2005, 4, 27), 'term': ('year', 10.0, 3650.0)}),
    ('''
    Lessor:                      475 Java Drive Associates, L.P.,
                                   a California Limited Partnership

Address of Lessor:           c/o The Mozart Development Company

                                   1068 East Meadow Circle
                                   Palo Alto, CA 94303

Lessee:                      NETWORK APPLIANCE, INC.,
                                   a Delaware Corporation

Address of Lessee:           2770 San Tomas Expressway
                                   Santa Clara, California 95051

Commencement Date (Article 5):  October 1, 1999

Term (Article 5):  25 years

Use (Article 11): Lessee may use the Premises for general office, administration
and research and development (including a cafeteria for its employees).

<PAGE>   3
    ''',
     {'commencement_date': datetime.date(1999, 10, 1), 'term': ('year', 25.0, 365 * 25)}),
    ('''
    Except as provided in Paragraph 42, Landlord shall not be
required to make any alterations, additions or improvements to the Premises and
the Premises shall be leased to Tenant in an "as-is" condition.

         3. Term. The term of this Lease ("Lease Term") shall be for five (5)
years, commencing on September 1, 1996 (the "Commencement Date") and ending on
August 31, 2001 unless sooner terminated pursuant to any provision hereof.
Notwithstanding said scheduled Commencement Date, if for any reason Landlord
cannot deliver possession of the Premises to Tenant
    ''',
     {'commencement_date': datetime.date(1996, 9, 1),
      'expiration_date': datetime.date(2001, 8, 31),
      'term': ('year', 5.0, 365 * 5)}),
    ('''
    3.   TERM.
     ----         

     (a)   The initial term (the "Initial Term") of this Lease and Lessee's
           obligation to pay rent shall commence as of January 15, 1998 (the
           "Commencement Date").

     (b)   The Initial Term of this Lease shall end at midnight on January 14,
           2008, unless sooner terminated or extended as hereinafter provided.
    ''',
     {'commencement_date': datetime.date(1998, 1, 15),
      'expiration_date': datetime.date(2008, 1, 14)})
]

LEASE_TYPE_TEST_DATA = [
    ('''
    Tenant shall also pay, monthly in advance, "Additional Rent" consisting of
all taxes, assessments, charges, utility costs, insurance premiums, repair costs
and expenditures of Landlord as set forth in Articles 4, 5, 6, 7, 13 and 17, or
in any other part of this Lease.  In the event of Tenant's default in payment,
Landlord shall have (in addition to any remedies granted Landlord hereunder for
Fixed Rent) all legal, equitable or other remedies provided by law for non-
payment of rent.
    ''', {'pay_taxes': True, 'pay_costs': True, 'pay_insurance': True}),
    ('''
    Tenant covenants and agrees to pay promptly, when due, all personal property taxes or other
taxes and assessments levied and assessed by any governmental authority upon the removable property
of Tenant in, upon or about the Property.''', {'pay_taxes': True}),
    ('''
    Tenant
shall procure, pay for and maintain, comprehensive public liability insurance, indemnifying both Landlord and Tenant from any
loss or damage occasioned by an accident or casualty, about or adjacent to the leased premises, which policy shall be written
on an "occurrence" basis, with limits of no less than One Hundred Thousand Dollars ($100,000.00) / Three Hundred Thousand
Dollars ($300,000.00) for bodily injury and Fifty Thousand Dollars ($50,000.00) property damage insurance. Tenant shall also in
addition procure, pay for, and maintain Renter's Insurance Policy indemnifying Landlord from any loss or damage occasioned to
the Tenant's personal properties including damages arising from plumbing, heating, electrical and roof malfunctions and/or leaks.
Certificate of such insurance shall be furnished to Landlord and shall provide that said coverage should not be changed, modified,
reduced or canceled without thirty (30) days prior written notice thereof being given to Landlord. The Landlord shall be responsible
for, and shall have in effect at all times, fire, extended coverage, and vandalism and malicious mischief insurance in an amount
not less than 80% of the replacement value of the building on the demised premises. Certificates of insurance will be furnished
Tenant upon request thereof.
    ''', {'pay_insurance': True})

]

PROPERTY_TYPE_TEST_DATA = [
    ('''
    g.
Permitted Use. The Premises shall be used only for lawful production and sale of cannabis and other related products
and for no other purpose without the prior written consent of Landlord (the "Permitted Use").

    ''', {'property_types__set': {'retail'}})
]

PERMITTED_USE_TEST_DATA = [
    ('''
    Rentable Square Feet:                    2,729
Use (Article 6):                         General and Executive Offices
Term (Article 2)                         Thirty-six (36) months''',
     {'permitted_use': 'General and Executive Offices '
                       'Term (Article 2) Thirty-six (36) months'}),
    ('''
    (k) Permitted Use: cutting, storage, and sales of silicon carbide products,
and office and administrative uses reasonably ancillary thereto.
    ''', {'permitted_use': 'cutting, storage, and sales of silicon carbide products, and '
                           'office and administrative uses reasonably ancillary thereto.'}),
    ('''
    g.
Permitted Use. The Premises shall be used only for lawful production and sale of cannabis and other related products
and for no other purpose without the prior written consent of Landlord (the "Permitted Use").

    ''', {'permitted_use': 'The Premises shall be used only for lawful production and sale of '
                           'cannabis and '
                           'other related products and for no other purpose without the prior written consent '
                           'of Landlord (the "Permitted Use").'}),
    ('''
         6.      Permitted Use. Retreat and
entertainment facility for employees, directors, guests and

invitees of Tenant and their family members.
    ''', {'permitted_use': 'Retreat and entertainment facility for employees, directors, '
                           'guests and invitees of Tenant and their family members.'})
]

PROHIBITED_USE_TEST_DATA = [
    ('''
   Tenant shall not be obligated to pay Base Rent or additional rent under this Lease for any period of time that 
   Tenant occupies the Premises prior to the Rent Commencement Date. 
   ''', {}),
    ('''
     Tenant shall not store any goods or merchandise in or use the Property for any purpose which will in any way
      impair or violate the
requirements of any policies of insurance on the Property. Tenant and its use of the Property will comply with all
 statutes, ordinances, rules, orders, regulations and requirements of all federal, state, city and local governments, 
 and with all
rules, orders and regulations of the applicable board of fire underwriters which affect the use of the Property.
''',
     {'prohibited_use__list': [
         'Tenant shall not store any goods or merchandise in or use the Property for any purpose which '
         'will in any way impair or violate the requirements of any policies of insurance on the '
         'Property.']}),
    ('''
    (m)     Lessee shall not Manage or authorize the Management of, any Hazardous Materials on the Premises without
     prior written disclosure to and prior written approval by
Lessor, except in such quantities as are necessary for the ordinary conduct of Lessee's operations.



                (n)     Lessee shall not take any action that would subject the Premises to additional Permit 
                requirements under RCR
A for treatment, storage or disposal of Hazardous Wastes
without prior written disclosure to and prior written approval by Lessor.



                (o)     Lessee shall not dispose of Hazardous Wastes in dumpsters provided by Lessor for Lessee's use 
                without prior written disclosure to and prior written approval by
Lessor.

    ''', {'prohibited_use__list':
        [
            '(m) Lessee shall not Manage or authorize the Management of, any Hazardous Materials on '
            'the Premises without prior written disclosure to and prior written approval by Lessor, '
            'except in such quantities as are necessary for the ordinary conduct of Lessee\'s '
            'operations.',
            '(n) Lessee shall not take any action that would subject the Premises to additional '
            'Permit requirements under RCR A for treatment, storage or disposal of Hazardous Wastes '
            'without prior written disclosure to and prior written approval by Lessor.'
        ]})
]

NON_RENEW_NOTICE_TEST_DATA = [
    ('''That, with consent of Landlord, this lease can continue on a month-to-month basis, but shall be terminated 
    when either Landlord or T
enant provides the other with Ninety (90) days written notice.''',
     {'renew_non_renew_notice': ('day', 90.0, 90),
      'auto_renew': True}),
    ('''The Lessee has an
      option to extend the Term for an additional period of six months , on the
      terms and conditions hereof. The exercise of the option will be by way of
      sending the Lessor a written notice of the Lessee's intention to extend
      the Term as above, no later than three (3) months prior to the expiration
      of the Term.''', {'auto_renew': False, 'renew_non_renew_notice': ('month', 3.0, 90)}),
    ('''3.2.   Having this Agreement ended, the Lessee who orderly fulfilled the undertaken obligations hereunder shall have the priority wi
th respect to other persons to renew this Agreement in accordance with the procedure set forth in Paragraph 3.3 hereof.
3.3. If having this Agreement ended the Lessor intends to further lease the Premises, the Lessor must notify the Lessee in writing o
f that in advance, but no later than 3 (three) months prior to the end of the lease term by specifying the Premises lease term and t
he fee as well as other substantial terms and conditions of lease. In this case the Lessee must furnish a written reply to the Lesso
r no later than within 1 (one) month as form receipt of notice of the Lessor and state whether or not the Lessee agrees to renew thi
s Agreement under the terms and conditions specified in the notice of the Lessor. If the Lessee agrees to enter into the Premises le
ase agreement under the terms and conditions specified in the notice of the Lessor, the Parties shall agree to take all the actions
under their control in order the new Premises leases agreement to be signed as soon as possible.
''', {'auto_renew': False, 'renew_non_renew_notice': ('month', 3.0, 90)}),
    (''' It is agreed and understood  that Tenant,  if not in default and if open and
operating,  shall  have  the  right  to  extend  this  Lease  Agreement  for one
additional  period of five (5) years at the base

<PAGE>

rental of $4.41 per square foot for the additional  term.. If Tenant shall elect
to extend,  Tenant  shall give to Landlord  not less than  twelve  (12)  months'
written  notice  prior to the  expiration  of the  original  term of this  Lease
Agreement.
''', {'auto_renew': False, 'renew_non_renew_notice': ('month', 12.0, 360)}),
    ('''4. RENEWAL OPTION. Provided and upon the condition that Lessee shall not then be in default under the terms of this Lease beyond an
y applicable grace or cure period, Lessee shall have the right to renew this Lease for
a total of three (3) additional terms of five (5) years each. Lessee shall give notice in writing to Lessor by certified mail at lea
st thirty (30) days prior to the end of the original term or the current five year renewal term of its intention not
to exercise its option to renew this Lease. Otherwise, the Lease shall automatically renew for the next term available. The terms of
 the lease shall remain in effect during each successive five year renewal term except that monthly rental amounts
may be adjusted by the aggregate increase in the Chained Consumer Price Index for all Urban Consumers Index (C-CPI-U as published by
 the U.S. Bureau of Labor Statistics) experienced since the beginning of the immediately preceding renewal term, or
in the case of the original term, since the date of the occupancy of the subject property. After the passage of 5 years, in any even
t, however, increases in the monthly rental amount for the initial renewal term shall not exceed 118% of the monthly
rental amount of the 5 year original term, and increases in monthly rental amounts of the subsequent renewal terms shall not exceed
115% of the immediately preceding renewal term. The parties understand and agree that this paragraph grants Lessee
three (3) separate options to renew this Lease Agreement for successive three (3) renewal terms provided the requisite notice is
''', {'auto_renew': True, 'renew_non_renew_notice': ('day', 30.0, 30)}),
    ('''Upon
full and complete performance of all the terms, covenants, and conditions herein contained by Tenant and payment of all rental
due under the terms hereof, Tenant shall be given the option to renew this Lease for an additional term of N/A. In
the event the Tenant desires to exercise said option Tenant shall give written notice of such fact to Landlord not less that sixty
(60) days prior to the expiration of the then current term of the Lease. In the event of such exercise this Lease Agreement shall
be deemed to be extended for the additional period; provided, however, Landlord shall have the right to increase the basic monthly
rental by an amount to be negotiated at the time.''', {'auto_renew': False,
                                                       'renew_non_renew_notice': (
                                                           'day', 60.0, 60)}),
    (''' 2.      Notice.
                                         To extend the Lease, Tenant must deliver written notice to Landlord not less than
                                         one hundred twenty (120) days prior to the expiration of the then-current Lease term.
                                         Time is of the essence of this Rider.
''', {'auto_renew': False, 'renew_non_renew_notice': ('day', 120.0, 120)}),
    ('''
    50.           Option
to Extend. Lessee shall reserve the right to extend the Lease for two (2)
extension terms of one (1) year each at the same terms and conditions including
annual rental increases. Leesee shall provide ninety (90) days written notice
should It elect to exercise the option(s).
''', {'renew_non_renew_notice': ('day', 90.0, 90), 'auto_renew': False})
]

ADDRESSES_TEST_DATA = [
    ('''Any notice, consent or other communication required or
permitted under this Lease shall be in writing and shall be delivered by hand,
sent by air courier, sent by prepaid registered or certified mail with return
receipt requested, or sent by facsimile, and shall be deemed to have been given
on the earliest of (i) receipt, (ii) one business day after delivery to an air
courier for overnight expedited delivery service, or (iii) five (5) business
days after the date deposited in the United States mail, registered or
certified, with postage prepaid and return receipt requested (provided that such
return receipt must indicate receipt at the address specified) or on the day of
its transmission by facsimile if transmitted during the business hours of the
place

<PAGE>   31

of receipt, otherwise on the next business day. All notices shall be addressed
as appropriate to the following addresses (or to such other or further addresses
as the parties may designate by notice given in accordance with this section):

If to Lessor:

                  475 Java Drive Associates, L.P.
            c/o The Mozart Development Company
                  1068 East Meadow Circle
                  Palo Alto, CA  94303
                  
                  Tel.:  (   )    -

If to Lessee:

                  Network Appliance Inc.
                  2770 San Tomas Expressway
                  Santa Clara, California 95051
                  Attn:  Chris Carlton
                  Tel. (408) 367-3200
''', None),
    ('''









<PAGE>   1
                                                                   EXHIBIT 10.16


                                  LEASE BETWEEN

                        475 Java Drive Associates, L.P.,
                        a California Limited Partnership

                                   ("LESSOR")

                                       AND

                            NETWORK APPLIANCE, INC.,
                             a Delaware Corporation

                                   ("LESSEE")


                                                                   June 11, 1998


<PAGE>   2

                                      LEASE

                  THIS LEASE is made and entered into as of June 11, 1998, by
and between 475 Java Drive Associates, L.P., a California Limited Partnership
("Lessor") and Network Appliance, Inc., a Delaware Corporation ("Lessee").

                                    RECITALS

                  A. Lessor owns that certain real property located in the City
of Sunnyvale, County of Santa Clara, State of California, and more particularly
described in Exhibit A attached hereto. The land described in Exhibit A together
with the Improvements (as defined below) thereon, is herein referred to as the
"Premises."

                  B. Lessee desires to lease the Premises from Lessor, and
Lessor has agreed to lease the Premises to Lessee on the terms and conditions
set forth in this Lease and for the purposes provided herein.

                  NOW, THEREFORE, in consideration of the rents to be paid
hereunder and of the agreements, covenants and conditions contained herein, the
parties hereby agree as follows:

ARTICLE 1. BASIC LEASE INFORMATION

                  The following is a summary of basic lease information. Each
term or item in this Article 1 shall be deemed to incorporate all of the
provisions set forth below pertaining to such term or item and to the extent
there is any conflict between the provisions of this Article 1 and any more
specific provision of this Lease, the more specific provision shall control.

Lessor:                      475 Java Drive Associates, L.P.,
                                   a California Limited Partnership

Address of Lessor:           c/o The Mozart Development Company

                                   1068 East Meadow Circle
                                   Palo Alto, CA 94303

Lessee:                      NETWORK APPLIANCE, INC.,
                                   a Delaware Corporation

Address of Lessee:           2770 San Tomas Expressway
                                   Santa Clara, California 95051

Commencement Date (Article 5):  October 1, 1999

Term (Article 5):  25 years

Use (Article 11): Lessee may use the Premises for general office, administration
and research and development (including a cafeteria for its employees).

<PAGE>   3

Base Monthly Rental as of Commencement Date (Article 7): Two Hundred Fifty Seven
Thousand Dollars ($257,000) per month.


Use (Article 11): Office, administration, research, development, light
manufacturing and industrial operations, and/or any lawful purpose

ARTICLE 2. DEFINITIONS

                  As used in this Lease, the following terms shall have the
following meanings, applicable, as appropriate, to both the singular and plural
forms of the terms herein defined:

                  "Additional Rental" is as defined in Article 8.

                  "Affiliate" means (i) the legal representative, successor or
assignee of, or any trustee of a trust for the benefit of, Lessee; (ii) any
entity of which a majority of the voting or economic interest is owned by Lessee
or one or more of the persons referred to in the preceding clause; (iii) any
partnership in which Lessee or a person referred to in the preceding clauses is
a partner; (iv) any person who is an officer, director, trustee, stockholder
(10% or more) or partner of Lessee or any person referred to in the preceding
clauses; or (v) any person directly or indirectly controlling, or under direct
or indirect common control with, any person referred to in any of the preceding
clauses. For purposes of this definition, "control" means owning directly or
indirectly ten percent (10%) or more of the beneficial interest in such entity
or the direct or indirect power to control the management policies of such
person or entity, whether through ownership, by contract or otherwise.

                  "Alterations" means any additional improvements, alterations,
remodeling, demolition, or reconstruction of or to the Initial Improvements or
construction of improvements different than the Initial Improvements after the
completion of the initial construction of the Initial Improvements.

                  "Applicable Laws" means all applicable covenants, conditions
and restrictions recorded against and applicable to the Premises and all
applicable laws, codes, ordinances, orders, rules, regulations and requirements,
including, without limitation, all Environmental Requirements, of all Federal,
state, county, municipal and other governmental authorities and the departments,
commissions, boards, bureaus, instrumentalities, and officers thereof, and all
orders, rules and regulations of the Pacific Fire Rating Bureau, and the
American Insurance Association (formerly the National Board of Fire
Underwriters) or any other body exercising similar functions relating to or
affecting the Premises, the Improvements now or hereafter located on the
Premises or the use, operation or occupancy of the Premises for the purposes
permitted hereunder, whether now existing or hereafter enacted.

                  "Appropriation" means any taking by exercise of right of
condemnation (direct or inverse) or eminent domain, or requisitioning by
military or other public authority for any purpose arising out of a temporary
emergency or other temporary circumstance or sale under threat of condemnation.
"Appropriated" means having been subject to such taking and "Appropriating"
means exercising such taking authority.


<PAGE>   4

                  "Award" means the amount paid by the Appropriating authority
as a result of an Appropriation.

                  "Base Monthly Rental" means the amount stated in the Basic
Lease Information, payable in accordance with Article 7.

                  "Basic Lease Information" means the information contained in
Article 1.

                  "Bonded Contracts" is as defined in Section 13.5(b).

                  "City" means the City of Sunnyvale.

                  "Commencement Date" is as stated in the Basic Lease
Information.

                  "CPI" means the Consumer Price Index published by the U.S.
Department of Labor, Bureau of Labor Statistics (San Francisco-Oakland Bay Area,
All Urban Consumers, All Items), or if such index is no longer published, a
successor or substitute index designated by Lessor, published by a governmental
agency and reflecting changes in consumer prices in the San Francisco Bay Area.

                  "Environmental Audit" is as defined in Section 20.5.

                  "Environmental Claims" means all claims, demands, judgments,
damages, penalties, fines, liabilities (including strict liability),
encumbrances, liens, costs, and expenses of investigation and defense of any
claim, including, without limitation, reasonable attorneys' fees and
disbursements and consultants' fees, any of which are incurred at any time as a
result of a Hazardous Substance Occurrence, including, without limitation:

                  (i) Claims for personal injury, or injury to property or
natural resources occurring upon or off of the Premises;

                  (ii) Fees incurred for the services of attorneys, consultants,
contractors, experts, laboratories and all other costs incurred in connection
with the investigation or remediation of Hazardous Substances or violation of
Environmental Requirements, including, but not limited to, preparation of
feasibility studies or reports, or the performance of any cleanup, remediation,
removal, response, abatement, containment, closure, restoration or monitoring
work required by any federal, state or local governmental agency or political
subdivision, or reasonably necessary to make full economic use of the Premises
or any other property or otherwise expended in connection with such conditions,
and including without limitation any attorneys' fees, costs and expenses
incurred in enforcing this Lease or collecting any sums due hereunder; and

                  (iii) Liability to any third person or governmental agency to
indemnify such person or agency for costs expended in connection with the items
referenced in subsection (ii) above.

                  "Environmental Requirements" means all applicable present and
future statutes, regulations, rules, ordinances, codes, licenses, permits,
orders, approvals, plans, authorizations, 


<PAGE>   5

concessions, franchises, and similar items, and all amendments thereto, of all
governmental agencies, departments, commissions, boards, bureaus or
instrumentalities of the United States, California, and political subdivisions
thereof, and all applicable judicial, administrative and regulatory decrees,
judgments, and orders relating to the protection of human health or the
environment, including, without limitation, the Comprehensive Environmental
Response, Compensation and Liability Act (42 U.S.C. section 9601 et seq.) and
the Resource Conservation and Recovery Act (42 U.S.C. section 6901 et seq.) and
including, without limitation: (i) all requirements pertaining to reporting,
licensing, permitting, investigation and remediation of emissions, discharges,
releases, or threatened releases of Hazardous Substances, whether solid, liquid,
or gaseous in nature, into the air, surface water, groundwater, or land, or
relating to the manufacture, processing, distribution, use, treatment, storage,
disposal, transport, or handling of Hazardous Substances, and (ii) all
requirements pertaining to the health and safety of employees or the public.

                  "Expiration Date" is as stated in the Basic Lease Information.

                  "Event of Default" is as defined in Article 28.

                  "Full Insurable Replacement Value" is as defined in Section
21.1.

         "Hazardous Substance" means any substance:

                  (i) the presence of which requires investigation or
remediation under any Environmental Requirement;

                  (ii) which is or becomes defined as a "hazardous waste,"
"hazardous substance," "pollutant," or "contaminant" under any Environmental
Requirement;

                  (iii) which is toxic, explosive, corrosive, flammable,
infectious, radioactive, carcinogenic, mutagenic, or otherwise hazardous and is
or becomes regulated under any Environmental Requirement;

                  (iv) the presence of which on the Premises causes or threatens
to cause a nuisance upon the Premises or to surrounding properties or poses or
threatens to pose a hazard to the health or safety of persons on or about the
Premises;

                  (v) the presence of which on adjacent properties could
constitute a trespass by Lessee;

                  (vi) without limitation of the foregoing, which contains
gasoline, diesel fuel or other petroleum hydrocarbons;

                  (vii) without limitation of the foregoing, which contains
polychlorinated biphenals (PCBs), asbestos or urea formaldehyde foam insulation;
or

                  (viii) without limitation of the foregoing, radon gas.


<PAGE>   6

                  "Hazardous Substance Occurrence" means any use, treatment,
keeping, storage, sale, release, disposal, migration or discharge of any
Hazardous Substance from, on, about, under or into the Premises, or the
exacerbation through the acts of Lessee or its subtenants of any previously
existing Hazardous Substance condition, that occurs during the, excluding any
Hazardous Substance Occurrence caused by Lessor or its Affiliates or originating
on property owned by Lessor or its Affiliates.

         "Impositions" is as defined in Section 8.1.

                  "Improvements" means all landscaping, buildings and other
structures and improvements, and fixtures thereto, constructed, planted, or
installed on the Premises, including, without limitation, the Initial
Improvements to be constructed by Lessee in accordance herewith and all
subsequent Alterations.

                  "Initial Improvements" means the initial improvements
constructed by Lessee.

                  "Interest Rate" means the lesser of (i) the rate of interest
charged by Bank of America at its offices in San Francisco as its prime or
reference rate, plus 2%, or (ii) the highest rate permitted under Applicable
Laws, compounded monthly.

                  "Lease Year" shall mean each successive twelve month period
commencing on October 1 and ending on September 30.

                  "Leasehold Mortgage" is as defined in Article 26.

         "Premises" is as defined in Recital A.

                  "Supplemental Audit" is as defined in Section 20.5.

         "Term" is as defined in Article 5.

                  "Termination Date" shall mean the Expiration Date or such
earlier date as this Lease is terminated pursuant to any provision hereof.

         "Transfer" is as defined in Section 24.1.

ARTICLE 3. LEASE OF PREMISES; RESERVATION OF RIGHTS

                  Lessor hereby leases and demises to Lessee, and Lessee hereby
 hires from Lessor, the Premises;

                  Subject to all zoning and governmental regulations now or
hereafter in effect, and all liens, encumbrances, restrictions, rights and
conditions of law or of record or otherwise known to Lessee or ascertainable by
inspection or a survey; and


<PAGE>   7

ARTICLE 4. DEMOLITION; NO OTHER ALTERATION BY LESSOR; ACCEPTANCE OF PREMISES

         Section 4.1 Lessor's Obligation To Demolish Existing Building. Prior to
the Commencement Date, Lessor shall cause the existing improvement to be
demolished and removed from the Premise in accordance with the specifications
described on EXHIBIT B attached hereto and incorporated herein by reference.
Lessor shall indemnify, defend and hold Lessee harmless from and against any
cost, claim, loss or liability directly or indirectly in connection with such
demolition. Lessor shall take no action which alters the physical condition of
the Premises except for the demolition described in the preceding sentence.

         Section 4.2 Lessee's Due Diligence. Prior to entering into this Lease,
Lessee has made a thorough, independent examination of the Premises and all
matters relevant to Lessee's decision to enter into this Lease, and Lessee is
thoroughly familiar with all aspects of the Premises and is satisfied that they
are in an acceptable condition and meet Lessee's needs. Without in any way
limiting the generality of the foregoing, Lessee's inspection and review has
included, to the extent that Lessee in its sole discretion has deemed necessary
or appropriate:

                  (a) All matters relating to title, together with all municipal
and other legal requirements such as taxes, assessments, zoning, use permit
requirements and building codes;

                  (b) The physical condition of the Premises, including the
soils and groundwater and the presence or absence of Hazardous Substances on,
under or in the vicinity of the Premises and all other physical and functional
aspects of the Premises;

                  (c) All easements and access rights;

                  (d) Lessee's ability to obtain appropriate licenses and
satisfy all licensing requirements under Applicable Laws;

                  (e) The economics of the business Lessee intends to conduct on
the Premises, including without limitation, market conditions and financial
viability; and

                  (f) Lessee's ability to finance the construction of the
Improvements.


<PAGE>   8

Section 4.3 Acceptance of the Premises. Subject to the obligations of Lessor
pursuant to Section 4.1, Lessee specifically agrees to take the Premises in its
condition as of the Commencement Date and acknowledges that in entering into
this Lease, Lessee does not rely on, and Lessor does not make, any express or
implied representations or warranties as to any matters including, without
limitation, the suitability of the soil or subsoil, any characteristics of the
Premises or improvements thereon, the suitability of the Premises for the
intended use, the economic feasibility of the business Lessee intends to conduct
on the Premises, title to the Premises, Hazardous Substances on or in the
vicinity of the Premises, or any other matter. Lessee has satisfied itself as to
such suitability and other pertinent matters by Lessee's own inquiries and tests
into all matters relevant in determining whether to enter into this Lease.
Subject to the obligations of Lessor pursuant to Section 4.1, Lessee accepts the
Premises in its condition as of the Commencement Date, and hereby expressly
agrees that if any remedial or restoration work is required in order to conform
the Premises to the requirements of Applicable Laws, Lessee shall assume sole
responsibility for any such work.

ARTICLE 5. TERM

                  The term of this Lease (the "Term") shall be for the period
stated in the Basic Lease Information, commencing on the Commencement Date and
expiring on the Expiration Date (subject to extension pursuant to Article 6) or
on such earlier date as this Lease may be terminated as hereinafter provided. In
the event the demolition to be completed by Lessor pursuant to Section 4.1 is
not completed as of October 1, 1999 the Commencement Date shall be extended to
the date of completion of such work.

ARTICLE 6. OPTIONS TO EXTEND TERM

         Lessee shall have no right to extend the Term.


<PAGE>   9

ARTICLE 7. BASE MONTHLY RENTAL

Section 7.1 Base Monthly Rental. Commencing upon the Commencement Date and
continuing throughout the term, Lessee shall pay to Lessor, at Lessor's address
stated in the Basic lease Information, or to such other person or at such other
place as Lessor may from time to time designate by notice to Lessee, without
prior notice or demand, Base Monthly Rental in the amount stated in the Basic
Lease Information, which amount shall be adjusted as provided below.

ARTICLE 8.        ADDITIONAL RENTAL

Section 8.1 Impositions. In addition to the Base Monthly Rental and all other
amounts and charges due hereunder, as part of the consideration for this Lease
and as additional rental hereunder, commencing October 1, 1999, Lessee covenants
and agrees to bear, discharge and pay to the relevant authority or entity, in
lawful money of the United States, without offset or deduction, as the same
become due, before delinquency, all taxes, assessments, rates, charges, license
fees, municipal liens, levies, excises or imposts, whether general or special,
or ordinary or extraordinary, of every name, nature and kind whatsoever,
including all governmental charges of whatsoever name, nature or kind that may
be levied, assessed, charged or imposed or may be or become a lien or charge
upon the Premises or any part thereof; or upon the rent or income of Lessee; or
upon the use or occupancy of the Premises; or this transaction or any document
creating or transferring an estate or interest in the Premises; upon any of the
buildings or improvements that are or are hereafter placed, built or newly
constructed upon the Premises; or upon the leasehold of Lessee or upon the
estate hereby created.

                  If at any time during the Term, under any Applicable Laws, any
tax is levied or assessed against Lessor directly, in substitution in whole or
in part for real property taxes, Lessee covenants and agrees to pay and
discharge such tax.

                  All of the foregoing taxes, assessments and other charges are
herein referred to as "Impositions."


<PAGE>   10

Section 8.2 Right to Contest. Lessee shall have the right to contest, by
appropriate proceedings, the amount or validity, in whole or in part, of any
Imposition, provided that Lessee shall not postpone or defer payment of such
Imposition but shall pay such Imposition in accordance with Section 8.1
notwithstanding such contest. Lessor shall have no obligation to join in any
such proceedings. Lessee shall indemnify and defend Lessor against and save
Lessor harmless, in accordance with Article 22 hereof, from and against any and
all claims, demands, losses, costs, liabilities, damages, penalties and
expenses, including, without limitation, reasonable attorneys' fees and
expenses, arising from or in connection with any such proceedings.

Section 8.3 Proration. Any Imposition relating to a fiscal period of any taxing
authority, only a part of which period is included within the Term, shall be
prorated as between Lessor and Lessee so that Lessor shall pay the portion
thereof attributable to any period prior to the commencement of and subsequent
to the lapse of the Term, and Lessee shall pay the portion thereof attributable
to any period during the Term. Lessee, however, shall pay all personal property
taxes, without proration, that relate to a fiscal year in which the Term hereof
shall commence or terminate.

Section 8.4 Assessment Proceedings. If at any time during the Term any
governmental authority shall undertake to create an improvement or special
assessment district the proposed boundaries of which shall include the Premises,
Lessee shall be entitled to appear in any proceeding relating thereto and to
exercise all rights of a landowner to have the Premises excluded from the
proposed improvement or special assessment district or to determine the degree
of benefit to the Premises resulting therefrom.

Section 8.5 Additional Rental. All of the above charges and all other charges
and amounts required to be paid by Lessee under this Lease shall be additional
rent ("Additional Rental"). All such Additional Rental that is payable to Lessor
shall be payable at the place where the Base Monthly Rental is payable.

ARTICLE 9. NET LEASE; NO COUNTERCLAIM OR ABATEMENT

                  The Base Monthly Rental and Additional Rental due to Lessor
hereunder shall be absolutely net to Lessor and shall be paid without assertion
of any counterclaim, setoff, deduction or defense and without abatement,
suspension, deferment or reduction. Under no circumstances or conditions,
whether now existing or hereafter arising, and whether or not beyond the present
contemplation of the parties, shall Lessor be expected or required to make any
payment of any kind whatsoever with respect to the Premises or be under any
obligation or liability hereunder except as expressly set forth in this Lease.

                  Except as otherwise expressly provided herein, this Lease
shall continue in full force and effect, and the obligations of Lessee hereunder
shall not be released, discharged or otherwise affected, by reason, of: (a) any
damage to or destruction of the Premises or any portion thereof or any
improvements thereon, or any taking thereof in eminent domain; (b) any
restriction or prevention of or interference with any use of the Premises or the
improvements or any part thereof; (c) any bankruptcy, insolvency,
reorganization, composition, adjustment, dissolution, liquidation or other
proceeding relating to Lessor, Lessee or any constituent partner 


<PAGE>   11

of Lessee or any sublessee, licensee or concessionaire or any action taken with
respect to this Lease by an trustee or receiver, or by any court, in any
proceeding; (d) any claim that Lessee or any other person has or might have
against Lessor; (e) any failure on the part of Lessor to perform or comply with
any of the terms hereof or of any other agreement with Lessee or any other
person; (f) any failure on the part of any sublessee, licensee, concessionaire,
or other person to perform or comply with any of the terms of any sublease or
other agreement between Lessee and any such person; (g) any termination of any
sublease, license or concession, whether voluntary or by operation of law; or
(h) any other occurrence whatsoever, whether similar or dissimilar to the
foregoing, in each case whether or not Lessee shall have notice or knowledge of
any of the foregoing.

                  The obligations of Lessee hereunder shall be separate and
independent covenants and agreements. Lessee hereby waives, to the full extent
permitted by applicable law, all rights now or hereafter conferred by statute,
including without limitation the provisions of Civil Code Sections 1932 and
1933, to quit, terminate or surrender this Lease or the Premises or any part
thereof, or to any abatement, suspension, deferment, diminution or reduction of
any rent hereunder.

ARTICLE 10. OPTION TO PURCHASE.

                  Lessor hereby grants to Lessee the option to purchase the
Premises pursuant to the terms and conditions of that certain Option Agreement
dated of even date herewith.

ARTICLE 11. USE OF PREMISES

                  Subject to all provisions and limitations contained herein,
the Premises and all buildings and improvements at any time located thereon
shall at all times be used and operated for the purposes stated in the Basic
Lease Information and for no other purpose. The parties hereby acknowledge and
agree that Lessee's covenant that the Premises shall be used solely for the
purposes stated in the Basic Lease Information and for no other purpose is
material consideration for Lessor's agreement to enter into this Lease. The
parties further acknowledge and agree that any violation of said covenant shall
constitute a material breach of this Lease and entitle Lessor to exercise any
and all of its rights and remedies under this Lease or otherwise at law or in
equity.

                  Without limitation of the foregoing, or any other provision of
this Lease, in no event shall the Premises be used for any purpose that in any
manner causes, creates, or results in a nuisance; any purpose or use that is of
a nature to involve substantial hazard, such as the manufacture or use of
explosives, chemicals or products that may explode, or any purpose or use that
otherwise may harm the health or welfare of persons or the physical environment;
or any discharge of Hazardous Substances on the Premises, including but not
limited to the disposing or discharging of such substances into or under the
Premises.

ARTICLE 12. LIMITATION ON EFFECT OF APPROVALS

                  Lessor shall have no obligation to review, comment upon,
approve, inspect or take any other action with respect to the Premises, the
Improvements, or the design or construction thereof, or any other matter, are
specifically for the benefit of Lessor and no other 


<PAGE>   12

party. No review, comment, approval or inspection, right or exercise of any
right to perform Lessee's obligations, or similar actions required or permitted
by, of, or to Lessor hereunder, or actions or omissions of Lessor's employees,
agents and trustees, or other circumstances shall give or be deemed to give
Lessor any liability, responsibility or obligation for, in connection with, or
with respect to, the design, construction, maintenance or operation of the
Premises or any Improvements, or the removal and/or remediation of any Hazardous
Substances on, in or from the Premises, nor shall any such approval, actions,
information or circumstances relieve or be deemed to relieve Lessee of the sole
obligation and responsibility for the design, construction, maintenance and
operation of the Premises and Improvements and the removal and/or remediation of
Hazardous Substances required under this Lease, if any.

ARTICLE 13. INITIAL CONSTRUCTION AND ALTERATIONS

Section 13.1 Construction of Initial Improvements. Lessee hereby is granted
permission, at Lessee's sole cost and expense, to design, develop and construct
upon the Premises the Initial Improvements.

Section 13.2 Alterations. Lessee shall have the right to make Alterations.

Section 13.3 Permits and Approvals. Lessee shall be solely responsible for
obtaining, at its sole cost and expense, any approvals that may be required
pursuant to that certain Declaration of Protected Covenants, of Moffet
Industrial Park No. 2 recorded in the Santa Clara official records on December
23, 1971, and the approval of the City (and any other governmental agencies with
jurisdiction) for any general plan amendment, rezoning, variance, conditional
use permit, building, electrical and plumbing permits, environmental impact
analysis and mitigations imposed thereby, or other governmental action necessary
to permit the development, construction and operation of the Improvements
(including any Alterations) in accordance with this Lease. Lessor, at no cost or
expense to itself, shall cooperate with Lessee to the extent reasonably required
to obtain the approval of the City for the Initial Improvements and any proposed
Alterations. Lessee shall reimburse Lessor for any out-of-pocket expenses
reasonably incurred by Lessor in connection with such cooperation.

Section 13.4 Design. The exterior design of the Improvements, including without
limitation, the site plan, landscaping plan and materials, colors, and
elevations, shall be subject to the approval of the City. Lessee shall provide
copies of such plans from time-to-time to Lessor.

Section 13.5 Prerequisites to Commencement of Construction. In addition to all
other requirements set forth herein, before commencing the construction of the
Initial Improvements or any Alterations and before any building materials have
been delivered to the Premises by Lessee or under Lessee's authority, Lessee
shall:

                  (a) Procure or cause to be procured the insurance coverage
described below in the limits hereinafter provided, and provide Lessor with
certified copies of all such insurance or, with the written approval of Lessor,
certificates of such insurance in form satisfactory to Lessor. All such
insurance shall comply with any requirements of Articles 14 and 21.

                  (b) Obtain the approval of Lessor of the general contractor in
respect of any Bonded Contracts, which approval shall not be unreasonably
withheld or delayed. Lessor hereby 


<PAGE>   13

approves Devcon Construction Company, and Lessor shall approve any other
contractor with an equivalent reputation and bonding capacity. If Lessor fails
to approve the general contractor, Lessee shall provide Lessor with performance
and payment bonds naming Lessor as an additional obligee, which shall cover
payment of all obligations arising under the Bonded Contracts in connection with
the construction of the Initial Improvements or any subsequent Alterations, as
the case may be, and guaranteeing the completion of such construction, and
payment in full of all claims for labor performed and materials supplied for
such construction. The bonds shall be issued by a responsible surety company,
licensed to do business in California, in an amount not less than the amount of
the Bonded Contracts and shall remain in effect until the entire cost of the
work shall have been paid in full. As used herein, the term "Bonded Contracts"
means the general contract and any construction contract separate from the
general contract that is for $100,000 or more. The bonds shall state that they
are conditioned to secure the completion of the work under the Bonded Contracts,
free from all liens and claims of contractors, subcontractors, mechanics,
laborers, and material suppliers; and that the construction work shall be
completed in accordance with the terms of the respective Bonded Contract by the
contractor thereunder, or, on its default, the surety.

                  (c) During the course of construction, to the extent not
covered by property insurance maintained by Lessee pursuant to Article 21,
maintain or caused to be maintained a comprehensive "all risk" builder's risk
insurance, including vandalism and malicious mischief, covering all improvements
in place on the Premises, all materials and equipment stored at the Premises and
furnished under contract, and all materials and equipment that are in the
process of fabrication at the premises of any third party or that have been
placed in due course of transit to the Premises when such fabrication or transit
is at the risk of, or when title to or an insurable interest in such materials
or equipment has passed to, Lessee or its construction manager, contractors or
subcontractors (excluding any contractors', subcontractors' and construction
managers' tools and equipment, and property owned by the employees of the
construction manager, any contractor or any subcontractor), such insurance to be
written on a completed value basis in an amount not less than the full estimated
replacement value of the Initial Improvements or such Alterations, as
applicable.

                  (d) Cause the contractor to procure and maintain comprehensive
liability insurance covering Lessee, Lessor and each construction manager,
contractor and subcontractor engaged in any work on the Premises, which
insurance may be effected by endorsement, if obtainable, on the policy required
to be carried pursuant to Article 21, including insurance for completed
operations, elevators, owner's, construction manager's and contractor's
protective liability, products completed operations for three (3) years after
the date of acceptance of the work by Lessee, broad form blanket contractual
liability, broad form property damage and full form personal injury (including
but not limited to bodily injury), covering the performance of all work at or
from the Premises by Lessee, its construction manager, contractors and
subcontractors, and in a liability amount not less than the amount at the time
carried by prudent owners of comparable construction projects in the Santa Clara
valley, but in any event not less than Ten Million Dollars ($10,000,000)
combined single limit, which policy shall contain a cross-liability clause or
separation of insureds provision, an endorsement deleting the property damage
exclusion as to explosion, underground, and collapse hazards, and an endorsement
providing incidental malpractice coverage, and shall include thereunder for the
mutual benefit of 


<PAGE>   14

Lessor and Lessee, bodily injury liability and property damage liability
automobile insurance on any non-owned, hired or leased automotive equipment used
in the construction of any work.

                  (e) Cause the contractor to procure and maintain Worker's
Compensation Insurance in the amounts and coverages required under workers'
compensation, disability and similar employee benefit laws applicable to the
Premises, and Employer's Liability Insurance with limits not less than Ten
Million Dollars ($10,000,000) or such higher amounts as may be required by law.

Section 13.6 General Construction Requirements.

                  (a) All construction and other work shall be done at Lessee's
sole cost and expense and in a prudent and first class manner and with first
class materials. Lessee shall construct the Initial Improvements and all
Alterations in strict accordance with all Applicable Laws, and with plans and
specifications that are in accordance with the provisions of this Article 13 and
all other provisions of this Lease.

                  (b) Lessee shall construct all improvements within setbacks
required by Applicable Laws or the provisions of this Lease.

                  (c) Prior to the commencement of any construction, alteration,
addition, improvements, repair or landscaping in excess of One Thousand Dollars
($1,000), Lessor shall have the right to post in a conspicuous location on the
Premises as well as to record with the County of Santa Clara, a Notice of
Lessor's Nonresponsibility. Lessee covenants and agrees to give Lessor at least
ten (10) days prior written notice of the commencement of any such construction,
alteration, addition, improvement, repair or landscaping in order that Lessor
shall have sufficient time to post such notice.

Section 13.7 Construction Completion Procedures.

                  (a) On completion of the construction of the Initial
Improvements or any Alterations during the Term, Lessee shall file for
recordation, or cause to be filed for recordation, a notice of completion.

                  (b) On completion of construction of the Initial Improvements
or any Alterations, Lessee shall deliver to Lessor evidence satisfactory to
Lessor of payment of all costs, expenses, liabilities and liens arising out of
or in any way connected with such construction (except for liens that are
contested in the manner provided herein).

ARTICLE 14. OWNERSHIP OF IMPROVEMENTS

                  All Improvements constructed, installed or placed by Lessee on
the Premises shall be the property of Lessee during, and only during, the Term
and no longer. During the Term, the Improvements shall not be conveyed,
transferred or assigned unless such conveyance, transfer or assignment shall be
to a person, corporation or other entity to whom this Lease is being transferred
or assigned simultaneously therewith in compliance with the provisions of (but
without limitation of the restrictions set forth in) Article 24, and at all such
times the holder of the leasehold interest of Lessee under this Lease shall be
the owner of the Improvements. Any 


<PAGE>   15

attempted conveyance, transfer or assignment of the Improvements, whether
voluntarily or by operation of law or otherwise, to any person, corporation or
other entity shall be void and of no effect whatever except a conveyance,
transfer or assignment to a person, corporation or other entity to whom this
Lease is being transferred or assigned simultaneously therewith in compliance
with the provisions of (but without limitation of the restrictions set forth in)
Article 24. Notwithstanding the foregoing, Lessee may from time to time replace
items of personal property and fixtures provided that the replacements for such
items are of equivalent or better value and quality, and such items are free
from any liens and encumbrances except as permitted hereunder. Upon any
termination of this Lease, whether by reason of the expiration of the Term
hereof, or pursuant to any provision hereof, or by reason of any other cause
whatsoever, all of Lessee's right, title and interest in the Improvements shall
cease and terminate and title to the Improvements shall vest in Lessor unless
Lessor makes the election to require demolition pursuant to Article 30. Lessee
shall surrender the Improvements to Lessor as provided in Article 30 hereof. No
further deed or other instrument shall be necessary to confirm the vesting in
Lessor of title to the Improvements. However, upon any termination of this
Lease, Lessee, upon request of Lessor, shall execute, acknowledge and deliver to
Lessor a quitclaim deed and quitclaim bill of sale confirming that all of
Lessee's rights, title and interest in the Improvements has expired and that
title thereto has vested in Lessor.

ARTICLE 15. MAINTENANCE AND REPAIRS; NO WASTE

Section 15.1 Maintenance and Repairs. During the Term, Lessee shall, at its own
cost and expense and without any cost or expense to Lessor, keep and maintain
the Premises and the Improvements and all appurtenant facilities, including
without limitation the grounds, soils, groundwater, sidewalks, parking and
landscaped areas, and all furniture, fixtures and equipment, in good condition
and repair and shall allow no nuisances to exist or be maintained thereon.

                  Lessor shall not be obligated to make to the Premises or the
Improvements any repairs, replacements or renewals of any kind, nature or
description whatsoever and Lessee hereby expressly waives any right to terminate
this Lease and any right to make repairs at Lessor's expense under Sections
1932(1), 1941 and 1942 of the California Civil Code, or any amendments thereof
or any similar law, statute or ordinance now or hereafter in effect.

Section 15.2 No Waste. Lessee shall not commit or permit waste upon the
Premises.

ARTICLE 16. UTILITIES AND SERVICES

                  Lessee shall be solely responsible for, shall make all
arrangements for, and shall pay for all utilities and services furnished to or
used at the Premises, including without limitation, gas, electricity, other
power, water, telephone, cable and other communication services, security
services, sewage, sewage service fees, trash collection, and any taxes or
impositions thereon. All service lines of such utilities shall be installed
beneath the surface of the Premises and connected and maintained at no cost or
expense to Lessor. Lessor grants to Lessee the right to grant to public
entities, public service corporations, or public utilities, for the purpose of
serving only the Premises, rights-of-way, or easements on or over the Premises
for poles or conduits or both for telephone, electricity, water, sanitary, or
storm sewers or both, and for other utilities and municipal or special district
services.


<PAGE>   16

ARTICLE 17. MECHANICS' AND OTHER LIENS

Section 17.1 No Liens. Lessee covenants and agrees to keep Lessor's Interest in
the Premises free and clear of and from any and all mechanics', material
supplier's and other liens for work or labor done, services performed,
materials, appliances, or power contributed, used or furnished, to be used in or
about the Premises for or in connection with any operations of Lessee, any
alteration, improvement or repairs or additions that Lessee may make or permit
or cause to be made, or any work or construction by, for or permitted by Lessee
on or about the Premises, and at all times promptly and fully to pay and
discharge any and all claims upon which any such lien may or could be based, and
to save and hold Lessor and Lessor's Interest in the Premises free and harmless
of and from any and all such liens and claims of liens and suits or other
proceedings pertaining thereto.

Section 17.2 No Affect on Lessor's Interests. No mechanics' or material
suppliers' liens or mortgages, deeds of trust, or other liens of any character
whatsoever created or suffered by Lessee shall in any way, or to any extent,
affect the interest, right or title of Lessor in and to the Premises or the
Improvements.

         Section 17.3 Lessor's Right to Cause Release of Liens. If Lessee shall
not within ten (10) days following the imposition of any such lien which is not
being contested by Lessee in accordance with Article 18 below, cause the lien to
be released of record by payment or posting of a proper bond, Lessor shall have
the right but not the obligation to cause the same to be released by such means
as Lessor shall deem appropriate and the amount paid by Lessor together with all
expenses incurred by Lessor in connection therewith (including without
limitation reasonable attorneys' fees and expense), plus interest at the
Interest Rate from the date of payment by Lessor, shall be Additional Rental,
immediately due and payable by Lessee to Lessor upon demand.

ARTICLE 18. RIGHT TO CONTEST LIENS

                  Lessee shall have the right to contest, in good faith, the
amount or validity of any lien of the nature described in Section 17.1 above,
provided that Lessee shall give Lessor written notice of Lessee's intention to
do so within ten (10) days after the recording of such lien, and provided
further, that Lessee shall, at its expense, defend itself and Lessor against the
same and shall pay and satisfy any adverse judgment that may be rendered thereon
before the enforcement thereof against the Premises.


<PAGE>   17

ARTICLE 19. COMPLIANCE WITH LAWS; INSURANCE REQUIREMENTS

Section 19.1 Compliance with Applicable Laws. Lessee, at Lessee's cost and
expense, shall comply with all Applicable Laws. Any work or installations made
or performed by or on behalf of Lessee or any person or entity claiming through
or under Lessee in order to conform the Premises to Applicable Laws shall be
subject to and performed in compliance with the provisions of Article 13. Lessee
shall give Lessor immediate written notice of any violation of Applicable Laws
known to Lessee and, at its sole cost and expense, Lessee shall immediately
rectify any such violation. Without in any way limiting the generality of the
foregoing obligation of Lessee, Lessee shall be solely responsible for
compliance with, and shall make or cause to be made all such improvements and
alterations to the Premises (including, without limitation, removing such
barriers and providing such alternative services) as shall be required by, the
Americans with Disabilities Act (42 USC section 12101 et seq.), as the same may
be amended from time to time, and any similar or successor laws, and with any
rules or regulations promulgated thereunder. Lessee's liability shall be primary
and Lessee shall indemnify Lessor in accordance with Article 22 in the event of
any failure or alleged failure of Lessee to comply or to cause the Improvements
to comply with said laws and rules and regulations.

Section 19.2 Compliance with Insurance Requirements. Lessee shall not do
anything, or permit anything to be done, in or about the Premises that would:
(i) invalidate or be in conflict with the provisions of any fire or other
insurance policies covering the Premises or any property located therein, or
(ii) result in a refusal by insurance companies of good standing to insure the
Premises or any such property in amounts required hereunder. Lessee, at Lessee's
expense, shall comply with all rules, orders, regulations or requirements of the
American Insurance Association (formerly the National Board of Fire
Underwriters) and with any similar body that shall hereafter perform the
function of such Association.

ARTICLE 20. HAZARDOUS SUBSTANCES

Section 20.1 Lessee Indemnity. Except for Lessor's obligations pursuant to
Section 4.1 above, Lessee releases Lessor from any liability for, waives all
claims against Lessor and shall indemnify, defend and hold harmless Lessor, its
employees, partners, agents, subsidiaries and affiliate organizations against
any and all claims, suits, loss, costs (including costs of investigation, clean
up, monitoring, restoration and reasonably attorney fees), damage or liability,
whether foreseeable or unforeseeable, by reason of property damage (including
diminution in the value of the property of Lessor), personal injury or death
directly arising from or related to Hazardous Substances released, manufactured,
discharged, disposed, used or stored on, in, or under the Land or Premises
during the initial Term and any extensions of this Lease by Lessee or its
employees, agents or contractors. The provisions of this Lessee Indemnity
regarding Hazardous Substances shall survive the termination of the Lease.


<PAGE>   18

Section 20.2 Lessor Indemnity. Lessor releases Lessee from any liability for,
waives all claims against Lessee and shall indemnify, defend and hold harmless
Lessee, its officers, employees, and agents to the extent of Lessor's interest
in the Project, against any and all actions by any governmental agency for clean
up of Hazardous Substances on or under the Land (including, without limitation,
any groundwater contamination) including costs of legal proceedings,
investigation, clean up, monitoring, and restoration, including reasonable
attorney fees and Lessor also releases Lessee from any liability for, waives all
claims against Lessee and shall indemnify, defend and hold harmless Lessee, its
officers, employees and agents from and against any and all liability and
actions for damages to property instituted by any third parties, if, and to the
extent, in either case, arising from the presence of Hazardous Substances on, in
or under the Land or Premises, except to the extent caused by the release,
disposal, use or storage of Hazardous Substances in, on or about the Premises by
Lessee, its employees, agents, sublessees, assignees, or contractors. The
provisions of this Lessor Indemnity regarding Hazardous Substances shall survive
the termination of the Lease.

Section 20.3 Lessee Covenants. Lessee has informed Lessor that, except for very
immaterial amounts of toxic materials incidental to office use (e.g. copier
toner, typical janitorial cleaning materials, petroleum products in cars),
Lessee will not use any Hazardous Substances within the Project and shall comply
with any applicable Laws to the extent that it does. Lessee shall immediately
notify Lessor if and when Lessee learns or has reason to believe there has been
any release of Hazardous Substances in, on or about the Project during the Term.

Section 20.4 Right to Remediate. Should Lessee fail to perform or observe any of
its obligations or agreements pertaining to Hazardous Substances or
Environmental Requirements, then Lessor shall have the right, but not the duty,
without limitation of any other rights of Lessor hereunder, to enter the
Premises personally or through its agents, consultants or contractors and
perform the same. Lessee agrees to indemnify Lessor for the costs thereof and
liabilities therefrom as set forth above in this Section 20.

ARTICLE 21. INSURANCE

Section 21.1 Required Insurance. At all times during the Term and at its sole
cost and expense, Lessee shall obtain and keep in force for the benefit of
Lessee and Lessor the following insurance:

                  (a) Fire and casualty insurance on all Improvements. The
amount of such insurance shall be the Full Insurable Replacement Value. All such
policies shall specify that proceeds shall be payable whether or not any
improvements are actually rebuilt. Each such policy shall include an endorsement
protecting the named and additional insureds against becoming a co-insured under
the policy. Lessee hereby waives as against Lessor any and all claims and
demands, of whatever nature, for damages, loss or injury to the Improvements and
to the property of Lessee in, upon or about the Premises caused by or resulting
from fire and/or other perils, construction defects and/or other events or
happenings.

                  "Full Insurable Replacement Value" means 100% of the actual
costs to replace the Improvements (without deduction for depreciation but with
standard exclusions such as foundations, excavations, paving and landscaping, as
applicable to specific perils), including the 


<PAGE>   19

costs of demolition and debris removal and including materials and equipment not
in place but in transit to or delivered to the Premises. The Full Insurable
Replacement Value initially shall be determined at Lessee's expense by an
appraiser or one of the insurers, selected by Lessee and acceptable to Lessor.
Lessor or Lessee may at any time, but not more frequently than once in any
twelve (12) month period, by written notice to the other, require the Full
Insurable Replacement Value to be redetermined, at Lessee's expense, by an
appraiser or one of the insurers, selected by Lessee and reasonably acceptable
to Lessor. Lessee shall maintain coverage at the current Full Insurable
Replacement Value throughout the Term.

                  (b) Insurance against loss of rental from the Premises, under
a rental value insurance policy, or against loss from business interruption
under a business interruption policy, covering risk of loss due to causes
insured against under subsection (a), in an amount not less than twelve months
of projected rental income from the Premises.

                  (c) Worker's Compensation Insurance in the amounts and
coverages required under worker's compensation, disability and similar employee
benefit laws applicable to the Premises, with all elective employment covered on
a voluntary basis where permissible, and Employer's Liability Insurance with
limits not less than $500,000 or such higher amounts as may be required by law.

                  (d) Comprehensive general liability through one or more
primary and umbrella liability policies against claims, including but not
limited to, bodily injury and property damage occurring on the Premises or the
streets, curbs or sidewalks adjoining the Premises, with such limits as may be
reasonably required by Lessor from time to time, but in any event not less than
Ten Million Dollars ($10,000,000), combined single limit and annual aggregate
for the Premises. Such insurance shall insure the performance by Lessee of the
indemnity agreements contained in this Lease. If any governmental agency or
department requires insurance or bonds with respect to any proposed or actual
use, storage, treatment or disposal of Hazardous Substances by Lessee or any
sublessee, tenant, or licensee of Lessee, Lessee shall be responsible for such
insurance and bonds and shall pay all premiums and charges connected therewith;
provided, however, that this provision shall not and shall not be deemed to
modify the provisions of Article 20 hereof.

                  Such insurance shall (i) delete any employee exclusion on
personal injury coverage; (ii) include employees as additional insureds; (iii)
provide for blanket contractual coverage, including liability assumed by and the
obligations of Lessee under Article 22 for personal injury, death and/or
property damage; (iv) provide Products and Completed Operations and Independent
Contractors coverage and Broad Form Property Damage liability coverage without
exclusions for collapse, explosion, demolition, underground coverage and
excavating, including blasting; (v) provide aircraft liability coverage, if
applicable, and automobile liability coverage for owned, non-owned and hired
vehicles; (vi) provide liability coverage on all mobile equipment used by
Lessee; and (vii) include a cross liability endorsement (or provision)
permitting recovery with respect to claims of one insured against another. Such
insurance shall insure against any and all claims for bodily injury, including
death resulting therefrom, and damage to or destruction of property of any kind
whatsoever and to whomever belonging and arising from Lessee's operations
hereunder and whether such operations are performed by Lessee or any of its
contractors, subcontractors, or by any other person.


<PAGE>   20

                  (e) An environmental impairment liability policy with such
limits as may be appropriate given the nature of Lessee's operations on the
Premises.

                  (f) All other insurance that Lessee is required to maintain
under Applicable Laws.

Section 21.2 Policy Form and General.

                  (a) All of the insurance policies required under this Lease,
including without limitation, under the provisions of Article 13 and this
Article 21, and all renewals thereof shall be issued by one or more companies of
recognized responsibility, authorized to do business in California with a
financial rating of at least a Class A--VII (or its equivalent successor)
status, as rated in the most recent edition throughout the Term of Best's
Insurance reports (or its successor, or, if there is no equivalent successor
rating, otherwise reasonably acceptable to Lessor). Any loss adjustment or
disposition of insurance proceeds by the insurer shall require the written
consent of Lessor for losses in excess of One Hundred Thousand Dollars
($100,000.00). All property insurance hereunder shall name Lessor as an
additional insured and all liability insurance shall name as additional insureds
Lessor, and its directors, trustees, officers, agents, and employees, and such
other parties as Lessor reasonably may request. Any deductibles or self
insurance retention for any of the foregoing insurance must be agreed to in
advance in writing by Lessor, which consent shall not be unreasonably withheld
or delayed; all deductibles and self insurance retention shall be paid by
Lessee. All insurance of Lessee shall be primary coverage.

                  (b) Each policy of property insurance and all other policies
of insurance required by the provisions of this Lease, shall be made expressly
subject to the provisions of this Article 21 and shall provide that Lessee's
insurers shall waive any right of subrogation against Lessor. All policies
provided for herein expressly shall provide that such policies shall not be
canceled, terminated or altered without thirty (30) days' prior written notice
to Lessor. Each policy, or a certificate of the policy executed by the insurance
company evidencing that the required insurance coverage is in full force and
effect, shall be deposited with Lessor on or before the date of this Lease,
shall be maintained throughout the Term, and shall be renewed, not less than
thirty (30) days before the expiration of the term of the policy. Except for
specific provisions described herein, no policy shall contain any provisions for
exclusions from liability and no exclusion shall be permitted in any event if it
conflicts with any coverage required hereby, and, in addition, no policy shall
contain any exclusion from liability for personal injury or sickness, disease or
death or which in any way impairs coverage under the contractual liability
coverage described above.

                  (c) If either party shall at any time deem the limits of any
of the insurance described in this Lease then carried or required to be carried
to be either excessive or insufficient, or if Lessee shall determine that any
form, scope, or type of insurance required hereunder is not generally available
in the marketplace at reasonable cost, the parties shall endeavor to agree upon
the proper and reasonable limits and terms for such insurance then to be carried
and such insurance shall thereafter be carried with the limits and terms thus
agreed upon until further change pursuant to the provisions of this subsection.
If the parties shall be unable to agree on the proper and reasonable limits and
terms for such insurance, then such limits and terms shall be determined
pursuant to the provisions of Article 37. The decision of the appraiser 


<PAGE>   21

as to such limits and terms for such insurance then to be carried shall be
binding upon the parties and such insurance shall be carried with the limits and
terms as thus determined until such limits shall again be changed pursuant to
the provisions of this subsection. The expenses of such determination shall be
borne equally between Lessor and Lessee.


ARTICLE 22. INDEMNITY AND RELEASE

                  Lessee shall indemnify, protect, defend and save and hold
harmless Lessor and the Premises from and against, and reimburse Lessor for, any
and all claims, demands, losses, damages, costs, liabilities, causes of action
and expenses, including, without limitation, reasonable attorneys' fees and
expenses, incurred in connection with or arising, in whole or in part, in any
way out of this Lease, any default by Lessee in the observance or performance of
any of the terms, covenants or conditions of this Lease on Lessee's part to be
observed or performed, the use, occupancy or manner of use or occupancy of the
Premises by Lessee or any sublessee, licensee, or any other person or entity,
the conduct or management of any work or thing done in or on the Premises, the
design, construction, maintenance, or condition of any Improvements, the
condition of the Premises, any actual or alleged acts, omissions, or negligence
of Lessee or of the sublessees, contractors, agents, servants, employees,
visitors or licensees of Lessee, in, on or about the Premises or other of
Lessor's lands, and any accident or other occurrence on the Premises from any
cause whatsoever, except to the extent caused solely by the gross negligence or
willful misconduct of Lessor.

                  In case any claim, action or proceeding be brought, made or
initiated against Lessor relating to any of the above described events, acts,
omissions, occurrences, or conditions, Lessee, upon notice from Lessor, shall at
its sole cost and expense, resist, or defend such claim, action or proceeding by
attorneys approved by Lessor.

                  Lessor shall not be responsible for, and Lessee hereby waives
any and all claims and causes of action whatsoever of any kind or nature against
Lessor for, any injury, loss, damage or liability to any person or property in
or about the Premises or in any way connected with the Premises or this Lease,
from any cause whatsoever (other than caused solely by the gross negligence or
willful misconduct of Lessor).

                  The provisions of this Article 22 shall survive any
termination of this Lease. The provisions of Article 21 (Insurance) shall not
limit in any way Lessee's obligations under this Article 22.


<PAGE>   22

ARTICLE 23. APPROPRIATION, DAMAGE OR DESTRUCTION

Section 23.1 No Termination, No Affect on Rental Obligation. No Appropriation
nor any loss or damage by fire or other cause resulting in either partial or
total destruction of the Premises, the Improvements or any other property on the
Premises shall,

Section 23.2 Determination of Award. The amount of the Award due to Lessor and
Lessee as a result of Appropriation shall be separately determined by the court
having jurisdiction of such proceedings based on the following: Lessor shall be
entitled to that portion of the Award attributable to the value of the fee
interest in the Premises (or portion thereof subject to Appropriation, in case
of a partial Appropriation) subject to this Lease, and to the value of Lessor's
reversionary interest in the Improvements (or portion thereof subject to
Appropriation, in case of a partial Appropriation), as determined by the court;
Lessee shall be entitled to that portion of the Award attributable to the value
of Lessee's leasehold interest in the Premises (or portion thereof subject to
Appropriation, in case of a partial Appropriation) and to the value of Lessee's
interest in the Improvements (or portion thereof subject to Appropriation, in
case of a partial Appropriation), as determined by the court.

ARTICLE 24. ASSIGNMENT

Section 24.1 Assignment. Prior to completion of construction of the Initial
Improvements, any assignment by Lessee of its leasehold estate shall not release
Lessee from its obligations hereunder and such assignments shall be subject to
the consent of Lessor, provided, however, Lessee shall have the right to assign
its interest hereunder to a financing entity in connection with a synthetic
lease transaction without the prior written consent of Lessor.

Section 24.2 Assumption in Writing. No assignment by Lessee shall become
effective unless and until the assignee executes and delivers to Lessor a
written form of assignment in which the assignee assumes and agrees to perform
and observe all covenants and conditions to be performed and observed by Lessee
under this Lease for the period from and after the date of the assignment.

ARTICLE 25. SUBLETTING

Section 25.1 Conditions to Subletting. Lessee may enter into Subleases in
respect of the Premises without Lessor's consent. No Sublease shall relieve
Lessee from the performance of any of its obligations under this Lease. No
Sublease shall extend beyond the Term of this Lease. Each Sublease shall be
subject to and subordinate to the terms, covenants and conditions of this Lease
and the rights of Lessor hereunder.

ARTICLE 26. LEASEHOLD MORTGAGES


<PAGE>   23

Section 26.1 Leasehold Mortgage. Notwithstanding the provisions of Article 24
regarding Transfer of this Lease, but subject to the provisions of this Article
26, Lessee shall have the right at any time and from time to time to encumber
the entire (but not less than the entire) leasehold estate created by this Lease
and Lessee's interest in the Improvements by a mortgage, deed of trust or other
security instrument (any such mortgage, deed of trust, or other security
instrument that satisfies the requirements of this Article 26 being herein
referred to as a "Leasehold Mortgage") to secure repayment of one or more loans
(and associated obligations) made to Lessee.

                  Lessee shall deliver to Lessor promptly after execution by
Lessee a true and verified copy of any Leasehold Mortgage, and any amendment,
modification or extension thereof, together with the name and address of the
owners and holder thereof.

                  In no event shall any interest of Lessor in the Premises,
including without limitation, Lessor's fee interest in the Premises or
reversionary interest in the Improvements or interest under this Lease, be
subject or subordinate to any lien or encumbrance of any mortgage, deed of trust
or other security instrument.

Section 26.2 Agreement Regarding the Leasehold Mortgage. During the continuance
of any Leasehold Mortgage until such time as the lien of any Leasehold Mortgage
has been extinguished, and if a true and verified copy of such Leasehold
Mortgage shall have been delivered to Lessor together with a written notice of
the name and address of the holder thereof:

                  (a) Lessor shall not agree to any termination nor accept any
surrender of this Lease (except upon the expiration of the Term or termination
pursuant to Article 23 hereof and as otherwise provided below with respect to
termination upon an Event of Default), nor shall any material amendment or
modification of this Lease be binding upon the holder of a Leasehold Mortgage
("Lender") or any purchaser in foreclosure from the Lender, unless the Lender
has given its prior written consent to such amendment or modification.

                  (b) The Lender shall have the right, but not the obligation,
at any time prior to termination of this Lease and without payment of any
penalty, to pay all of the Base Monthly Rental and Additional Rental due
hereunder, to provide any insurance and make any other payments, to make any
repairs and improvements and do any other act or thing required of Lessee
hereunder, and to do any act or thing which may be necessary and proper to be
done in the performance and observance of the covenants, conditions and
agreements hereof to prevent the termination of this Lease. All payments so made
and all things so done and performed by the Lender shall be as effective to
prevent a termination of this Lease as the same would have been if made, done
and performed by Lessee instead of by the Lender.

                  (c) Should any Event of Default under this Lease occur, the
Lender shall have thirty (30) days after receipt of notice from Lessor setting
forth the nature of such Event of Default, and, if the default is such that
possession of the Premises is necessary to remedy the default, a reasonable time
after the expiration of such thirty (30) day period, within which to remedy such
default, provided that (i) the Lender shall have fully cured any default in the
payment of any monetary obligations of Lessee under this Lease within such
thirty (30) day period and shall continue to pay currently such monetary
obligations as and when the same are 

<PAGE>   24

due, and (ii) the Lender shall have acquired Lessee's leasehold estate created
hereby or given Lessor written notice that the Lender intends to take action to
acquire Lessee's leasehold estate and commenced foreclosure or other appropriate
proceedings in the nature thereof within such thirty (30) day period or prior
thereto, and shall thereafter diligently and continuously prosecute such
proceedings to completion.

                  (d) An Event of Default under this Lease which in the nature
thereof cannot be remedied by the Lender shall be deemed to be remedied if (i)
within thirty (30) days after receiving written notice from Lessor of such Event
of Default, the Lender shall have acquired Lessee's leasehold estate created
hereby or given Lessor written notice that the Lender intends to take action to
acquire Lessee's leasehold estate and commenced foreclosure or other appropriate
proceedings in the nature thereof, (ii) the Lender shall diligently and
continuously prosecute any such proceedings to completion, (iii) the Lender
shall have fully cured any default in the payment of any monetary obligations of
Lessee under this Lease within such thirty (30) day period and shall thereafter
continue to faithfully perform all such monetary obligations, and (iv) after
gaining possession of the Premises, the Lender shall perform all of the
obligations of Lessee hereunder as and when the same are due and cure any
defaults that are curable by the Lender but that require possession of the
Premises to cure, such cure to be effected within thirty (30) days after gaining
possession, or such longer period of time as is reasonably necessary to effect
such cure using all due diligence.

                  (e) If the Lender is prohibited by any process or injunction
issued by any court or by reason of any action by any court having jurisdiction
of any bankruptcy or insolvency proceedings involving Lessee from commencing or
prosecuting foreclosure or other appropriate proceedings in the nature thereof,
the times specified in subsections (c) and (d) above for commencing or
prosecuting such foreclosure or other proceedings shall be extended for the
period of such prohibition; provided that the Lender shall have fully cured any
default in the payment of any monetary obligations of Lessee under this Lease
and shall continue to pay currently such monetary obligations as and when the
same fall due, and provided further that the Lender shall diligently attempt to
remove any such prohibition.

                  (f) Lessor shall mail to the Lender a duplicate copy by
certified mail of any and all notices that Lessor may from time to time give to
or serve upon Lessee pursuant to the provisions of this Lease.

                  (g) Foreclosure of a Leasehold Mortgage or any sale
thereunder, whether by judicial proceedings or by virtue of any power of sale
contained in the Leasehold Mortgage, or any conveyance of the leasehold estate
created hereby from Lessee to the Lender by virtue or in lieu of foreclosure or
other appropriate proceedings in the nature thereof, shall not require the
consent of Lessor or constitute a breach of any provision of or a default under
this Lease and upon such foreclosure, sale or conveyance, Lessor shall recognize
the Lender, or any other foreclosure sale purchaser or recipient of any deed in
lieu, as Lessee hereunder; provided, (i) the Lender shall have fully complied
with the provisions of this Article 26 applicable prior to gaining possession of
the Premises and the Lender or foreclosure sale purchaser or deed in lieu
recipient, as the case may be, who is to become the Lessee hereunder shall
comply with the provisions of this Article 26 applicable after gaining
possession of the Premises; (ii) the Lender, or foreclosure sale purchaser or
deed in lieu recipient, as the case may be, who is to become the


<PAGE>   25

Lessee hereunder shall be responsible for taking such actions as shall be
necessary to obtain possession of the Premises; and (iii) the Lender, or
foreclosure sale purchaser or deed in lieu recipient, as the case may be, who is
to become the Lessee hereunder shall execute, acknowledge and deliver to Lessor
an instrument in recordable form pursuant to which the Lender or foreclosure
sale purchaser or deed in lieu recipient, as the case may be, expressly assumes
all obligations of the Lessee under this Lease which arise from and after the
date of foreclosure or deed in lieu thereof. If there are two or more Leasehold
Mortgages or foreclosure sale purchasers (whether of the same or different
Leasehold Mortgages), Lessor shall have no duty or obligation whatsoever to
determine the relative priorities of such Leasehold Mortgages or the rights of
the different holders thereof and/or foreclosure sale purchasers. If the Lender
or foreclosure sale purchaser becomes Lessee under this Lease, or under any new
lease obtained pursuant to subsection (h) below, the Lender or foreclosure sale
purchaser shall not be personally liable for the obligations of the Lessee under
this Lease accruing after the period of time that the Lender is the Lessee
hereunder or thereunder.

                  (h) In the event of (a) any rejection of this Lease by Lessee
in any bankruptcy proceeding, or (b) such other termination of this Lease by
reason of a condition which (i) is not known or ascertainable by the parties on
the effective date of the Lender's Leasehold Mortgage, (ii) results from any
applicable state or federal law enacted after the effective date of such
Leasehold Mortgage, and (iii) which would work an inequitable forfeiture upon
the Lender due to the non-curable nature of such condition, Lessor shall,
subject to the terms and conditions of this subsection (h), upon written request
by the Lender to Lessor made within sixty (60) days after such termination,
execute and deliver a new lease of the Premises to the Lender for the remainder
of the term of this Lease with the same covenants, conditions and agreements
(except for any requirements which have been satisfied by Lessee prior to
termination) as are contained herein; provided, however, that Lessor's execution
and delivery of such new lease of the Premises shall be made without
representation or warranty of any kind or nature whatsoever, either express or
implied, including without limitation, any representation or warranty regarding
title to the Premises or the priority of such new lease and Lessor's obligations
and liability under such new lease shall not be greater than if this Lease had
not terminated and the Lender had become the Lessee hereunder. Lessor's delivery
of any Improvements to the Lender pursuant to such new lease shall be made
without representation or warranty of any kind or nature whatsoever, either
express or implied; and the Lender shall take any Improvements "as is" in their
then current condition. Upon execution and delivery of such new lease, the
Lender, at its sole cost and expense, shall be responsible for taking such
action as shall be necessary to cancel and discharge this Lease and to remove
the Lessee named herein and any other occupant from the Premises. Lessor's
obligation to enter into such new lease of the Premises with the Lender shall be
conditioned as follows: (x) the Lender shall have complied with the provisions
of this Article 26 applicable prior to the gaining of possession and shall
comply with the provisions of this Article 26 applicable after gaining
possession of the Premises; (y) if more than one holder of a Leasehold Mortgage
claims to be the Lender and requests such new lease, Lessor shall have no duty
or obligation whatsoever to determine the relative priority of such Leasehold
Mortgages, and in the event of any dispute between or among the holders thereof,
Lessor shall have no obligation to enter into any such new lease if such dispute
is not resolved to the sole satisfaction of Lessor within ninety (90) days after
the date of termination of this Lease; and (z) the Lender shall pay all costs
and expenses of Lessor, including without limitation, reasonable attorneys'
fees, real property transfer taxes and any escrow fees and recording charges,
incurred in 


<PAGE>   26

connection with the preparation and execution of such new lease and any
conveyances related thereto.

ARTICLE 27. LESSOR'S RIGHT OF INSPECTION

                  Lessor shall be entitled, at all reasonable times with advance
written notice to go upon the Premises and the Improvements for the purposes of
(a) inspecting the same, (b) inspecting the performance by Lessee of the terms,
covenants, agreements and conditions of this Lease, (c) posting and keeping
posted thereon Notices of Non-Responsibility for any construction, alteration or
repair thereof, as required or permitted by any law or ordinance, and (d) any
other lawful purposes; provided, however, Lessor's rights hereunder shall not
entitle Lessor to access to the demised premises of any subtenant occupying the
Improvements without the written consent of such subtenant, which consent shall
not be unreasonably withheld.

ARTICLE 28. EVENT OF DEFAULT AND LESSOR'S REMEDIES

Section 28.1 Events of Default. The occurrence of any of the following shall be
an Event of Default on the part of Lessee hereunder:

                  (a) Failure to pay any part of the Base Monthly Rental or
Additional Rental, herein reserved, or any other sums of money that Lessee is
required to pay hereunder at the times or in the manner herein provided, when
such failure shall continue for a period of ten (10) days after written notice
thereof from Lessor to Lessee. No such notice shall be deemed a forfeiture or a
termination of this Lease unless Lessor expressly so elects in such notice.

                  (b) Failure to perform any express or implied nonmonetary
provision of this Lease when, except in the case of any provision which by its
terms provides for no grace period, such failure shall continue for a period of
thirty (30) days, or such other period as is expressly set forth herein, after
written notice thereof from Lessor to Lessee; provided that if the nature of the
default is such that more than thirty (30) days are reasonably required for its
cure, then an Event of Default shall not be deemed to have occurred if Lessee
shall commence such cure within said thirty (30) day period and thereafter
diligently and continuously prosecute such cure to completion and cure. No such
notice shall be deemed a forfeiture or a termination of this Lease unless Lessor
expressly so elects in such notice.

                  (c) The abandonment of the Premises.

                  (d) Lessee shall admit in writing its inability to pay its
debts generally as they become due, file a petition in bankruptcy, insolvency,
reorganization, readjustment of debt, dissolution or liquidation under any law
or statute of any government or any subdivision thereof either now or hereafter
in effect, make an assignment for the benefit of its creditors, consent to or
acquiesce in the appointment of a receiver of itself or of the whole or any
substantial part of the Premises.

                  (e) A court of competent jurisdiction shall enter an order,
judgment or decree appointing a receiver of Lessee or of the whole or any
substantial part of the Premises and such order, judgment or decree shall not be
vacated, set aside or stayed within forty-five (45) days 


<PAGE>   27

after the date of entry of such order, judgment, or decree, or a stay thereof
shall be thereafter set aside.

                  (f) A court of competent jurisdiction shall enter an order,
judgment or decree approving a petition filed against Lessee under any
bankruptcy, insolvency, reorganization, readjustment of debt, dissolution or
liquidation law or statute of the Federal government or any state government or
any subdivision of either now or hereafter in effect, and such order, judgment
or decree shall not be vacated, set aside or stayed within forty-five (45) days
from the date of entry of such order, judgment or decree, or a stay thereof
shall be thereafter set aside.

Section 28.2 Lessor's Remedies. Upon the occurrence of an Event of Default,
Lessor shall have the following rights and remedies:

                  (a) The right to terminate this Lease, in which event Lessee
shall immediately surrender possession of the Premises in accordance with
Article 30, and pay to Lessor all Base Monthly Rental, Additional Rental and
other charges and amounts due from Lessee hereunder to the date of termination.

                  (b) The rights and remedies described in California Civil Code
Section 1951.2, including without limitation, the right to recover the worth at
the time of award of the amount by which the Base Monthly Rental, Additional
Rental and other charges payable hereunder for the balance of the Term after the
time of award exceed the amount of such rental loss for the same period that
Lessee proves could be reasonably avoided, as computed pursuant to subdivision
(b) of said Section 1951.2, and the right to recover any amount necessary to
compensate Lessor for all the detriment proximately caused by Lessee's failure
to perform its obligations under this Lease or which in the ordinary course of
things would be likely to result therefrom which, without limiting the
generality of the foregoing, includes unpaid taxes and assessments, any costs or
expenses incurred by Lessor in recovering possession of the Premises,
maintaining or preserving the Premises after such default, preparing the
Premises for reletting to a new lessee, any repairs or alterations to the
Premises for such reletting, leasing commissions, architect's fees and any other
costs necessary or appropriate either to relet the Premises or to adapt them to
another beneficial use by Lessor and such amounts in addition to or in lieu of
the foregoing as may be permitted from time to time by applicable California
law.

                  (c) The rights and remedies described in California Civil Code
Section 1951.4 that allow Lessor to continue this Lease in effect and to enforce
all of its rights and remedies under this Lease, including the right to recover
Base Monthly Rental, and Additional Rental as they become due, for so long as
Lessor does not terminate Lessee's right to possession. Acts of maintenance or
preservation, efforts to relet the Premises or the appointment of a receiver
upon Lessor's initiative to protect its interest under this Lease shall not
constitute a termination of Lessee's right to possession.

                  (d) The right and power to enter and to sublet the Premises,
to collect rents from all subtenants and to provide or arrange for the provision
of all services and fulfill all obligations of Lessee under the subleases and
Lessor is hereby authorized on behalf of Lessee, but shall have absolutely no
obligation, to provide such services and fulfill such obligations and to incur
all such expenses and costs as Lessor deems necessary in connection therewith.
Lessee 


<PAGE>   28

shall be liable immediately to Lessor for all costs and expenses Lessor incurs
in collecting such rents and arranging for or providing such services or
fulfilling such obligations. Lessor is hereby authorized, but not obligated, to
relet the Premises or any part thereof on behalf of Lessee, to incur such
expenses as may be necessary to effect a relet and make said relet for such term
or terms, upon such conditions and at such rental as Lessor in its sole
discretion may deem proper. Lessee shall be liable immediately to Lessor for all
reasonable costs Lessor incurs in reletting the Premises including, without
limitation, brokers' commissions, expenses of remodeling the Premises required
by the reletting, and other costs. If Lessor relets the Premises or any portion
thereof, such reletting shall not relieve Lessee of any obligation hereunder,
except that Lessor shall apply the rent or other proceeds actually collected by
it as a result of such reletting against any amounts due from Lessee hereunder
to the extent that such rent or other proceeds compensate Lessor for the
nonperformance of any obligation of Lessee hereunder. Such payments by Lessee
shall be due at such times as are provided elsewhere in this Lease, and Lessor
need not wait until the termination of this Lease, by expiration of the Term
hereof or otherwise, to recover them by legal action or in any other manner.
Lessor may execute any lease made pursuant hereto in its own name, and the
lessee thereunder shall be under no obligation to see to the application by
Lessor of any rent or other proceeds, nor shall Lessee have any right to collect
any such rent or other proceeds. Lessor shall not by any reentry or other act be
deemed to have accepted any surrender by Lessee of the Premises or Lessee's
interest therein, or be deemed to have otherwise terminated this Lease, or to
have relieved Lessee of any obligation hereunder, unless Lessor shall have given
Lessee express written notice of Lessor's election to do so as set forth herein.

                  (e) The right to have a receiver appointed upon application by
Lessor to take possession of the Premises and to collect the rents or profits
therefrom and to exercise all other rights and remedies pursuant to Section
28.2(d).

                  (f) The right to enjoin, and any other remedy or right now or
hereafter available to a lessor against a defaulting lessee under the laws of
the State of California or the equitable powers of its courts, and not otherwise
specifically reserved herein.

ARTICLE 29. LESSOR'S RIGHT TO CURE DEFAULTS.

                  If Lessee shall fail or neglect to do or perform any act or
thing herein provided by it to be done or performed and such failure shall not
be cured within any applicable grace period provided in Article 28, then Lessor
shall have the right, but shall have no obligation, to pay any Imposition
payable by Lessee hereunder, discharge any lien, take out, pay for and maintain
any insurance required under Article 21, or do or perform or cause to be done or
performed any such other act or thing (entering upon the Premises for such
purposes, if Lessor shall so elect), and Lessor shall not be or be held liable
or in any way responsible for any loss, disturbance, inconvenience, annoyance or
damage resulting to Lessee on account thereof, and Lessee shall repay to Lessor
upon demand the entire reasonable cost and expense thereof, including, without
limitation, compensation to the agents, consultants and contractors of Lessor
and reasonable attorneys' fees and expenses. Lessor may act upon shorter notice
or no notice at all if necessary in Lessor's judgment to meet an emergency
situation or governmental or municipal time limitation or otherwise to protect
Lessor's interest in the Premises. Lessor shall not be required to inquire into
the correctness of the amount or validity of any Imposition or lien that may be


<PAGE>   29

paid by Lessor, and Lessor shall be duly protected in paying the amount of any
such Imposition or lien claimed, and, in such event, Lessor shall also have the
full authority, in Lessor's sole judgment and discretion and without prior
notice to or approval by Lessee, to settle or compromise any such lien or
Imposition. Any act or thing done by Lessor pursuant to the provisions of this
Article 30 shall not be or be construed as a waiver of any default by Lessee, or
as a waiver of any term, covenant, agreement or condition herein contained or of
the performance thereof. All amounts payable by Lessee to Lessor under any of
the provisions of this Lease, if not paid when the same become due as in this
Lease provided, shall bear interest at the Interest Rate.

ARTICLE 30. SURRENDER OF THE PREMISES

                  Upon the termination of this Lease, whether at the expiration
of the Term as stated in Article 5 hereof or prior thereto pursuant to any
provision hereof, Lessee shall surrender to Lessor the Premises in good order
and repair, reasonable wear and tear and acts of God casualties excepted. Within
ninety (90) days following the termination of this Lease, Lessor may elect to
require Lessee to demolish the buildings located on the Property. Lessor may
make such election by delivering written notice to Lessee within such 90-day
period. In the event Lessor makes such election, Lessee shall diligently proceed
to demolish the buildings and complete such demolition within a reasonable time,
at no cost to Lessor. Unless Lessor gives written notice of its election to
require Lessee to demolish the improvements in accordance with the foregoing,
all Improvements shall automatically and without further act by Lessor or
Lessee, become the property of Lessor.


                  Any personal property of Lessee that remains on the Premises
after the Termination Date may, at the option of Lessor, be deemed to have been
abandoned by Lessee and may either be retained by Lessor as its property or
disposed of, without accountability, in such manner as Lessor may determine in
its sole discretion.

ARTICLE 31. REPRESENTATIONS AND WARRANTIES OF LESSEE

                  Lessee hereby represents and warrants to Lessor as follows:

                  (a) Lessee is a corporation, partnership, or limited liability
company duly formed and validly existing under the laws of the state of
identified in the Basic Lease Information and is qualified to do business under
the laws of the State of California. Lessee has full corporate power and
authority to enter into and perform its obligations under this Lease and to
develop, construct and operate the Premises as contemplated by this Lease.

                  (b) Lessee has taken all necessary action to authorize the
execution, delivery and performance of this Lease and this Lease constitutes the
legal, valid, and binding obligation of Lessee.

                  (c) Lessee has the right, power, legal capacity and authority
to enter into and perform its obligations under this Lease and no approvals or
consents of any person are required in connection with the execution and
performance of this Lease. The execution and performance of this Lease will not
result in or constitute any default or event that with notice or the lapse of


<PAGE>   30

time or both, would be a default, breach or violation of the organizational
instruments governing Lessee or any agreement or any order or decree of any
court or other governmental authority to which Lessee is a party or to which it
is subject.

ARTICLE 32. NO WAIVER BY LESSOR

                  No failure by Lessor to insist upon the strict performance of
any term, covenant, agreement, provision, condition or limitation of this Lease
or to exercise any right or remedy upon a breach thereof, and no acceptance by
Lessor of full or partial rent during the continuance of any such breach, shall
constitute a waiver of any such breach or of such term, covenant, agreement,
provision, condition or limitation. No term, covenant, agreement, provision,
condition or limitation of this Lease and no breach thereof may be waived,
altered or modified except by a written instrument executed by Lessor. No waiver
of any breach shall affect or alter this Lease but each and every term,
covenant, agreement, provision, condition and limitation of this Lease shall
continue in full force and effect with respect to any other then existing or
subsequent breach.

ARTICLE 33. NO PARTNERSHIP

                  It is expressly understood that neither Lessee nor Lessor is
or becomes, in any way or for any purpose, a partner of the other in the conduct
of its business, or otherwise, or joint venturer or a member of a joint
enterprise with the other, or agent of the other by reason of this Lease or
otherwise. Lessee is and shall be an independent contractor with respect to the
Lease and Premises.

ARTICLE 34. NO DEDICATION

                  This Lease shall not be, nor be deemed or construed to be, a
dedication to the public of the Premises, the areas in which the Premises are
located or the Improvements, or any portion thereof.

ARTICLE 35. NO THIRD PARTY BENEFICIARIES

                  This Lease shall not confer nor be deemed nor construed to
confer upon any person or entity, other than the parties hereto, any right or
interest, including, without limiting the generality of the foregoing, any third
party beneficiary status or any right to enforce any provision of this Lease.

ARTICLE 36. NOTICES

                  Any notice, consent or other communication required or
permitted under this Lease shall be in writing and shall be delivered by hand,
sent by air courier, sent by prepaid registered or certified mail with return
receipt requested, or sent by facsimile, and shall be deemed to have been given
on the earliest of (i) receipt, (ii) one business day after delivery to an air
courier for overnight expedited delivery service, or (iii) five (5) business
days after the date deposited in the United States mail, registered or
certified, with postage prepaid and return receipt requested (provided that such
return receipt must indicate receipt at the address specified) or on the day of
its transmission by facsimile if transmitted during the business hours of the
place 

<PAGE>   31

of receipt, otherwise on the next business day. All notices shall be addressed
as appropriate to the following addresses (or to such other or further addresses
as the parties may designate by notice given in accordance with this section):

If to Lessor:

                  475 Java Drive Associates, L.P.
            c/o The Mozart Development Company
                  1068 East Meadow Circle
                  Palo Alto, CA  94303

                  Tel.:  (   )    -

If to Lessee:

                  Network Appliance Inc.
                  2770 San Tomas Expressway
                  Santa Clara, California 95051
                  Attn:  Chris Carlton
                  Tel. (408) 367-3200

ARTICLE 37. HOLDING OVER

                  This Lease shall terminate upon the Termination Date and any
holding over by Lessee after the Termination Date shall not constitute a renewal
of this Lease or give Lessee any rights hereunder or in or to the Premises.

ARTICLE 38. MEMORANDUM

                  This Lease shall not be recorded. However, at the request of
either party, the parties hereto shall execute and acknowledge a memorandum
hereof (including Lessee's options under Article 10) in recordable form that
Lessor shall file for recording in the Official Records of Santa Clara County.

ARTICLE 39. ESTOPPEL CERTIFICATE

                  Each of the parties hereto agrees, at any time and from time
to time upon not less than twenty (20) days' prior written request by the other
party (which request must specify that response is required within twenty (20)
days), to execute, acknowledge and deliver to the party making such request, or
to any other Person specified by the requesting party, an estoppel certificate
stating: (a) whether this Lease is in full force and effect and whether such
party has any existing defenses or offsets against the enforcement of this
Lease; (b) whether this Lease has been assigned, modified, supplemented or
amended, and, if so, identifying and describing any such assignment,
modification, supplement or amendment; (c) the date to which Rent has been paid;
(d) whether the party to whom the request is directed knows of any default or
failure to perform conditions on the part of the other party hereunder, and if
so, specifying the nature thereof; and (e) that this Lease, as it may have been
modified, supplemented or amended, represents the entire agreement between the
parties as to this leasing.


<PAGE>   32

                  The failure of either party to issue such a certificate to the
requesting party or other specified Person within said twenty (20) day period
shall constitute an acknowledgment by the party to whom such request is directed
that this Lease is unmodified and in full force and effect and shall constitute,
as to any Person entitled to rely upon such certificate, a waiver of any
defaults that may exist prior to the date of such request. Such certificate
shall act as a waiver of any claim by the party furnishing such certificate to
the extent such claim is based upon facts which are contrary to those asserted
in the certificate but only to the extent the claim is asserted against a bona
fide encumbrancer or purchaser for value without knowledge of facts contrary to
those contained in the certificate and who has acted in reasonable reliance upon
the certificate. Such certificate shall in no event subject the party furnishing
it to any liability whatsoever, notwithstanding the negligent or inadvertent
failure of such party to disclose correct or relevant information.


<PAGE>   33

ARTICLE 40. GENERAL PROVISIONS

Section 40.1 Severability. In case any one or more of the provisions of this
Lease shall for any reason be held to be invalid, illegal or unenforceable in
any respect, such invalidity, illegality or unenforceability shall not affect
any other provision of this Lease, and this Lease shall be construed as if such
invalid, illegal or unenforceable provisions had not been contained herein.

Section 40.2 Headings. Article, Section and subsection headings in this Lease
are for convenience only and are not to be construed as a part of this Lease or
in any way limiting or amplifying the provisions hereof.

Section 40.3 Lease Construed as a Whole. The language in all parts of this Lease
shall in all cases be construed as a whole according to its fair meaning and not
strictly for or against either Lessor or Lessee. The parties acknowledge that
each party and its counsel have reviewed this Lease and participated in its
drafting and therefore that the rule of construction that any ambiguities are to
be resolved against the drafting party shall not be employed nor applied in the
interpretation of this Lease.

Section 40.4 Meaning of Terms. Whenever the context so requires, the neuter
gender shall include the masculine and the feminine, and the singular shall
include the plural, and vice versa. Any reference to a specific sum of money,
shall mean that amount of lawful money of the United States of America that
(except where the specific provision by its terms provides for adjustment to
reflect inflation) is the equivalent in value on the date such determination is
to be made under the relevant provision of this Lease, to the stated amount in
U.S. Dollars in the year of the Commencement Date: i.e. the stated amount
increased by the percentage increase equal to the cumulative percentage increase
in the CPI from January 1 of the year of the Commencement Date, to the date of
determination.

Section 40.5 Attorneys' Fees. In the event of any action or proceeding at law or
in equity between Lessor and Lessee to enforce or interpret any provision of
this Lease or to protect or establish any right or remedy of either party
hereunder, the party not prevailing in such action or proceeding shall pay to
the prevailing party all costs and expenses, including without limitation,
reasonable attorneys' fees and expenses (including attorneys' fees and expenses
of in-house attorneys), incurred therein by such prevailing party and if such
prevailing party shall recover judgment in any such action or proceeding, such
costs, expenses and attorneys' fees shall be included in and as a part of such
judgment.

Section 40.6 Binding Agreement. The terms, covenants and agreements contained in
this Lease shall bind and inure to the benefit of the parties hereto and their
respective successors and assigns.



<PAGE>   34

Section 40.7 Entire Agreement. This instrument, together with the exhibits
hereto, all of which are incorporated herein by reference, constitutes the
entire agreement between Lessor and Lessee with respect to the subject matter
hereof and supersedes all prior offers, negotiations, oral and written. This
Lease may not be amended or modified in any respect whatsoever except by an
instrument in writing signed by Lessor and Lessee.

Section 40.8 Quiet Enjoyment. Lessor agrees that Lessee, upon paying the Base
Monthly Rental, Additional Rental and all other sums due hereunder and upon
keeping and observing all of the covenants, agreement and provisions of this
Lease on its part to be observed and kept, shall, subject to the exceptions and
reservations referred to in Article 3, lawfully and quietly hold, occupy and
enjoy the Premises during the Term without hindrance or molestation by anyone
claiming by, through, or under Lessor.

Section 40.9 Termination Not Merger. The voluntary sale or other surrender of
this Lease by Lessee to Lessor, or a mutual cancellation thereof, or the
termination thereof by Lessor pursuant to any provision contained herein, shall
not work a merger, but at the option of Lessor shall either terminate any or all
existing subleases or subtenancies hereunder, or operate as an assignment to
Lessor of any or all of such subleases or subtenancies.

                  IN WITNESS WHEREOF, Lessor and Lessee have executed this Lease
by proper persons thereunto duly authorized as of the date first above written.



LESSOR:                             /s/ STEVE DOSTART
                                    --------------------------------
                                    475 Java Drive Associates, L.P.,
                                    a California Limited Partnership

                                   By: M-D Ventures, Inc.,
                                   its General Partner

                                   By: /s/
                                      ------------------------------

                                        Its: Vice President
                                            ------------------------


LESSEE:                            NETWORK APPLIANCE, INC.,
                                   a Delaware Corporation

                                   By: /s/ CHRIS CARLTON
                                      ------------------------------

                                        Its: Vice President
                                            ------------------------


<PAGE>   35

                                    Exhibit A

                            [Description of Premises]




<PAGE>   36

                                TABLE OF CONTENTS



''', None)
]

FIND_NUMBERS_TEST_DATA = [
    ('45.67', [45.67]),
    ('2,000 square feet', [2000.0]),
    ('.23, 45', [0.23, 45]),
    (': approximately 100,000 gross', [100000])
]

DEPOSIT_TEST_DATA = [
    ('''            As used herein, the term "LEASE MONTH" means each
                        calendar month during the Term (and if the Commencement
                        Date does not occur on the first day of a calendar
                        month, the period from the Commencement Date to the
                        first day of the next calendar month shall be included
                        in the first Lease Month for purposes of determining the
                        duration of the Term).

Security Deposit:       $49,000.00 due upon execution of the Lease as referenced
                        in Section 5 of the Lease.

Rent:                   Basic Rental, Tenant's share of Electrical Costs, Excess
                        (if any), and all other sums that Tenant may owe to
                        Landlord under the Lease.
''', {'security_deposit__set': {49000.0}}),
    ('''5. Security Deposit. Tenant shall deposit the sum of Thirty Two
Thousand Five Hundred Fifty Dollars ($32,550.00) (the "Security Deposit") upon
execution of this Lease, to secure the faithful performance by Tenant of each
term, covenant and condition of this Lease. If Tenant shall at any time fail to
make any payment or fail to keep or perform any term, covenant or condition on
its part to be made or performed or kept under this Lease, Landlord may, but
shall not be obligated to and without waiving or releasing Tenant from any
obligation under this Lease, use, apply or retain the whole or any part of the
Security Deposit (A) to the extent of any sum due to Landlord; (B) to make any
required payment on Tenant's behalf; or (C) to compensate Landlord for any loss,
damages, attorneys' fees or expense sustained by Landlord due to Tenant's
default. In such event, Tenant shall, within five (5) days of written demand by
Landlord, remit to Landlord sufficient funds to restore the Security Deposit to
its original sum. No interest shall accrue on the Security Deposit. Landlord
shall not be required to keep the Security Deposit separate from its general
funds. The Security Deposit, less any sums owing to Landlord or which Landlord
is otherwise entitled to retain, shall be returned to Tenant within thirty (30)
days after the termination of this Lease and vacancy of the Premises by Tenant.

''', {'security_deposit__set': {32550.0}})
]

RENT_DUE_FREQUENCY_TEST_DATA = [
    (''' 6.
 Rent.  Lessee agrees to pay Lessor rent in advance for the term of the Lease in the amount of $250,000.  The rent payment shall be
due upon execution of this Lease.
''', {'rent_due_frequency': 'total amount'}),
    ('''WITNESSETH THAT:   Lessor does hereby demise and let unto Lessee all that certain portion of the premises consisting of 6,126 +/- sq
uare feet identified as 480 Shoemaker Road Suite 104, hereinafter referred to as the "Demised Premises" and further described on the
 attached Exhibit "A" and being located in a 49,352 +/- square foot building  (the "Property"), in the Gulph Mills Business Center (
the "Business Center"), in the Township of Upper Merion, in the County of Montgomery, Commonwealth of Pennsylvania, to be used and o
ccupied as general office and warehouse space and for the mixing of ink technology and for no other purpose, for the term of five (5
) years and three (3) months (plus the period between the delivery date, if it falls on a day other than the first day of a month, a
nd the first day of the next month) (the "Term") commencing upon January 1, 2014 (the "Commencement Date"), with the minimum rent to
 be paid in accordance with the rent schedule herein, payable without deduction or setoff,  in monthly installments, in advance duri
ng the said Term of this Lease, on the first day of each month, with the first installment of minimum rent and additional rent to be
 paid at the time of signing this Lease (the "Rent").   The first rental payment to be made during the occupancy of the Demised Prem
ises shall be adjusted to pro-rate a partial month of occupancy, if any, at the inception of this Lease.
''', {'rent_due_frequency': 'monthly'}),
    ('''
    Total Rent for Year 1 shall be $24,000.00 payable in monthly installments
    of $2,000.00 in advance on the first day of each month during term hereof.
    The total amount due each month including estimated taxes, estimated utilities and rent
    shall be $2,446.66. Year 2 Rent shall increase by then CPI-U.
    ''', {'rent_due_frequency': 'monthly'})
]

PERIOD_RENT_AMOUNT_TEST_DATA = [
    ('''RENTAL SCHEDULE               MONTHLY/QUARTERLY/ANNUAL AMOUNT(S)
- ------------------------      ------------------------------------------
01/1/08 THROUGH 12/31/08      $200.00/per month(1); $600/per quarter(2);
                              $2,400/per year(3)
''', {'mean_rent_per_month__set': {200.00}}),
    ('''2.1  Tenant
      covenants and agrees to pay to Landlord, at its designated payment center
      at P.O. Box 18110, Newark, NJ 07191-8110, through-out the full term of
      this Lease, but subject to adjustments as hereinafter provided, an annual
      guaranteed basic rent ("Basic Rent") in the amount of Thirty-Four
      Thousand, Eight and 50/100 ( $34,008.50) DOLLARS, payable in equal monthly
      installments, of Two Thousand, Eight Hundred, Thirty-four and 04/100
      ($2,834.04) DOLLARS.''',
     {'mean_rent_per_month__set': {2834.04}}),
    ('''3. RENT. Lessee shall pay to Lessor rent in the
amount of Three Thousand Two Hundred and no/100 Dollars ($3,200.00) per month which rental amount shall be due and payable on or bef
ore the 10th day of each monthly period during the term of this Lease Agreement. Lessee shall pay to Lessor, as
additional rent, an amount equal to five percent (5%) of one (1) month's rent as a late penalty should Lessor not receive the monthl
y rental payment on or before such 30th da''', {'mean_rent_per_month__set': {3200.0}}),
    (''' a.      The
                                         Total Rent for Year 1 shall be $24,000.00 payable in monthly installments
                                         of $2,000.00 in advance on the first day of each month during term hereof.
                                         The total amount due each month including estimated taxes, estimated utilities and rent
                                         shall be $2,446.66. Year 2 Rent shall increase by then CPI-U.''',
     {'mean_rent_per_month__set': {2446.66, 2000.00}})
]


def test_detect_term():
    _test_field_extraction(TERM_TEST_DATA, ('start_end_term',))


def test_detect_lease_type():
    _test_field_extraction(LEASE_TYPE_TEST_DATA, ('lease_type',))


def test_detect_property_type():
    _test_field_extraction(PROPERTY_TYPE_TEST_DATA, ('property_type',))


def test_detect_permitted_use():
    _test_field_extraction(PERMITTED_USE_TEST_DATA, ('permitted_use',))


def test_detect_prohibited_use():
    _test_field_extraction(PROHIBITED_USE_TEST_DATA, ('prohibited_use',))


def test_performance():
    data = [('''Lessees
<PAGE> MASTER LEASE AGREEMENT
THIS MASTER LEASE AGREEMENT, dated as of February 1, 2002 (this "AGREEMENT"), between GENERAL ELECTRIC CAPITAL CORPORATION, FOR ITSELF AS LESSOR AND AS AGENT FOR LESSORS, with an office at 401 Merritt Seven, Second Floor, Norwalk, Connecticut 06856 (in its capacity as Agent, "AGENT"), and GALAXY INDUSTRIES CORPORATION, a Michigan corporation with its mailing address and chief place of business at 41150 Joy Road, Plymouth, MI 48170, MID STATE MACHINE PRODUCTS, a Maine corporation with its mailing address and chief place of business at 1501 Verti Drive, Winslow, Maine 04901, NATIONWIDE PRECISION PRODUCTS CORP., a New York corporation with its mailing address and chief place of business at 200 Tech Park Drive, Henrietta, New York 14623, GENERAL AUTOMATION, INC., an Illinois corporation with its mailing address and chief place of business at 3300 Oakton Street, Skokie, Illinois 60076, CERTIFIED FABRICATORS, INC., a California corporation with its mailing address and chief place of business at 6291 Burnham Avenue, Buena Park, California 90621, GILLETTE MACHINE & TOOL CO., INC., a New York corporation with its mailing address and chief place of business at 955 Millstead Way, Rochester, New York, 14624, GALAXY PRECISION PRODUCTS CORP., a Delaware corporation with its mailing address and chief place of business at 47440 Michigan Avenue, Canton, Michigan 48188, and PRECISION PARTNERS, INC., a Delaware corporation with its mailing address and chief place of business at 100 Village Court, Suite 301, Hazlet, New Jersey 07730 (hereinafter collectively called "LESSEES").
''', {})]
    _test_field_extraction(data)


def test_non_renew_notice():
    _test_field_extraction(NON_RENEW_NOTICE_TEST_DATA, ('renew_non_renew_notice',))


def test_detect_address_default():
    for text, expected in ADDRESSES_TEST_DATA:
        sentences = get_sentence_list(text)
        actual = detect_address_default(text, sentences)
        print('Actual: {0}\nExpected: {1}'.format(actual, expected))
        assert_equal(actual, expected) if actual and expected else assert_true(
            actual is None and expected is None)


def test_find_numbers():
    for text, expected in FIND_NUMBERS_TEST_DATA:
        actual = find_numbers(text)
        actual = list(actual) if actual else []
        print('Actual: {0}\nExpected: {1}'.format(actual, expected))
        assert_list_equal(actual, expected)


def test_security_deposit():
    _test_field_extraction(DEPOSIT_TEST_DATA, ('security_deposit',))


def test_rent_due_frequency():
    _test_field_extraction(RENT_DUE_FREQUENCY_TEST_DATA, ('rent_due_frequency',))


def test_period_rent_amount():
    _test_field_extraction(PERIOD_RENT_AMOUNT_TEST_DATA, ('mean_rent_per_month',))
