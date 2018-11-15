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

import gensim.models.word2vec
import os
import pickle
import regex as re
import string

# from lexnlp.extract.en.money import get_money
from lexnlp.extract.en.definitions import get_definitions
from lexnlp.extract.en.entities.nltk_maxent import get_companies, get_persons, get_geopolitical
from lexnlp.extract.en.money import get_money
from lexnlp.extract.en.dates import get_dates
from lexnlp.extract.en.durations import get_durations
from lexnlp.nlp.en.tokens import get_stems

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2018, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.1.5a/LICENSE"
__version__ = "1.1.5a"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"

TRIGGER_LIST_COMPANY = ["corporation", "company", "employer"]
TRIGGER_LIST_EMPLOYEE = ["employee", "executive"]
FALSE_PEOPLE = ["agreement", "addendum",
                "article"]  # get_persons wrongly returns a bunch of these - exclude for now. TODO as about if can improve get_persons
TRIGGER_LIST_TIME_UNIT = [("per annum", 1), ("annual", 1), ("yearly", 1), ("per year", 1), ("year", 1),
                          ("bi-weekly", 26), ("monthly", 12), ("annually", 1), ("per month", 12)]

# below words determine if it is definately a non-compete/termination
# or definately not a non-compete/termination
# and are used to fetch similar words via w2v
non_compete_positive_words = ["competit", "noncompetit"]
non_compete_negative_words = []
termination_positive_words = ["termin"]
termination_negative_words = []
benefits_positive_words = ["benefit", "disabl", "stock", "pension", "insur"]
# exclude clauses where saying you don't get benefits cause terminated
benefits_negative_words = ["termin"]
severance_positive_words = ["sever"]
severance_negative_words = []


def clean(text):
    return text.lower().strip(string.punctuation).replace(" ", "").replace(",", "")


# Employee or Executive is found as a definition in the sentence
# there is a person (get_persons) who is not also a company - that is the employee
# Return list of all potential "Employees"
def get_employee_name(text, return_source=False):
    definitions = list(get_definitions(text))
    fake_person = False
    found_employee = None
    defined_employee_found = False
    for d in definitions:
        if d.lower() in TRIGGER_LIST_EMPLOYEE:
            defined_employee_found = True
            break

    if defined_employee_found:
        persons = list(get_persons(text))
        companies = list(get_companies(text))
        for p in persons:
            person_is_a_company = False
            for f in FALSE_PEOPLE:
                if f in str(p).lower():
                    fake_person = True
            if not fake_person:
                for c in companies:
                    # persons and companies return slightly different values for same text
                    # so need to standardize to compare
                    if len(c) > 0:
                        if c[1] is not None and c[0] is not None:
                            company_full_string = str(clean(c[0]) + clean(c[1]))
                        else:
                            company_full_string = str(clean(c[0]))

                        employee_full_string = str(clean(p))
                        # handle this- where get_companies picks up more surrounding text
                        # than get_persons: EMPLOYMENT AGREEMENT WHEREAS, Kensey Nash Corporation,
                        # a Delaware corporation (the “Company”) and Todd M. DeWitt
                        # (the “Executive”) entered into that certain Amended
                        # and Restated Employment Agreement,...
                        if (employee_full_string == company_full_string or
                                    employee_full_string in company_full_string):
                            person_is_a_company = True

            if not person_is_a_company and not fake_person:
                found_employee = str(p)
                # take first person found meeting our employee criteria
                break
            fake_person = False  # reset for next person

    if return_source:
        return found_employee, text
    else:
        return found_employee


# Case 1 Find definition of employee and employer in sentence return company found.
# this doesn't handle more than one company in the same employee/employer definition sentence
# First instance of this is fine since this is generally the first sentence
def get_employer_name(text, return_source=False):
    definitions = list(get_definitions(text))

    companies = []
    defined_employer_found = False
    defined_employee_found = False
    first_company_string = None

    for d in definitions:
        if d.lower() in TRIGGER_LIST_COMPANY:
            defined_employer_found = True
        if d.lower() in TRIGGER_LIST_EMPLOYEE:
            defined_employee_found = True
        if defined_employee_found is True and defined_employer_found is True:
            break

    if defined_employer_found and defined_employee_found:
        companies = list(get_companies(text))
        if len(companies) > 0:
            # take first employer found
            first_company_string = ', '.join(str(s) for s in companies[0])

    if return_source:
        return first_company_string, text
    else:
        return first_company_string


# "Your bi-weekly rate of pay will be $7,403.85, which is the equivalent of an annual rate of $192,500, based on a 40-hour workweek."
# For above- pair min time unit number with max money number.
def get_salary(text, return_source=False):
    TRIGGER_LIST_SALARY = ["salary", "rate of pay"]
    # text to be found and multiplier to get yearly
    found_time_unit = None
    found_time_units = []
    found_salary_trigger = False
    money = None
    min_annual_salary = 20000  # sample is mostly executives- so this is safe.
    for t in TRIGGER_LIST_SALARY:
        if findWholeWordorPhrase(t)(text) is not None:
            found_salary_trigger = True
            break
    if found_salary_trigger:
        for t in TRIGGER_LIST_TIME_UNIT:
            found_time_unit_temp = findWholeWordorPhrase(t[0])(text)
            if found_time_unit_temp is not None:
                found_time_units.append(t[1])
        if len(found_time_units) > 0:
            found_time_unit = min(found_time_units)
            found_money = list(get_money(text))
            if len(found_money) > 0:
                money_temp = max(found_money, key=lambda item: item[0])
                if money_temp[0] * found_time_unit > min_annual_salary:
                    money = money_temp
    if money is not None:
        if return_source:
            return money, found_time_unit, text
        else:
            return money, found_time_unit
    else:
        return None


# get duration- per unit- and the words "vacation" or "paid time off"
def get_vacation_duration(text, return_source=False):
    found_time_unit = None
    duration = None
    found_vacation_trigger = False
    TRIGGER_LIST_VACATION = ["vacation", "paid time off"]

    for v in TRIGGER_LIST_VACATION:
        if (findWholeWordorPhrase(v)(text)) is not None:
            found_vacation_trigger = True
            break
    if found_vacation_trigger:
        for t in TRIGGER_LIST_TIME_UNIT:
            if (findWholeWordorPhrase(t[0])(text)) is not None:
                found_time_unit = t[1]
                break
        if found_time_unit is not None:
            found_duration = list(get_durations(text))
            if len(found_duration) > 0:
                # take first duration
                duration = found_duration[0]
            if return_source:
                return duration, found_time_unit, text
            else:
                return duration, found_time_unit
    else:
        return None


def get_governing_geo(text, return_source=False):
    TRIGGER_lIST_GOVERNING = ["governed", "governing law"]
    found_governing = False
    geo_entity = None
    for g in TRIGGER_lIST_GOVERNING:
        if (findWholeWordorPhrase(g)(text)) is not None:
            found_governing = True
            break
    if found_governing:
        found_geo_entities = list(get_geopolitical(text))
        if len(found_geo_entities) > 0:
            # take first geo_entity
            geo_entity = found_geo_entities[0]
    if return_source:
        return geo_entity, text
    else:
        return geo_entity


def get_effective_date(text, return_source=False):
    # need a better more accurate way of doing this
    # right now looks for triggers and takes latest date in that sentence
    TRIGGER_LIST_START_DATE = ["dated as of", "effective as of", "made as of", "entered into as of"]
    found_start_date_trigger = False
    effective_date = None

    for t in TRIGGER_LIST_START_DATE:
        if findWholeWordorPhrase(t)(text) is not None:
            found_start_date_trigger = True
            break

    if found_start_date_trigger:
        dates = list(get_dates(text))
        if len(dates) > 0:
            effective_date = max(dates)
    if return_source:
        return effective_date, text
    else:
        return effective_date


def get_similar_to_terms_employee(text, positives, negatives):
    """
    Use Employment Agreement W2V to get terms similar
    to those provided and search text for those
    """
    stems = get_stems(text)
    positive_found = False
    negative_found = False
    dir_path = os.path.dirname(os.path.realpath(__file__))

    for p in positives:
        if p in stems:
            positive_found = True
    if positive_found:
        for n in negatives:
            if n in stems:
                negative_found = True
    if positive_found and not negative_found:
        return 1

    w2v_model = gensim.models.word2vec.Word2Vec.load(
        os.path.normpath(os.path.join(dir_path, "data/w2v_cbow_employment_size200_window10")))
    trained_similar_words = w2v_model.wv.most_similar(positive=positives,
                                                      negative=negatives)

    trained_similar_words = dict(trained_similar_words)

    sum_similarity = 0
    num_similars = 0
    for i in stems:
        if trained_similar_words.get(i) is not None:
            sum_similarity = sum_similarity + trained_similar_words[i]
            num_similars += 1
    if num_similars is not 0:
        return sum_similarity / num_similars
    else:
        return 0


def get_similar_to_non_compete(text, non_compete_positives=non_compete_positive_words,
                               non_compete_negatives=non_compete_negative_words):
    return get_similar_to_terms_employee(text, non_compete_positives, non_compete_negatives)


def get_similar_to_termination(text, termination_positives=termination_positive_words,
                               termination_negatives=termination_negative_words):
    return get_similar_to_terms_employee(text, termination_positives, termination_negatives)


def get_similar_to_benefits(text, benefits_positives=benefits_positive_words,
                            benefits_negatives=benefits_negative_words):
    return get_similar_to_terms_employee(text, benefits_positives, benefits_negatives)


def get_similar_to_severance(text, severance_positives=severance_positive_words,
                             severance_negatives=severance_negative_words):
    return get_similar_to_terms_employee(text, severance_positives, severance_negatives)


def findWholeWordorPhrase(w):
    w = w.replace(" ", r"\s+")
    return re.compile(r'\b({0})\b'.format(w), flags=re.IGNORECASE).search


def is_employment_doc(text,
                      path=None,
                      model=None,
                      true_value=1):
    """
    Detect if text is employment document
    """
    if model is None:
        if path is None:
            path = os.path.join(
                os.path.dirname(os.path.realpath(__file__)),
                'data/doc_detector_svm_model.pickle')
        model = pickle.load(open(path, 'rb'))
    return model.predict([text]) == true_value
