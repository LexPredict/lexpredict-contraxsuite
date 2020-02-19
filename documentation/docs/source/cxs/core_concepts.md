## Document Processing

ContraxSuite uses many open source software packages and toolkits for optical character recognition (OCR), database management, worker node scaling, document processing, and more.

After a user selects what documents to upload into ContraxSuite, several methods are used to process the documents.

---

#### OCR

Documents uploaded to ContraxSuite undergo a process called Optical Character Recognition (OCR) in order to become fully machine-readable. For OCR, ContraxSuite uses Apache Tika and Google Tesseract.

###### Tika

[Apache Tika](https://tika.apache.org/1.23/gettingstarted.html) is an OCR toolkit that detects and extracts metadata and text from many common file types (*e.g.*, PPT, XLS, RTF, PDF). Documents uploaded into ContraxSuite are scanned by Tika so that the documents are machine-readable.

###### Tesseract

[Tesseract](https://github.com/tesseract-ocr/tesseract) supports unicode (UTF-8), and can also recognize more than 100 languages. Tesseract supports various output formats: plain text, hOCR (HTML), PDF, invisible-text-only PDF, TSV.

---

#### Database Management

Documents uploaded into ContraxSuite are OCR'd and then stored in a secure database.

ContraxSuite uses PostgreSQL, a free and open-source relational database management system (RDBMS). The flexibility of Postgres allows ContraxSuite to be deployed on-premise, in the cloud, or in hybrid deployments.

---

#### Language Detection

After OCR is conducted on a contract, ContraxSuite can recognize the language(s) used in the document, as well as the language(s) of individual text units. Almost all subsequent processing will depend on the language of the content, such as sentence segmentation, part-of-speech tagging, clause classifiers, date location/extraction, *etc.*

#### Content Type Detection

After OCR and language detection...

Detect the type of content (document, text unit). Some models may depend on whether the content is formal (contract) vs. informal (email) English, whether the content is a financial contract or employment contract, etc.

Examples:

    Document A: Contract

    Document B: Email

    Paragraph C: Financial


Implementation:

    Formal vs Informal:

        Good: simple character/token frequency

        Hint: single character/n-character sequence can often detect differences, e.g., by frequency of commas, periods, lists

        Note: word2vec/doc2vec likely overkill for this

    Domain (e.g., Finance vs Employment):

        Good: doc2vec model





    Structured Information Locator

    Structured Information Extractor

LexNLP





If you'd like more control over your contracts, *purchase the Enterprise Edition*


**LexNLP extractors**
 
Broken into text units, terms, tasks...
Examples:

    Document A: English (80%)

    Paragraph B: German (90%)

 

Implementation:





Step 4: Structured Information Locator

Determine whether a text unit contains zero or more types of structured information by classifying a sequence of tokens, either as a whole sequence or at the token level through I-O-B tagging. Locators do not structure the information, but can identify whether and where structured information exists. This allows subsequent Structured Information Extraction code to run efficiently over small subsets of text instead of entire documents.

NOTE: For example, documents typically have very few dates, so a locator should identify the small number of sentences where dates do occur. Today, we use a regular expression engine to parse the entire document, even if zero dates occur, and this regex pass cannot be re-used for any other tasks like durations, monetary amounts, etc.

References:

    I-O-B tagging: https://en.wikipedia.org/wiki/Inside%E2%80%93outside%E2%80%93beginning_(tagging)

Depends On:

    Language Detection

    Content Type Detection (optional)

Examples:

    Sentence A: sequence-level classification

        contains date (90%)

        contains duration (90%)

    Sentence A: token-level IOB

        contains date: B=27th, I=of, I=December, I=2019)

        contains duration: B=six, I=months


Implementation:

    NOTE: Goal is to allow ALL LOCATORS to run in parallel, sharing the same feature vectors, through a multi-label classification model.

Step 5: Structured Information Extractors

Convert unstructured sequence of tokens into a structured data type, such as a date, duration, or monetary amount. This structuring can be done using techniques like regular expressions or “standard” Python methods.

 

The goal of LexNLP v2 and its ML/NLP sequence classification is to:

    Allow users to locate structured information without extracting structure

    Reduce number of passes through entire document

    Separate location logic from extraction logic so that multiple structuring approaches can be used, not just regex


Reference:

    LexNLP v1

Implementation:

    See LexNLP v1.

    Consider where if-else/token in [...] logic can exist without regex overhead.


---

The following three probably can be filled out using material from "Document Field Text Unit Type"

#### Text Units

section

paragraph

sentence

clause

term/word-level

#### Terms

words, stems, lemmas

#### Tasks