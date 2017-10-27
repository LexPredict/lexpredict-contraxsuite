import regex as re
import string

# from lexnlp.extract.en.money import get_money
from lexnlp.extract.en.definitions import get_definitions
from lexnlp.extract.en.entities.nltk_maxent import get_companies, get_organizations, get_persons
from lexnlp.extract.en.money import get_money
from lexnlp.extract.en.dates import get_dates, get_date_features
from lexnlp.extract.en.entities.nltk_re import get_parties_as
from lexnlp.extract.en.utils import strip_unicode_punctuation
from sklearn.metrics.pairwise import cosine_similarity

TRIGGER_LIST_COMPANY = ["corporation", "company", "employer"]
TRIGGER_LIST_EMPLOYEE = ["employee", "executive"]
non_compete_samples=["""(b) Noncompetition. The Executive agrees that during the period of the Executive’s employment with the Company, the period, if any, during which the Executive is receiving payments from the Company pursuant to Section 4, and for a period of two years thereafter the Executive shall not in any manner, directly or indirectly, through any person, firm or corporation, alone or as a member of a partnership or as an officer, director, stockholder, investor or employee of or consultant or other agent to any other corporation or enterprise or otherwise, engage or be engaged, or assist any other person, firm, corporation or enterprise in engaging or being engaged, in any business, in which the Executive was involved or had knowledge, being conducted by, or contemplated by, the Company or any of its subsidiaries as of the termination of the Executive’s employment in any geographic area in which the Company, any of its subsidiaries or the Parent is then conducting or is contemplating conducting such business.""",
                     """(ii) During the Noncompetition Period, in the Territory, solicit, cause or authorize, directly or indirectly, to be solicited for or on behalf of herself or third parties, from parties who are or were customers of the Company or its Subsidiaries, any Edgewater Services Business transacted by or with such customer by the Company or its Subsidiaries; or""",
                     """employ of Aleris, the Company or its affiliates, or solicit, hire or engage on behalf of himself or any other Person (as defined below) any employee of Aleris or the Company or anyone who was employed by Aleris or the Company during the six-month period preceding such hiring or engagement. 8. Confidentiality; Non-Compete; Non-Disclosure; Non-Disparagement. (a) The Executive hereby agrees that, during the Employment Period and thereafter, he will hold in strict confidence any proprietary or Confidential Information related to Aleris, the Company and its affiliates. For purposes of this Agreement, the term “Confidential Information” shall mean all information of Aleris, the Company or any of its affiliates (in whatever form) which is not generally known to the public, including without limitation any inventions, processes, methods of distribution, customer lists or customers’ or trade secrets. (b) The Executive and the Company agree that Aleris, the Company and its affiliates would likely suffer significant harm from the Executive’s competing with Aleris, the Company or its affiliates during the Employment Period and for some period of time thereafter. Accordingly, the Executive agrees that he will not, during the Employment Period and for a period of twelve months following the termination of the Employment Period, directly or indirectly, become employed by, engage in business with, serve as an agent or consultant to, become a partner, member, principal, stockholder or other owner (other than a holder of less than 1% of the outstanding voting shares of any publicly held company) of, any Person competitive with, or otherwise perform services relating to, the business of Aleris, the Company or its affiliates at the time of the termination for any Person (the “Business”) (whether or not for compensation). For purposes of this Agreement, the term “Person” shall mean any individual, partnership, corporation, limited liability company, unincorporated organization, trust or joint venture, or a governmental agency or political subdivision thereof that is engaged in the Business, or otherwise competes with Aleris, the Company or its affiliates, anywhere in which Aleris, the Company or its affiliates engage in or intend to engage in the Business or where Aleris, the Company or its affiliates’ customers are located. (c) The Executive hereby agrees that, upon the termination of the Employment Period, he shall not take, without the prior written consent of the Company, any drawing, blueprint, specification or other document (in whatever form) of the Company or its affiliates, which is of a confidential nature relating to Aleris, the Company or its affiliates, or, without limitation, relating to its or their methods of distribution, or any description of any formulas or secret processes and will return any such information (in whatever form) then in his possession. (d) The Executive hereby agrees not to defame or disparage Aleris, the Company, its affiliates and their officers, directors, members or executives. The Executive hereby agrees to cooperate with Aleris, the Company and its affiliates in refuting any defamatory or disparaging remarks by any third party made in respect of Aleris, the Company or its affiliates or their directors, members, officers or executives.""",
                     """reason, the Employee shall not directly or indirectly do any of the following without the consent of a Company executive, ratified by the Board of Directors: 8.2.1 Solicit or accept any business similar to that provided by the Company from a person, firm or corporation that is a customer of the Company during the time the Employee is employed by the Company; and""",
                     """8.1 The Employee, recognizing the high level of trust and authority and the unique access to Company Proprietary Information to which he is being afforded by the Company, in exchange covenants and agrees that he will not during the term of employment and for a period of one year thereafter, on behalf of himself or on behalf of any other person or business entity or enterprise directly or indirectly as an employee, proprietor, stockholder, partner, consultant or otherwise, engage in any business or activity competitive with the business activities or the Company or its affiliates as they now are or hereafter undertaken by the Company.""",
                     """(a) Employee acknowledges that in the course of her employment by the Company he has and will become privy to various economic and trade secrets and relationships of the Company and its subsidiaries under its direct control ("Subsidiaries"). Therefore, in consideration of this Agreement, Employee hereby agrees that he will not, directly or indirectly, except for the benefit of the Company or its Subsidiaries, or with the prior written consent of the Board of Directors of the Company, which consent may be granted or withheld at the sole discretion of the Company's Board of Directors: (i) During the Noncompetition Period (as hereinafter defined), become an officer, director, stockholder, partner, member, manager, associate, employee, owner, creditor, independent contractor, co- venturer, consultant or otherwise, or be interested in or associated with any other person, corporation, firm or business engaged in providing software solutions services, including but not limited to, systems integration, custom software development, training, systems support, outsourcing and/or information technology consulting services (an "Edgewater Services Business") within a radius of fifty (50) miles from any office operated during the Noncompetition Period by the Company, or any of its Subsidiaries (collectively, the "Territory") or in any Edgewater Services Business directly competitive with that of the Company, or any of its Subsidiaries, or itself engage in such business; provided, however, that"""]


# Employee or Executive is found as a definition in the sentence
# there is a person (get_persons) who is not also a company - that is the employee
def get_employee_name(text, return_source=False):
    definitions = list(get_definitions(text))

    found_employees = []
    defined_employee_found = False
    for d in definitions:
        if d.lower() in TRIGGER_LIST_EMPLOYEE:
            defined_employee_found = True
            break

    if (defined_employee_found):
        persons = list(get_persons(text))
        companies = list(get_companies(text))
        for p in persons:
            person_is_a_company = False
            for c in companies:
                # persons and companies return slightly different values for same text
                # so need to standardize to compare
                company_full_string = str(c[0].lower().strip(string.punctuation).replace(" ", "").replace(",", "")
                                          + c[1].lower().strip(string.punctuation).replace(" ", "").replace(",",
                                                                                                            ""))
                employee_full_string = str(p.lower().strip(string.punctuation).replace(" ", "").replace(",", ""))
                if (employee_full_string == company_full_string):
                    person_is_a_company = True
                    break
            if (not person_is_a_company):
                found_employees.append(p)

    if (return_source):
        yield (found_employees, text)
    else:
        yield found_employees


# Case 1 Find definition of employee and employer in sentence return company found.
# this doesn't handle more than one company in the same employee/employer definition sentence
def get_employer_name(text, return_source=False):
    definitions = list(get_definitions(text))

    companies = []
    defined_employer_found = False
    defined_employee_found = False

    for d in definitions:
        if d.lower() in TRIGGER_LIST_COMPANY:
            defined_employer_found = True
        if d.lower() in TRIGGER_LIST_EMPLOYEE:
            defined_employee_found = True
        if defined_employee_found == True and defined_employer_found == True:
            break

    if (defined_employer_found and defined_employee_found):
        companies = list(get_companies(text))

    if (return_source):
        yield (companies, text)
    else:
        yield companies

#TODO- group parts of sentence so can separate when it is like this:
# "Your bi-weekly rate of pay will be $7,403.85, which is the equivalent of an annual rate of $192,500, based on a 40-hour workweek."
def get_salary(text, return_source=False):
    TRIGGER_LIST_SALARY = ["salary", "rate of pay"]
    # text to be found and multiplier to get yearly
    TRIGGER_LIST_TIME_UNIT = [("per annum", 1), ("yearly", "1"), ("per year", "1"),
                              ("bi-weekly", "26"), ("monthly", "12")]
    found_time_unit = 0
    money=[]
    for t in TRIGGER_LIST_TIME_UNIT:
        if (findWholeWordorPhrase(t[0])(text)) is not None:
            found_time_unit = t[1]
            break

    if (found_time_unit):
        money = get_money(text)
    if (return_source):
        yield (money, found_time_unit, text)
    else:
        yield (money, found_time_unit)

def get_effective_date(text, return_source=False):
    # Trigger List Start Date should be followed by the start of the date as picked up by get_dates
    TRIGGER_LIST_START_DATE=["dated as of", "effective as of"]
    EXCLUDE_LIST_START_DATE=["amends"]
    found_start_date_trigger= False
    found_start_date_excluder=False
    dates=[]

    for t in TRIGGER_LIST_START_DATE:
        if findWholeWordorPhrase(t)(text) is not None:
            found_start_date_trigger=True
            break
    for e in EXCLUDE_LIST_START_DATE:
        if findWholeWordorPhrase(e)(text) is not None:
            found_start_date_excluder=True
            break

    if (found_start_date_trigger and not found_start_date_excluder):
        dates = get_dates(text)
    if(return_source):
        yield (dates, text)
    else:
        yield(dates)


#def check_is_non_compete(text_unit, sample_set=non_compete_samples, similarity_threshold=.75):

#TODO See if there is a better way than copying text unit similariy- see tasks-tasks.py-similarity

def findWholeWordorPhrase(w):
    w = w.replace(" ", r"\s+")
    return re.compile(r'\b({0})\b'.format(w), flags=re.IGNORECASE).search



#text = """This Amendment, dated as of March 9, 2004, amends the Employment Agreement, entered into as of March 11, 2000 and amended as of November 20, 2002 (as so amended, the "Agreement"), by and between Joseph R. Martin (the "Executive") and Fairchild Semiconductor Corporation, a Delaware corporation (the "Corporation”)"""
#p = list(get_effective_date(text))
#print(p)