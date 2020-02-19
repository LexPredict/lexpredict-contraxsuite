## User Roles

---

#### Reviewers

Legal or contract review resource, able to follow links and respond to questions and prompts inside of ContraxSuite.
* Has subject matter expertise for relevant document types
* Requires minimal user interface training (experienced with other document review-type platforms)

The interface is designed to be intuitive, but there may be complications with some of the more technical aspects of ContraxSuite that are not comparable to other web-based forms and tools

---

#### Power Users and Admins

A power user of ContraxSuite is likely a subject matter expert, and possibly the project manager who directly supervises reviewers. A power user or admin likely does all of the following:
* Determine what Document Types and Document Fields are needed for a project
* Write descriptions for Fields, and configures Document Types and Document Fields
* Determine which Fields are shown or hidden, based on project needs
* Able to be trained on how to modify Fields and Field Detectors, though this may be covered by IT (see below)
* May have some IT or developer knowledge, but is not the implementation lead on the project

A business analyst or innovation resource acting as a power user or admin may have more advanced training, though not necessarily as much as a developer. Configuring additional aspects of the ContraxSuite interface may mean that a power user or admin has been trained to perform some or all of the following:
* Modify Document Fields and their descriptions
* Change the order in which Fields appear on the page, as well as their Categories
* Add automatic extraction for Fields that meet certain simple criteria, with degree of complexity dependent on sophistication of reviewers (see above)
* Add Fields with data that is not automatically extracted, [using formulas](./power_users/writing_formulas)
* Manage and update app notifications
* Add or hide Fields, and change labels, in a data visualization. May require working with IT or LexPredict resources on server-side storage of relevant data
* Connect other data visualization tools, such as PowerBI. May require working with IT or LexPredict resources to connect to database
* Build new data models, including customizable data visualization options, which may require working with IT or LexPredict resources

---

#### IT

Specialist in server maintenance, data storage, and upgrades. An IT resource will likely be responsible for all of the following:
* Responsible for server maintenance, and moving or renaming servers
* Able to implement system upgrades by taking instruction from LexPredict staff and copy-pasting code into command line
* Responsible for server size and troubleshooting for space needs on virtual machines (VMs)
* Responsible for off-server database backups

IT specialists are not mandatory on a project, as LexPredict staff can assist in these functions. An IT specialist on a ContraxSuite implementation will be given documentation, including how to upgrade their instance via a `dev` server.

---

#### Developers

Whether you use the Enterprise Edition or the Community Edition of ContraxSuite, there are many ways a developer can add their own custom code. We deploy [Jupyter](https://jupyter.org/) notebooks so that a developer can use the platform to analyze their own documents, all without setting up a complete development environment. Developers can thus:
* Use LexNLP to load a document set and retrieve all of one data type (*e.g.*, every **date** in a document set). This data can be exported to a spreadsheet or a third-party application
* Work with LexPredict resources to ensure that changes they make using Jupyter notebooks are not overwritten during system upgrades

LexPredict has various law firm clients and non-law firm clients with their own data science teams, and they choose our platform because of the many versatile developer tools we offer. For LexNLP Jupyter notebooks, [visit the LexNLP GitHub page](https://github.com/LexPredict/lexpredict-lexnlp/tree/master/lexnlp/extract/en).