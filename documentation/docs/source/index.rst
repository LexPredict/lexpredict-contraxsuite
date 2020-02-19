.. LexPredict ContraxSuite documentation master file, created by
   sphinx-quickstart on Thu Oct 31 11:08:57 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Introduction to ContraxSuite Documentation |version|
====================================================

Welcome to ContraxSuite! ContraxSuite AI is the leading open-source contract analytics and legal document review platform. We offer several tools, including a customizable web application, the legal domain-specific natural language toolkit LexNLP, as well as pre-trained contract analytics models. In this documentation guide you will find everything you need to set up and install ContraxSuite, learn how to use the software, and much more!

ContraxSuite is for anyone who works with legal or financial documents: corporate legal departments, law firms, financial institutions, insurance companies, accountants, auditors, and large publicly-traded companies in any sector. ContraxSuite can identify, organize, and relate the legal material in contracts, extracting terms and locating key clauses in large sets of contracts so that you can find what is most relevant to you. ContraxSuite is also full of features and flexibility, including the ability to integrate with other software tools to visualize and export data.

ContraxSuite can help organizations across a wide range of problems, including:

* Contract Harmonization
* Diligence and M&A
* High-volume and high-impact contract review
* Supply chain and vendor management
* Real estate and lease abstraction
* Large-scale compliance work related to things like GDPR and LIBOR

Learn more about these and other ContraxSuite use cases by `visiting our website <https://contraxsuite.com>`_.

.. toctree::
   :titlesonly:
   :maxdepth: 1
   :hidden:
   :caption: Overview

   introduction/lexpredict_company_overview
   introduction/lexnlp_overview
   introduction/solutions
   introduction/pricing_support
   introduction/intro_legal_analytics


.. toctree::
    :titlesonly:
    :maxdepth: 1
    :hidden:
    :caption: Getting Started

    cxs/use_case_doc_types
    cxs/use_case_data_types
    cxs/core_concepts
    
.. toctree::
    :titlesonly:
    :maxdepth: 1
    :hidden:
    :caption: Setup

    configuration/setup
    configuration/install

.. toctree::
    :titlesonly:
    :hidden:
    :caption: Using CxS - Reviewers
    :maxdepth: 1

    guides/user/reviewers/create_manage
    guides/user/reviewers/batch_analysis
    guides/user/reviewers/document_review

.. toctree::
    :titlesonly:
    :hidden:
    :caption: Using CxS - Power Users
    :maxdepth: 1

    guides/user/cxs_roles
    guides/user/power_users/create_document_type
    guides/user/power_users/create_document_field
    guides/user/power_users/create_field_detectors
    guides/user/power_users/field_detection_examples
    guides/user/power_users/writing_formulas

.. toctree::
    :titlesonly:
    :maxdepth: 1
    :hidden:
    :caption: Data Model Development
    :glob:

    guides/developer/dev_guide_1
    guides/developer/admonition

    api/contraxsuite_orm/*