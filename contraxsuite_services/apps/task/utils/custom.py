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
# Standard imports
import re
import string

# NLTK and textract imports
import nltk
import nltk.tokenize.punkt
from nltk import SpaceTokenizer
from textract import process as textract_process

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2018, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.0.5/LICENSE"
__version__ = "1.0.7"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


def doc2text(path, language='eng'):
    """
    Simple doc2text method.
    :param path:
    :param language:
    :return:
    """
    # extract text as bytes
    text = textract_process(path, method='tesseract', language=language)
    # convert to string
    text = text.decode('utf-8')
    # process text - remove extra symbols, etc.
    # text = re.sub(r'\s*\n+\s*', '\n', text)
    return text


entity_blacklist = [
    'abia', 'acre', 'ain', 'apac', 'arad', 'ards', 'arta', 'aude',
    'aur', 'bago', 'bam', 'bar', 'bay', 'bled', 'boe', 'bury',
    'central', 'centre', 'cher', 'chin', 'clare', 'coast', 'como',
    'creuse', "dar'a", 'derry', 'down', 'ealing', 'east', 'eastern',
    'eger', 'enna', 'est', 'eua', 'eure', 'ewa', 'faro', 'feni',
    'fier', 'gard', 'gers', 'goa', 'gulf', 'ha', 'has', 'ibb',
    'ica', 'ig', 'ilan', 'imo', 'kent', 'kosi', 'kumi', 'lae',
    'lakes', 'lara', 'lib', 'lija', 'lima', 'lira', 'lodi', 'lofa',
    'lory', 'lot', 'maio', 'male', 'mary', 'mat', 'mie', 'mila',
    'mili', 'mon', 'mono', 'most', 'nara', 'natore', 'north',
    'north central', 'north-east', 'north-west', 'north-western',
    'northern', 'nui', 'oio', 'olt', 'oman', 'ondo', 'oran',
    'orne', 'osh', 'oslo', 'oyo', 'para', 'paul', 'pest', 'pita',
    'pool', 'poole', 'qax', 'qom', 'raa', 'reading', 'rize',
    'roma', 'ruse', 'sal', 'south', 'south west', 'south-western',
    'southern', 'sul', 'tarn', 'trat', 'tui', 'unity', 'uri',
    'uvs', 'van', 'vas', 'west', 'west coast', 'western', 'xizi',
    'yala', 'yap', 'yonne', 'zou', 'zug']


def get_entity_noun_phrase(text, entity_type):
    """
    NLTK noun phrase extractor convenience method.
    :param text:
    :param entity_type:
    :return:
    """
    p0 = 0
    p1 = None

    pos_list = nltk.pos_tag(nltk.word_tokenize(text))
    for i, _ in enumerate(pos_list):
        if i > 0:
            if pos_list[i][1] == "NNP" and pos_list[i - 1][1] != "NNP":
                p0 = i
            elif pos_list[i][1] != "NNP" and pos_list[i - 1][1] == "NNP":
                p0 = None
        if pos_list[i][0].lower() == entity_type.lower() and pos_list[i][1] == 'NNP':
            p1 = i + 1
            break

    if p0 is not None and p1 is not None:
        entity_noun_phrase = " ".join([x[0] for x in pos_list[p0:p1]])
        return entity_noun_phrase
    else:
        return None


party_type_ptns = {
    r"corp(?:\W|$|oration)": "CORP",
    r"inc(?:\W|$)": "INC",
    r"Limited Liability Company": "LLC",
    r"(?:llc|l\.l\.c)(?:\W|$)": "LLC",
    r"(?:llp|l\.l\.p)(?:\W|$)": "LLP",
    r"(?:lp|l\.p)(?:\W|$)": "LP",
    r"(?:lllp|l\.l\.l\.p)(?:\W|$)": "LLLP",
    r"(?:pllc|p\.l\.l\.c)(?:\W|$)": "PLLC",
    r"(?:plc|p\..l\.c)(?:\W|$)": "PLC",
    r"p\.c(?:\W|$)": "PC",
    r"(?:gmbh|g\.m\.b\.h)(?:\W|$)": "GMBH",
    r"ab(?:\W|$)": "AB",
    r"a\.?g(?:\W|$)": "AB",
    r"ltd(?:\W|$)": "LTD",
    r"s\.?a(?:\W|$)": "SA",
    r"trust(?:\W|$)": "TRUST",
}

tokenizer = SpaceTokenizer()
party_ptn = re.compile(r'.+?[\s,]+(?:%s)' % '|'.join(party_type_ptns), flags=re.I)
party_type_ptn = re.compile(r'\s+(?:%s)' % '|'.join(party_type_ptns), flags=re.I)
clean_party_type_ptn = re.compile(r'(?:\W|ORATION)')
clean_party_name_end_ptn = re.compile(r'\s*\([^\)]+(?:\)\W*)?$')
clean_party_name_start_ptn = re.compile(r'^\s*\([^\)]+\)\s*')


def get_cleaned_party(noun_phrase):
    """
    NLTK clean party name extractor
    :param noun_phrase:
    :return:
    """
    # search parties in noun_phrase like
    # "SES AMERICOM CALIFORNIA INC SES AMERICOM COLORADO INC"
    party_search = party_ptn.findall(noun_phrase)
    cleaned_parties = []
    for item in party_search:
        type_search = party_type_ptn.findall(item)
        if re.match(party_type_ptn, ' %s' % item) or not type_search:
            continue
        party_type = type_search[0]
        cleaned_party_type = clean_party_type_ptn.sub('', party_type.upper())
        # normalize party type in party name
        cleaned_party_name = item.replace(party_type.strip(), cleaned_party_type).upper().strip()
        # replace text in ()
        cleaned_party_name = clean_party_name_start_ptn.sub('', cleaned_party_name)
        cleaned_party_name = clean_party_name_end_ptn.sub('', cleaned_party_name)
        # remove text after party type
        party_name_parts = cleaned_party_name.split(r'\s+%s' % cleaned_party_type)
        if len(party_name_parts) == 2:
            cleaned_party_name = cleaned_party_name.replace(party_name_parts[1], '')
        # delete extra spaces
        cleaned_party_name = ' '.join(cleaned_party_name.replace(',', '').strip().split())
        # do not consider if party name == party type
        if cleaned_party_name == cleaned_party_type:
            continue
        cleaned_parties.append((cleaned_party_name, cleaned_party_type))
    return cleaned_parties


def extract_nnp_phrases(text):
    """
    NNP extractor convenience method.
    :param text:
    :return:
    """
    phrase_list = []

    for sentence in nltk.sent_tokenize(text):
        # Get POS
        tokens = nltk.word_tokenize(sentence)
        pos = nltk.pos_tag(tokens)

        # Get POS
        phrase = []

        for t, p in pos:
            if p in ["NNP", "NNPS"] or t in [",", "&"]:
                phrase.append(t)
            else:
                if len(phrase) > 1:
                    phrase_list.append(clean_nnp_phrase(phrase))
                phrase = []

    return phrase_list


def clean_nnp_phrase(phrase):
    """
    NNP cleaner.
    :param phrase:
    :return:
    """
    while len(phrase) > 0:
        if phrase[-1] in string.punctuation:
            phrase = phrase[0:-1]
        elif phrase[-1] in string.whitespace:
            phrase = phrase[0:-1]
        elif phrase[0] in string.punctuation:
            phrase = phrase[1:]
        elif phrase[0] in string.whitespace:
            phrase = phrase[1:]
        else:
            break
    return phrase


def extract_entity_list(text):
    """
    Entity list extractor convenience method
    :param text:
    :return:
    """
    entity_list = []
    for e in extract_nnp_phrases(text):
        e = " ".join(e).strip(string.punctuation)
        party = get_cleaned_party(e)
        if party:
            entity_list += party
    return entity_list


stemmer = nltk.stem.PorterStemmer()


# Clean token method
def clean_token(token):
    if len(token.strip().strip(string.punctuation)) == 0:
        return None
    else:
        return stemmer.stem(token.strip().lower())


small_num = {
    'zero': 0,
    'one': 1,
    'two': 2,
    'three': 3,
    'four': 4,
    'five': 5,
    'six': 6,
    'seven': 7,
    'eight': 8,
    'nine': 9,
    'ten': 10,
    'eleven': 11,
    'twelve': 12,
    'thirteen': 13,
    'fourteen': 14,
    'fifteen': 15,
    'sixteen': 16,
    'seventeen': 17,
    'eighteen': 18,
    'nineteen': 19,
    'twenty': 20,
    'thirty': 30,
    'forty': 40,
    'fifty': 50,
    'sixty': 60,
    'seventy': 70,
    'eighty': 80,
    'ninety': 90
}

Magnitude = {
    'thousand': 1000,
    'million': 1000000,
    'billion': 1000000000,
}


def text2num(s):
    a = re.split(r'[\s-]+', re.sub(r'[\d\)]', '', s).strip())
    n = 0
    g = 0
    for w in a:
        x = small_num.get(w, None)
        if x is not None:
            g += x
        elif w == 'hundred' and g != 0:
            g *= 100
        else:
            x = Magnitude.get(w, None)
            if x is not None:
                n += g * x
                g = 0
            else:
                raise RuntimeError('Unknown number: ' + w)
    return n + g
