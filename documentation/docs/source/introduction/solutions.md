Solutions
=========

For many years, ContraxSuite has helped numerous law firms, legal services providers, and enterprise organizations to efficiently review and analyze their contracts to gain important insights.

One of the things that has always set ContraxSuite apart is that our platform is available as both an enterprise closed source product, and an open source platform for software developers and data scientists. Read on to explore the different ContraxSuite solutions, to decide which one is right for you.

***

## Community Edition

ContraxSuite is available as open source software, able to be used under the terms of the [Affero General Public License (AGPL)](https://github.com/LexPredict/lexpredict-contraxsuite/blob/master/LICENSE). This "Community Edition" of ContraxSuite allows users to upload documents, extract data, and view that data in the "Explore Data" user interface.

To serve our goal of keeping these elements of ContraxSuite available as an open source project, we have placed our codebase [on GitHub](https://github.com/LexPredict/lexpredict-contraxsuite).

If you are a user of the Community Edition of ContraxSuite, visit the following pages of this documentation for more information:
* For more on what ContraxSuite and LexNLP do, proceed to ["What Is Legal Analytics?"](./intro_legal_analytics)
* To learn about system requirements to address before installation, visit the ["Prerequisites" section](../configuration/setup)
* The ["Installation" section](../configuration/install) will walk you through installing ContraxSuite Community Edition

***

## Enterprise Edition

The Enterprise Edition provides users with the full feature set and functionality of the ContraxSuite AI platform, and includes the following capabilities, among others:
* **For Document Reviewers**:
    * View and organize contracts using the Clustering tool
    * View the values ContraxSuite finds in uploaded contracts
    * Manually change, add, or delete annotations for machine learning training
    * Search documents using either full-text search, or [```regexp```](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Regular_Expressions)
    <br>
* **For Project Managers**:
    * Assign documents to reviewers for easier workflow
    * [Create custom Document Types](../guides/user/power_users/create_document_type) for your reviewers
    * [Create custom Document Fields](../guides/user/power_users/create_document_field) for your reviewers
    * [Create custom Document Field Detectors](../guides/user/power_users/create_field_detectors) for Document Fields you've created
    <br>
* **For Power Users/Administrators**
    * Integrate visualization tools (*e.g.*, PowerBI, RShiny)
    * Integrate document management tools (*e.g.*, Salesforce, iManage, MS Azure, SharePoint, NetDocs, Box, *etc.*) via API
    <br>
* **For Data Scientists**:
    * Create custom machine learning algorithms
    * Utilize ML model-building techniques, such as word2vec and doc2vec

***

## LexNLP

LexNLP™ by LexPredict is the leading open source information retrieval and extraction tool for real, unstructured legal text. LexNLP is for developers and other parties who need to solve problems involving contracts, plans, policies, procedures, and other material. Developers and other parties can use LexNLP to build their own solutions, or extract custom data from legal or financial documents. Corporate legal departments, law firms, financial institutions, publicly-traded companies, insurance companies, accountants, and auditors can all benefit from LexNLP.

LexNLP can extract the following types of information:
* Segmentation and tokenization of common legal abbreviations like "LLC." and "F.3d", and common legal concepts like pages, titles, and sections
* Pre-trained word embedding and topic models, broadly and for specific practice areas
* Pre-trained classifiers for document type and clause type
* Tools for building new clustering and classification methods
* Hundreds of unit tests from real legal documents
* Broad range of fact extraction, such as:
    * Monetary amounts, non-monetary amounts, percentages, ratios
    * Addresses, persons, companies, telephone numbers, and email addresses
    * Conditional statements and constraints, like "less than" or "later than"
    * Dates and durations
    * Courts, regulations, and citations

LexNLP is available to organizations through a range of options. The Community Edition supports a default, open source AGPL license. [Read the AGPL license here](https://github.com/LexPredict/lexpredict-contraxsuite/blob/master/LICENSE). However, LexNLP is available under a dual-licensing model. Organizations can request a release from the AGPL terms or a non-GPL evaluation license by contacting LexPredict at [license@contraxsuite.com](mailto:license@contraxsuite.com).

Learn more about LexNLP, its features, and its use cases, on the [Introduction to LexNLP](./lexnlp_overview) page of this documentation.

The Enterprise Edition of ContraxSuite includes a closed source version of LexNLP. For more information on support packages, managed services, and custom implementations, click the "Next" button below to view our Pricing and Support page, or navigate to any other section of this documentation with the menu at left.