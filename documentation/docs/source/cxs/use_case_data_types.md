## Use Case Data Types

---

ContraxSuite can label a document as a certain type, such as "binary," "multi-class," "multi-label".
* Binary: a document is either labeled as "Contract" **or** "NOT Contract"
* Binary: a document is either labeled "Amendment/Modification" **or** "Original"
* Multi-Class: a document is either "Draft" **or** "Signed" **or** "Executed"
* Multi-Class: a document is either "License" **or** "Lease" **or** "Employment" **or** "Other"
* Multi-Label: a document is "License" **and/or** "Lease" **and/or** Employment"
* ContraxSuite can also connect and order Amendments to their Originals, based on parties + historically referenced effective dates

ContraxSuite can identify the internal structure of a document:
* The title of a document, plus any "attached" ancillaries, such as Exhibits, Appendices, Addenda
* The table of contents of a document
* The sections of a document, with properly captured hierarchies (*e.g.*, "Section 3, Subsection 3.A")
* The signature block of a document
* Individual text units at the level of sentences, paragraphs, sections, and clauses

ContraxSuite can find clauses in a document:
* Clauses that occur once in every document (**exactly** 1 match per document)
* Any clauses that may occur 0 or more times in a document (0+ matches per document)

ContraxSuite can extract facts from a document:
* Facts that occur once in every document (exactly 1 match per document). Example: Effective Date  
* Facts that may occur 0 or more times in a document (**0+** matches per document).  Example: Prices for multiple work items    
* Items that [LexNLP can find](../../introduction/lexnlp_overview.md)

---

###### Identification Methods

**Basic Match Types**
* Term match: for example, finding the word "insolvency" from the stem/lemma ("insolven"), or via word2vec
* Definition match: for example, finding the definition of "Lessor" and "Lessee" in a contract
* Regular expression (regexp) match: for example, a document that has "Purchase Order [0-9]+"
* Pre-trained ```sklearn``` classifier match: a document has a classifier score > 0.5 (not retrained on user input)
* Can also support pre-trained external model classifier matches that may be more efficient than ```sklearn``` models

**Complex Match Types**
* Basic Match + Fact Present: for example, document has "insolvency" stem/lemma ("insolven") **and** a LexNLP percentage
* Multiple Basic Matches: for example, document has "insolvency" stem/lemma ("insolven") **and** regular expression "Purchase Order [0-9]+"
* Dynamic/online ```sklearn``` classifier match: for example, a document has a classifier score > 0.5 **and** is re-trained on user inputExtraction methods
* Overinclusive regex match **and** a classifier score > 0.5 to narrow
* Prioritize multiple Match Types: *e.g.* try X first, then if nothing is found, try Y
* Find and Map: Finding a geographical value **and** matching it to its country, or finding a company value **and** matching it back to its parent

**Basic Extraction Types**
* Take first/last/Nth (returns exactly **one** value)
* Take Mth, Nth (returns 2 or more values)
* Take greatest (last date, biggest amount, *etc.*)
* Take least (first date, smallest amount, *etc.*)
* Take the closest to some pre-determined value

**Conditional Types**
* Currency Filter: *e.g.* USD only
* Company Filter: *e.g.* LLC only
* Amounts Filter: *e.g.* Units = "pounds (lbs.)" only
* "Found In" Filter: *e.g.* first N pages, first N paragraphs, TOC, definitions

**Token Classifiers**
* Take a token or token sequence with, *e.g.*, a score > 0.5