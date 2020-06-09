## Writing Formulas in ContraxSuite

In ContraxSuite, multiple Fields within a Document Type can be combined by writing a formula that calculates the value of another Field within that Document Type, provided that the data necessary for the calculation is extracted, and not merely text included in an annotation. For example, you can write a formula that uses a Duration Field and a Date Field, but this formula would not be able to include ancillary data from one of those Field's annotations (*e.g.*, the time zone mentioned in the duration) as part of the formula.

A common situation in which a formula might be needed is in the case of expiration dates. Some contracts explicitly state their expiration date. Others might only state the start date and the term length of the contract. For contracts that lack an explicit expiration date, the expiration date can be calculated with a formula that takes the start date and the term. The result is an expiration date not directly extracted from the contract, but nevertheless reliably calculated and then stored as a value.

Let's look at an example of how this would work. Let's say we want to find, or calculate, as many expiration dates as possible in a project. We want to create both an expiration date value to be extracted, *and* a calculated expiration date for those situations where there is no explicitly stated expiration date.

To achieve this, we might follow these steps:

**1.** Create a **"Start Date"** Field:
  * **Field Type:** Date: Non-recurring
  * **Code:** `start_date`
  * Create Field Detectors to extract this "Start Date"

**2.** Create a **"Term"** Field:
  * **Field Type:** Duration
  * **Code:** `term`
  * Create Field Detectors to extract this "Term"

**3.** Create an **"Expiration Date"** Field:
  * **Field Type:** Date: Non-recurring
  * **Code:** `expiration_date`
  * Create Field Detectors to extract this "Expiration Date" from wherever it may be explicitly stated in the document

Once these three Fields have been created, it's time to create the Field that will contain the proper formula:

**4.** Create an **"Expiration Date Calc"** Field:
  * **Field Type:** Date: Non-recurring
  * Select:
    * **Value detection strategy:** "No ML. Use formula only."
    * **Add Depends-on fields:** `start_date`, `term`, and `expiration_date`
    * **Set Field Detection: Calculated Fields**. In the form, write the formula:
      * `expiration_date` **if** `expiration_date` \ 
      * **else** `start_date` + `datetime.timedelta(days=term)` **if** `term` **and** `start_date` \
      * **else** None

The `datetime.delta` code will calculate the expiration date by adding the number of days in `term` to the date value extracted from `start_date`. Since `expiration_date` is a Date Field, the value will be calculated and stored as a Date value.

**5.** Determine if you want users to see `expiration_date` or not, and whether you want users to be able to edit Expiration Date Calc directly. This can be handled one of two ways:
  * **Expiration Date Calc Read Only:** If we want reviewers to take the time to capture proper annotation highlights (to use the data for further training), we make Expiration Date Calc read only. We can then advise reviewers that if they find an explicitly stated expiration date, they should assign it to the Expiration Date Field. Otherwise, they should populate Start Date and Term with proper annotation highlights. Reviewers should never edit Expiration Date Calc directly.
  * **Expiration Date Hidden Always:** If we want answers fast, and if there are only limited benefits to having reviewers manually tag any expiration dates they find, then we can make the Expiration Date Field hidden always. Reviewers will not be able to see or edit the annotations on Expiration Date directly; they will only see the final calculated value for Expiration Date Calc displayed in the annotator. This method is useful when admins and power users plan to utilize the final calculated values, but not their associated annotations.

---

#### Examples of Possible Errors

The best way to write formulas depends heavily on the Field Types used, and the desired Field Type result. If you want a Date Field result, for example, then you need to have your formula return a Date Field. Error messages in ContraxSuite can provide some guidance on what the Field Type should look like if/when it is misused in the context of the written formula.

For example, if we write a formula that includes an "Effective Date" Field, but that Field is actually a **String** Field rather than a Date Field, we will get an error as soon as we try using it in a formula:

  ![DateToString](../../_static/img/guides/FormulaWritingGuide/date_to_string_field.png)

You can correct this by replacing the code in the image above with `str(effective_date)` so that the data is properly read as a String.

Another example of a common error is when you try to do addition with a Currency Field. The error occurs because a Currency Field is not just a number, but a number *and* a currency type. Assume that `salary_yearly` is a Currency Field:

  ![BadCurrencyField](../../_static/img/guides/FormulaWritingGuide/bad_currency_formula.png)

The above error message appears because a Currency Field has both a numeric value and a currency type (*e.g.*, USD), as opposed to one of the Integer Field Types that only have numeric values. In order to add "1000" to the "amount" portion of the Currency Field, you would need to do a calculation on only the "amount" portion of the extracted value, and ensure that the final calculated result is formatted using the criteria outlined in the currency dictionary referenced by the error message (in this case, a `python` dictionary with a "currency" and an "amount". Learn more about [“Python Dictionaries here”](https://www.w3schools.com/python/python_dictionaries.asp) for additional information).

An error-free version of this calculation might look like this:

  ![GoodCurrencyField](../../_static/img/guides/FormulaWritingGuide/good_currency_formula.png)

The calculation works because the 'currency' value of 'USD' is kept separate from the numeric value '300' and the arithmetic performed on it by the formula.

Error messages will supply some information on correct formatting, but here are some of the most common Field Types and the data values to keep in mind as you write formulas:
  * Currency Field: This is a dictionary value (*e.g.*, USD, GBP, JPY) and an amount
  * Related Info: Requires a Boolean value (*i.e.*, True if any annotations found, otherwise False)
  * Date: A value format that can include a Date and/or a Time
  * Duration: Floating Point Number
  * Company, String, Choice, Multi Choice: All of these Fields return string values

---

#### Additional Tips and Troubleshooting

It's important to remember that any Field you use in a formula must be present in the same Document Type.
  * Formulas can break document loading if they do not properly account for null/None/empty values. Always check that a value "is not None" before you write an operation into a formula (you do not want to divide by 0, for example).
    * A quick way to check if `field_a` is "None" or not, is to use `field_a` within your **if** statement (*e.g.*, `field_a` **if** `field_a` == "*anything not null/None/empty*").
    * It is important to regularly test loading documents while you write formulas, to make sure you do not end up with these types of runtime errors.
  * Sometimes the operator "==" is used, while other times the word "is" appears in formulas.
    * Use "is" for: "is None," "is not None," "is True," "is False"
    * In any other situation (*i.e.*, comparing a value to some value other than "None," "True," or "False"), use the  "==" operator
  * Formulas must be written on one line of logical `python`. The "\\" operator allows you to put in a line break for readability, but due to the one line limitation, **if-then** statements must be written like "result" **if** "condition" **else** "alternative" format.
  * Every formula *always* needs to return a value. Always include a final **else** in a formula.
  * You must use the exact Codee that matches a Field used in a formula as a "dependent field". If you use a Code that is not in "dependent fields" you will receive an error message.

---

#### Additional Sample Formulas

**Example #1**

Assume that a Field called `span_color` is a Company, Choice, or String Field. (Click here for more on [Document Fields](./create_document_field)). Further assume that a function called `eng_color` is a Company, Choice, or String Field. Then consider how to write logic for the following:
* If eng_color is not "empty" and is "red", set `span_color` to "rojo"
* Otherwise, if `eng_color` is not "empty" and is "blue", set `span_color` to "azul"
* Otherwise, if `eng_color` is not "empty" and is "yellow", set `span_color` to "amarillo"
* Otherwise, the Field stays empty

Here is how we would write this in code:
* 'rojo' **if** `eng_color` **and** `eng_color` == 'red'
* **else** 'azul' **if** `eng_color` **and** `eng_color` == 'blue'
* **else** 'amarillo' **if** `eng_color` **and** `eng_color` == 'yellow'
* **else** ' '

This could also be written the following way (logically the same):

* ('rojo' **if** `eng_color` == 'red' \ **else** 'azul' **if** `eng_color` == 'blue' \ **else** 'amarillo' **if** `eng_color` == 'yellow' \ **else** ' ') **if** `eng_color` **else** ' '

**Example #2**

Let's look at a different sort of formula. Assume that `term_find` is a Duration Field, and `commencement_date` and `expiration_date` are both Date Fields. Then consider how to write logic for the following:
* If `term_find` is populated, use that value
* Otherwise, if `commencement_date` and `expiration_date` are populated, subtract `commencement_date` from `expiration_date` to get the length (in days) of the term, and use that value
* Otherwise, the Field stays empty

Here is how we would write this in code:
* `term_find` **if** `term_find`
* **else** (`commencement_date` - `expiration_date`).days **if** `commencement_date` **and** `expiration_date`
* **else** ' '

**Example #3**

Consider this example formula. Assume that `standard_percent` is a Floating Integer Number Field, and that `percent_find` is a Floating Integer Number Field. Then consider how to write logic for the following:
* If `percent_find` is populated and greater than 1, use that value
* If `percent_find` is less than 1, multiply by 10
* Otherwise, the value is 0

Note that a Percent Field will conduct this standardization automatically, so this code would only need to be used if you needed to search for Floating Point Integer Number Fields, not strictly "%"s. This would be written in code as the following:
* `percent_find` **if** `percent_find` **and** `percent_find` > 1
* **else** `percent_find` * 10 **if** `percent_find`
* **else** 0

**Example #4**

One more example. Consider the standard way you might want to write just about any formula. Assume you have a Company, Choice, or String Field.
* If a String or a Choice or a Company is 'any Field Type'
* If `field_a` is populated, then use that value
* Otherwise, populate with 'No Value Found'

We would write this standard code as:
* `field_a` **if** `field_a` \ **else** 'No Value Found'

---

#### Some Tips On Regular Expressions (regexp)

You can use a tool like [regex101.com](https://regex101.com/) to set the python flavor to test your regexp. You can set a "case insensitive" flag with this tool, too.

Regexps are run at the sentence level, not across sentences, and are not used to extract values. Rather, they are used to *identify* the sentence that you want to extract a value out of.

When writing regexps, **do not use `.*` or `.+`**. Using either of these overly inclusive codes may cause catastrophic backtracking. Instead of either of those codes, use `.{1,N}`, where N is the maximum distance between two words that you would reasonably expect in the same sentence.

Also be careful not to put code like `.{1,N}` at the beginning of a regexp. This will break the Document Type because it will search for 1 to N of *nothing* if it is at the beginning of the regexp. This is why you must make sure to test with something like [regex101.com](https://regex101.com/), to catch these errors before you break a whole Document Type.

Here is a sample of some good regexp code:

    (?:lessor|landlord|sub-lessor|sub-landlord|sublessor|sublandlord).{0,16000}:\W*(?P<landlord>.{0,16000})
    (?:lessee|tenant|sub-lessee|sub-tenant|sublessee|subtenant).{0,16000}:\W*(?P<tenant>.{0,16000})