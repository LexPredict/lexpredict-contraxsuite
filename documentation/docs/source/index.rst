.. LexPredict ContraxSuite documentation master file, created by
   sphinx-quickstart on Thu Oct 31 11:08:57 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. |version| replace:: 1.6.0

Introduction to ContraxSuite Documentation |version|
====================================================

Welcome to ContraxSuite! ContraxSuite is the leading open-source contract analytics and legal document review platform. We offer several tools, including a customizable web application, the legal domain-specific natural language toolkit LexNLP, as well as pre-trained contract analytics models. In this documentation guide you will find everything you need to set up and install ContraxSuite, learn how to use the software, and much more!

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
   :caption: Introduction

   introduction/overview
   introduction/pricing_support
   introduction/intro_legal_analytics

.. toctree::
    :titlesonly:
    :maxdepth: 1
    :hidden:
    :caption: Getting Started

    configuration/setup
    configuration/install
    configuration/core_concepts

.. toctree::
    :titlesonly:
    :hidden:
    :caption: Using CxS - Reviewers
    :maxdepth: 1

    user_guides/reviewers/create_manage
    user_guides/reviewers/batch_analysis
    user_guides/reviewers/contract_analysis

.. toctree::
    :titlesonly:
    :hidden:
    :caption: Using CxS - Power Users
    :maxdepth: 1

    user_guides/cxs_roles
    user_guides/power_users/import_jupyter_notebooks
    user_guides/power_users/create_document_type
    user_guides/power_users/create_document_field
    user_guides/power_users/create_field_detectors
    user_guides/power_users/field_detection_examples
    user_guides/power_users/writing_formulas
    user_guides/doc_type_migration

.. toctree::
    :titlesonly:
    :maxdepth: 1
    :hidden:
    :caption: Data Model Development
    :glob:

    api/contraxsuite_orm/*