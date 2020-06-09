Overview
========

## LexPredict Overview

LexPredict was first incorporated in 2013 as Quantitative Legal Solutions, a client service company. The company began developing its first software and data products in 2014, and re-branded to LexPredict that same year.

LexPredict is an enterprise legal technology and consulting firm, part of the [Elevate](https://elevateservices.com/) family of businesses. Our personnel specialize in legal analytics, legal data science and training, risk management, and legal data strategy consulting. We work with corporate legal departments, law firms of all sizes, financial institutions, and other conglomerates to empower better organizational decision-making by improving processes, technology, and the ways people interact with both. We developed ContraxSuite to assist organizations with contract analytics and workflows, using the best machine learning techniques, as well as our own natural language library for legal-specific text, [LexNLP](https://contraxsuite.com/lexnlp/).

Read on for more information about the different ContraxSuite solutions we offer, or navigate to any page in this documentation using the navigation pane on the left side of the screen.

---

## Use Cases

ContraxSuite can help organizations extract information and build custom document analytics to solve a wide range of problems. It's virtually impossible to create an exhaustive list of all of ContraxSuite's use cases, but below we highlight some of the most common.

* **Contract Identification and Organization**: No one knows where *all* of their contracts are. ContraxSuite and LexNLP can help identify unstructured data from sources like shared drives, email accounts, and contract management systems, and then tag contracts for easy organization.
* **Contract Harmonization**: There are many ways to write a clause, and there are even more ways to assemble several clauses into a contract. Contract clutter is a serious problem, and contract consistency is a must. ContraxSuite and LexNLP were built for contract harmonization projects. Match changes in historical paper or slice and dice contracts at the document, section, or clause level. LexNLP can quickly find outliers, anomalies, and other unique language or terms. When you're done, you can then use ContraxSuite to help drive and validate convergence in ongoing contracting.
* **Due Diligence and M&A**: Doing business around the world can be great. Missing law, regulations, and gepolitical risks, on the other hand, *isn't* great. LexNLP identifies risks in contract language, and when a little extra review is necessary, LexNLP can analyze communications and other documents, conducting *pre*-discovery, not just e-discovery.
* **Real Estate and Lease Abstraction**: ContraxSuite and LexNLP can help make sure you understand the restrictions and terms across your real estate and lease portfolios.
* **Finance and Capital Markets**: Identify key financial terms like currency amounts, percentages, rates, and ratios. Find borrowing spreads over LIBOR, leverage ratios in warehouses, and transaction fees. LexNLP can also process documents and agreements like offering and private placement memoranda (OCs, OMs, PPMs), ISDAs, CSAs, ED and PB agreements, and much more. 
* **Supply Chain and Vendor Management**: Sort through new risks and regulatory trends that emerge. Look for things like cyber insurance for Canadian vendors, BAAs for all US facilities, mandatory notice and cooperation clauses for FCPA violations, GDPR or CCPA frameworks, to name just a few examples.
* **Complaint and Settlement Analysis**: Many organizations have massive amounts of unstructured data like demand letters, complaints, and settlement agreements. These documents are not usually searchable or structured, but they contain a trove of valuable data. Tools like LexNLP can uncover and organize this treasure trove, and build strategic analytics to support practices like product liability, professional liability, and labor and employment.
* **Lease Accounting**: Using LexNLP, alongside machine learning tools combined with pre-trained financial and accounting models, you can quickly classify leases and lease terms like term, maintenance, transfer, and purchase rights.

---

## ContraxSuite Solutions

For many years, ContraxSuite has helped law firms, law departments, legal services providers, and enterprise organizations efficiently review and analyze their contracts to gain important insights.

One of the things that has always set ContraxSuite apart is that our platform is available as both an enterprise closed source product, and an open source platform for software developers and data scientists. Read on to explore the different ContraxSuite solutions and decide which one is right for you.


#### Document Explorer

Elements of ContraxSuite are available as open source software, able to be used under the terms of the [Affero General Public License (AGPL)](https://github.com/LexPredict/lexpredict-contraxsuite/blob/master/LICENSE). The **ContraxSuite Document Explorer** allows users to upload documents, extract data, and view that data.

To serve our goal of keeping these elements of ContraxSuite available as an open source project, we have placed our codebase [on GitHub](https://github.com/LexPredict/lexpredict-contraxsuite).

If you are a user of ContraxSuite Document Explorer, visit the following pages of this documentation for more information and instructions:
* For more on what ContraxSuite and LexNLP do, proceed to ["What Is Legal Analytics?"](./intro_legal_analytics)
* To learn about system requirements to address before installation, visit the ["Prerequisites" section](../configuration/setup)
* The ["Installation" section](../configuration/install) will walk you through installing ContraxSuite Community Edition

#### Extraction & Analysis

ContraxSuite Extraction & Analysis module provides users with the full feature set and functionality of ContraxSuite's AI platform, and includes the following capabilities, among others:
* **For Document Reviewers**:
    * View and organize contracts using the Clustering tool
    * View the values ContraxSuite extracts from uploaded contracts
    * Manually change, add, or delete annotations for machine learning training
    * Search documents using either full-text search, or [```regexp```](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Regular_Expressions)
    <br>
* **For Project Managers**:
    * Assign documents to reviewers for easier workflow
    * [Create custom Document Types](../user_guides/power_users/create_document_type) for your reviewers
    * [Create custom Document Fields](../user_guides/power_users/create_document_field) for your reviewers
    * [Create custom Document Field Detectors](../user_guides/power_users/create_field_detectors) for Document Fields you've created
    <br>
* **For Power Users/Administrators**
    * Integrate visualization tools (*e.g.*, PowerBI, RShiny)
    * Integrate document management tools (*e.g.*, Salesforce, iManage, MS Azure, SharePoint, NetDocs, Box, *etc.*) via API
    <br>
* **For Data Scientists**:
    * Create custom machine learning algorithms
    * Utilize ML model-building techniques, such as word2vec and doc2vec

---

## LexNLP

*[Click here for LexNLP documentation](http://publicdocs.contraxsuite.com/lexnlp/index.html)*

LexNLP™ by LexPredict is the leading open source information retrieval and extraction tool for real, unstructured legal text. LexNLP is for developers and other parties who need to solve problems involving contracts, plans, policies, procedures, and other material. Developers and other parties can use LexNLP to build their own solutions, or extract custom data from legal or financial documents. Corporate legal departments, law firms, financial institutions, publicly-traded companies, insurance companies, accountants, and auditors can all benefit from LexNLP.

#### LexNLP Features

LexNLP can extract the following types of information:
* Segmentation and tokenization of common legal abbreviations like "LLC." and "F.3d", and common legal concepts like pages, titles, and sections
* Pre-trained word embedding and topic models, broadly and for specific practice areas
* Pre-trained classifiers for document type and clause type
* Tools for building new clustering and classification methods
* Hundreds of unit tests from real legal documents
* Broad range of fact extraction from legal domain-specific text, such as:
    * Monetary amounts, non-monetary amounts, percentages, ratios
    * Addresses, parties, persons, companies, telephone numbers, and email addresses
    * Conditional statements and constraints, like "less than" or "later than"
    * Dates and durations, including effective dates, termination dates, and delivery dates
    * Terms, notice periods, or assignment delays
    * References to citations or regulations like "26 U.S.C. 501," "26 CFR 31.3121," or "655 F.3d 1013"
    * Controlling law and jurisdictions
    * Copyrights and trademarks
    * Phrasal definitions like "Default shall mean..."

![durations image](/_static/img/intro/lexnlp_durations.png "Code for LexNLP's legal domain-specific terms")

###### Extract Financial Terms

Financial terms, regardless of regional or jurisdictional variants:

* Monetary and non-monetary amounts
* Currency symbols and abbreviations
* Geopolitical entities and distances 
* Percentages, rates, ratios, and proportions

![money image](/_static/img/intro/lexnlp_money.png "Code for LexNLP's financial terms")

###### Tokenization and Segmentation

Other libraries struggle with headings and sections, or they stumble over common abbreviations like "U.S.C." LexNLP tokenizes and segments, leaving nothing behind:

* Pages, paragraphs, and sentences
* Tokens, stems, and stopwords
* Titles, articles, sections
* Exhibits and schedules
* Tables of contents

![tokens image](/_static/img/intro/lexnlp_tokens.png "Code for LexNLP's tokenization and segmentation")

###### Clustering and Classification

LexNLP can cluster and classify data in intuitive ways:

* Sentences, paragraphs, clauses, sections, and documents
* Documents as legal or non-legal material
* Documents as financial or non-financial material
* Contracts among various contract types
* Clauses among various clause types
* By using deep semantic models to find synonyms or related concepts

![tokens image](/_static/img/intro/lexnlp_word2vec.png "Code for LexNLP's word2vec classification models")

<br>

LexNLP is available to organizations through a range of options, including an open source version available under the terms of the Affero General Public License (AGPL). [Read the AGPL license here](https://github.com/LexPredict/lexpredict-contraxsuite/blob/master/LICENSE).

LexNLP is also available under a dual-licensing model. Organizations can request a release from the AGPL terms or a non-GPL evaluation license by contacting LexPredict at [license@contraxsuite.com](mailto:license@contraxsuite.com).

Customers who purchase a ContraxSuite license automatically receive a closed sourced license for LexNLP. For more information on support packages, managed services, and custom implementations, click the "Next" button below to view our Pricing and Support page, or navigate to the Pricing and Support page of this documentation using the menu at left.