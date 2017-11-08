import regex as re
import string
import gensim.models.word2vec
import os

# from lexnlp.extract.en.money import get_money
from lexnlp.extract.en.definitions import get_definitions
from lexnlp.extract.en.entities.nltk_maxent import get_companies, get_persons, get_geopolitical
from lexnlp.extract.en.money import get_money
from lexnlp.extract.en.dates import get_dates
from lexnlp.extract.en.durations import get_durations
from lexnlp.extract.en.entities.nltk_re import get_parties_as
from lexnlp.extract.en.utils import strip_unicode_punctuation
from sklearn.metrics.pairwise import cosine_similarity
from lexnlp.nlp.en.tokens import get_stems
from django.conf import settings




TRIGGER_LIST_COMPANY = ["corporation", "company", "employer"]
TRIGGER_LIST_EMPLOYEE = ["employee", "executive"]
FALSE_PEOPLE=["agreement", "addendum"] #get_persons wrongly returns a bunch of these - exclude for now. TODO as about if can improve get_persons
TRIGGER_LIST_TIME_UNIT = [("per annum", 1), ("yearly", 1), ("per year", 1),
                          ("bi-weekly", 26), ("monthly", 12), ("annually", 1), ("per month", 12)]

#below words determine if it is definately a non-compete/termination or definately not a non-compete/termination
# and are used to fetch similar words via w2v
non_compete_positive_words=["competit", "noncompetit"]
non_compete_negative_words=[]
termination_positive_words=["termin"]
termination_negative_words=[]
benefits_positive_words=["benefit", "disabl", "stock", "pension", "insur"]
benefits_negative_words=["termin"] #exclude clauses where saying you don't get benefits cause terminated




# Employee or Executive is found as a definition in the sentence
# there is a person (get_persons) who is not also a company - that is the employee
# Return list of all potential "Employees"
def get_employee_name(text, return_source=False):
    definitions = list(get_definitions(text))

    found_employee = None
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
            fake_person= str(p).lower() in FALSE_PEOPLE
            if not fake_person:
                for c in companies:
                    # persons and companies return slightly different values for same text
                    # so need to standardize to compare
                    if len(c)>0:
                        if(c[1] is not None and c[0] is not None):
                            company_full_string = str(c[0].lower().strip(string.punctuation).replace(" ", "").replace(",", "")
                                                  + c[1].lower().strip(string.punctuation).replace(" ", "").replace(",",""))
                        else:
                            company_full_string=str(c[0].lower().strip(string.punctuation).replace(" ", "").replace(",", ""))

                        employee_full_string = str(p.lower().strip(string.punctuation).replace(" ", "").replace(",", ""))
                        if (employee_full_string == company_full_string or
                            #handle this- where get_companies picks up more surrounding text than get_persons: EMPLOYMENT AGREEMENT WHEREAS, Kensey Nash Corporation, a Delaware corporation (the “Company”) and Todd M. DeWitt (the “Executive”) entered into that certain Amended and Restated Employment Agreement,...
                            employee_full_string in company_full_string):
                                person_is_a_company = True
            if (not person_is_a_company and not fake_person):
                found_employee=str(p)
                break #take first person found meeting our employee criteria

    if (return_source):
        return (found_employee, text)
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
    first_company_string=None

    for d in definitions:
        if d.lower() in TRIGGER_LIST_COMPANY:
            defined_employer_found = True
        if d.lower() in TRIGGER_LIST_EMPLOYEE:
            defined_employee_found = True
        if defined_employee_found == True and defined_employer_found == True:
            break

    if (defined_employer_found and defined_employee_found):
        companies = list(get_companies(text))
        if(len(companies)>0):
            first_company_string= ', '.join(str(s) for s in companies[0]) #take first employer found

    if (return_source):
        return (first_company_string, text)
    else:
        return first_company_string

#TODO- group parts of sentence so can separate when it is like this:
# "Your bi-weekly rate of pay will be $7,403.85, which is the equivalent of an annual rate of $192,500, based on a 40-hour workweek."
def get_salary(text, return_source=False):
    TRIGGER_LIST_SALARY = ["salary", "rate of pay"]
    # text to be found and multiplier to get yearly
    found_time_unit = None
    money=None
    for t in TRIGGER_LIST_TIME_UNIT:
        if (findWholeWordorPhrase(t[0])(text)) is not None:
            found_time_unit = t[1]
            break

    if found_time_unit is not None:
        found_money= list(get_money(text))
        if(len(found_money)>0):
            money = found_money[0] #took just the first time unit- so also just take first money
    if money is not None:
        if (return_source):
            return (money, found_time_unit, text)
        else:
            return (money, found_time_unit)
    else:
        return None

#get duration- per unit- and the words "vacation" or "paid time off"
def get_vacation_duration(text, return_source=False):
    found_time_unit=None
    duration=None
    found_vacation_trigger=False
    TRIGGER_LIST_VACATION= ["vacation", "paid time off"]
    for v in TRIGGER_LIST_VACATION:
        if(findWholeWordorPhrase(v)(text)) is not None:
            found_vacation_trigger=True
            break
    if found_vacation_trigger:
        for t in TRIGGER_LIST_TIME_UNIT:
            if(findWholeWordorPhrase(t[0])(text)) is not None:
                found_time_unit= t[1]
                break
        if found_time_unit is not None:
            found_duration=list(get_durations(text))
            if len(found_duration)>0:
                duration=found_duration[0] #take first duration
            if return_source:
                return (duration, found_time_unit, text)
            else:
                return (duration, found_time_unit)
    else:
        return None

def get_governing_geo(text, return_source=False):
    TRIGGER_lIST_GOVERNING=["governed by", "governing law"]
    found_governing=False
    geo_entity=None
    for g in TRIGGER_lIST_GOVERNING:
        if(findWholeWordorPhrase(g)(text)) is not None:
            found_governing=True
            break
    if found_governing:
        found_geo_entities= list(get_geopolitical(text))
        if len(found_geo_entities)>0:
            geo_entity= found_geo_entities[0] #take first geo_entity
    if return_source:
        return (geo_entity, text)
    else:
        return geo_entity




def get_effective_date(text, return_source=False):
    # need a better more accurate way of doing this
    # right now looks for triggers and takes latest date in that sentence
    TRIGGER_LIST_START_DATE=["dated as of", "effective as of", "made as of", "entered into as of"]
    found_start_date_trigger= False
    effective_date=None

    for t in TRIGGER_LIST_START_DATE:
        if findWholeWordorPhrase(t)(text) is not None:
            found_start_date_trigger=True
            break

    if (found_start_date_trigger):
        dates = list(get_dates(text))
        if len(dates) >0:
            effective_date= max(dates)
    if(return_source):
        return (effective_date, text)
    else:
        return(effective_date)

def get_similar_to_terms_employee(text, positives,
                         negatives):
    """Use Employment Agreement W2V to get terms similar to those provided and search text for those"""
    stems = get_stems(text)
    positive_found=False
    negative_found=False
    dir_path = os.path.dirname(os.path.realpath(__file__))



    for p in positives:
        if p in stems:
            positive_found=True
    if positive_found:
        for n in negatives:
            if n in stems:
                negative_found=True
    if positive_found and not negative_found:
        return 1

    w2v_model = gensim.models.word2vec.Word2Vec.load(dir_path+ "/w2v_cbow_employment_size200_window10")
    trained_similar_words= w2v_model.wv.most_similar(positive=positives,
                                                     negative=negatives)

    trained_similar_words= dict(trained_similar_words)

    sum_similarity=0
    num_similars=0
    for i in stems:
        if trained_similar_words.get(i) is not None:
            sum_similarity= sum_similarity+ trained_similar_words[i]
            num_similars=num_similars+1
    if num_similars is not 0:
        return sum_similarity/num_similars
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

def findWholeWordorPhrase(w):
    w = w.replace(" ", r"\s+")
    return re.compile(r'\b({0})\b'.format(w), flags=re.IGNORECASE).search

