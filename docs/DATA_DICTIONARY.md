# CART data dictionary

This document explains every field in the CART audit data.

Each CART audit produces a CSV file with one row for each page or file in the audit.

The data comes from:

- **GOV.UK Content API**: information about each page, such as its title, dates and owner
- **Google Analytics 4 (GA4)**: visits, downloads and user engagement over a 12-month period
- **Screaming Frog**: a web crawler that checks links and errors, and reads the text of pages and PDFs
- **Derived**: values CART works out from the data we have, including the issue flags, quality scores and recommendations

The descriptions in the data dictionary tables are CART's final data definitions. The **Logic** column explains which rows have a value, and any rules we use.

The tables group fields by topic, so they're not in the same order as the columns in the CSV file.

---

## How to read the data

### Types of row

| Row type | What it is |
|----------|------------|
| Main page | An HTML page on GOV.UK that isn't attached to another page |
| HTML attachment | An HTML publication that sits under a parent HTML page as part of GOV.UK's standard publication design |
| File | A non-HTML file that sits under a parent HTML page, such as a PDF, spreadsheet or Word document |

HTML attachments and files are both **attachments**. An attachment's parent page is given in `parent_content_id` and `parent_public_url`.

Attachments take these fields from their parent page: `categories`, `publishing_orgs`, `primary_publishing_org`, `publishing_app`, `is_historic` and `withdrawn`.

### Formats

| Format | What it means | Example |
|--------|---------------|---------|
| string | Text | `Trade and investment` |
| numeric | A number | `553.0` |
| boolean | `TRUE` or `FALSE` | `TRUE` |
| date | Day, month and year | `14/06/2026` |
| timestamp | Date and time | `23/04/2025 11:18` |
| array[string] | A list in square brackets. `[]` means the list is empty. | `['Exporting', 'Free trade']` |
| set[string] | A list of labels in curly brackets. Labels with spaces are in double quotes. `{}` means none. | `{"high (lower)",high}` |

An empty cell means there's no data, or the field doesn't apply to that row. An empty cell isn't the same as `0`. For example, `sessions` is `0` when a page had no visits, but empty when there's no visit data at all.

The file uses UTF-8 text (a standard way of storing letters and symbols), with commas between fields. The first row has the field names.

---

## Core content metadata

| Field | Format | Description | Source | Logic |
|-------|--------|-------------|--------|-------|
| title | string | Name of the page or file | Content API | All rows. |
| public_url | string | Web address of the page or file | Content API | All rows. |
| content_id | string | Unique GOV.UK identifier for an HTML page | Content API | All HTML pages on GOV.UK, including HTML publications, have their own ID. Non-HTML files, and HTML pages on other websites, show `None`. |
| file_extension | string | File format, such as HTML, PDF or DOCX | Derived | All rows. Taken from the web address. Written in lower case, for example `html`, `pdf` or `odt`. |
| document_type | string | GOV.UK content type, such as guidance or policy paper | Content API | Main HTML pages and HTML attachments. Files show `N/A`. |
| abstract | string | Short summary of what a page is about | Content API | Main HTML pages whose document type has a summary. |

---

## Taxonomy and ownership

| Field | Format | Description | Source | Logic |
|-------|--------|-------------|--------|-------|
| categories | array[string] | Topics the content is tagged to on GOV.UK | Content API | All rows. Some document types, such as manuals, have no topics. Attachments take their parent page's topics. |
| primary_publishing_org | string | Organisation primarily responsible for the content | Content API | All rows. Attachments take their parent page's primary organisation. |
| publishing_orgs | array[string] | All organisations associated with publishing the content | Content API | All rows. Attachments take their parent page's organisations. |

---

## Publishing metadata

| Field | Format | Description | Source | Logic |
|-------|--------|-------------|--------|-------|
| date_published | date | Date a page was first published | Content API | Main HTML pages and HTML attachments on GOV.UK only. |
| public_updated_at | date | Date a page was last significantly updated | Content API | Main HTML pages and HTML attachments on GOV.UK only. |
| pdf_modified | timestamp | Date a PDF file was last modified | Screaming Frog | PDFs only. Taken from the PDF file's own details, so it can be missing or wrong. |
| pdf_created | timestamp | Date a PDF file was originally created | Screaming Frog | PDFs only. Taken from the PDF file's own details, so it can be missing or wrong, for example `03/12/1989 00:00`. |
| publishing_app | string | System used to publish the content | Content API | All rows, for example `whitehall`, `specialist-publisher` or `manuals-publisher`. Attachments take their parent page's value. |
| withdrawn | boolean | Whether the page or file has been officially withdrawn | Content API | All rows. Attachments take their parent page's value. |
| is_historic | boolean | Whether the page or file relates to a previous government | Content API | All rows. `TRUE` means the content is in 'history mode'. Attachments take their parent page's value. |

---

## Hierarchy and structure

| Field | Format | Description | Source | Logic |
|-------|--------|-------------|--------|-------|
| grouping_id | string | ID used to link a page or file with its parent page, child pages or attachments | Derived | All rows. For a main HTML page, this is its own `content_id`. Attachments use their parent page's `content_id`. |
| is_attachment | boolean | Whether the page or file is a child or attachment on another page | Derived | All rows. |
| parent_content_id | string | Content ID of the parent page for a child or attachment | Content API | Attachments only. |
| parent_public_url | string | URL of the parent page for a child or attachment | Content API | Attachments only. |
| no_of_attachments | numeric | How many files are attached to a page | Derived | All rows. Counts HTML attachments as well as files. |
| is_parent | boolean | Whether a page is a parent page with one or more attachments | Derived | All rows. `TRUE` when `no_of_attachments` is more than 0. |

---

## Analytics (GA4)

All analytics fields cover the same 12-month period.

| Field | Format | Description | Source | Logic |
|-------|--------|-------------|--------|-------|
| sessions | numeric | Number of visits over a 12-month period | Google Analytics | All types of row. `0` means there were no visits. Empty means there's no visit data, and this is confirmed in the `ranking_reasons` column, which will state `Missing demand data`. |
| engaged_sessions | numeric | Number of visits where users actively engaged with a page over a 12-month period | Google Analytics | Main HTML pages and HTML attachments only. |
| users | numeric | Number of unique users over a 12-month period | Google Analytics | All types of row. Empty when there's no visit data. |
| engagement_time_secs | numeric | Total time users actively spent on the page over a 12-month period | Google Analytics | Main HTML pages and HTML attachments only. In seconds. |

---

## File downloads (GA4)

| Field | Format | Description | Source | Logic |
|-------|--------|-------------|--------|-------|
| all_downloads_from_parent | numeric | Total downloads of all attachments on a parent page over a 12-month period | Google Analytics | Main HTML pages and HTML attachments only. |
| all_downloads_of_attachment | numeric | Number of times a specific file was downloaded over a 12-month period | Google Analytics | Non-HTML files only. |
| all_downloads_via_navigation | numeric | Number of times a file was opened through navigation interactions over a 12-month period | Google Analytics | Non-HTML files only. |
| total_file_downloads | numeric | Combined total of downloads and navigation opens for a specific file over a 12-month period | Derived | Non-HTML files only. `all_downloads_of_attachment` plus `all_downloads_via_navigation`. (In older CART data, this name meant downloads of all attachments on a page. That's now `all_downloads_from_parent`.) |

---

## Crawl and readability (Screaming Frog)

Except for `word_count` on main HTML pages and HTML attachments, the word, sentence, page count and readability fields need a successful crawl. `screaming_frog_available` shows whether there is one.

| Field | Format | Description | Source | Logic |
|-------|--------|-------------|--------|-------|
| word_count | numeric | Total number of words | Content API, Screaming Frog | Main HTML pages and HTML attachments: from the Content API, so there's a value even without crawl data. PDFs: from the crawl, so only PDFs the crawler could read. |
| sentence_count | numeric | Total number of sentences | Screaming Frog | Main HTML pages, HTML attachments and PDFs the crawler could read. |
| pdf_page_count | numeric | Number of pages in a PDF | Screaming Frog | PDFs the crawler could read. |
| average_words_per_sentence | numeric | Average sentence length | Screaming Frog | Main HTML pages, HTML attachments and PDFs the crawler could read. Worked out by the crawler, so it may not equal `word_count` divided by `sentence_count`. |
| flesch_reading_ease_score | numeric | Score showing how easy the content is to read | Screaming Frog | Main HTML pages, HTML attachments and PDFs the crawler could read. From 0 to 100. A higher score means the content is easier to read. |
| readability_label | string | Plain language readability rating, such as `Easy` or `Hard` | Screaming Frog | Based on `flesch_reading_ease_score`. One of 7 labels, from `Very Easy` to `Very Hard`. See [Readability labels](#readability-labels). |
| is_broken | boolean | Whether the page or file cannot be accessed because it returns a 404 error | Screaming Frog | All rows. |
| is_redirecting | boolean | Whether the URL automatically sends users to another URL | Screaming Frog | All rows. Always `FALSE` at the moment. |
| screaming_frog_available | boolean | Whether web crawl data is available for the page or file (web crawl data is used for things like link checking, readability and PDF text analysis) | Screaming Frog | All rows. `FALSE` when the crawler has no data for the page or file. This includes files that aren't PDFs, such as ODT, ODS and DOCX files, and pages or PDFs the crawler couldn't reach. |

---

## Structure and links

| Field | Format | Description | Source | Logic |
|-------|--------|-------------|--------|-------|
| total_headings | numeric | Number of headings in the content | Derived | Main HTML pages and HTML attachments only. |
| word_to_heading_ratio | numeric | Average number of words between headings on a page | Derived | Main HTML pages and HTML attachments only. `word_count` divided by `total_headings`. If there are no headings, this is the same as `word_count`. |
| expected_reading_time_mins | numeric | Estimated time needed to read the content | Derived | Wherever there's a `word_count`. `word_count` divided by 250. |
| n_links | numeric | Total number of links on a page | Derived | Main HTML pages and HTML attachments only. |
| n_broken_links | numeric | Number of links on a page that do not work | Screaming Frog | Main HTML pages and HTML attachments only. |
| broken_link_ratio | numeric | Percentage of links on a page that are broken | Derived | All rows. Written as a decimal from 0 to 1, so `0.0652` means 6.5%. `0` when there's no link data. |
| broken_link_text | array[string] | List of broken links found on a page | Screaming Frog | All rows. The web addresses of the broken links. `[]` when there are none. |
| n_redirecting_links | numeric | Number of links on a page that redirect elsewhere | Derived | Main HTML pages and HTML attachments only. |

---

## Accessibility

| Field | Format | Description | Source | Logic |
|-------|--------|-------------|--------|-------|
| accessible_url | string | URL of an accessible version of the content, where one has been identified | Derived | For main HTML pages and HTML attachments, it's their own web address. For PDFs, the address of a possible matching HTML version, where one was found. Empty for other files. |
| accessible_url_confidence_score | numeric | How confident the system is that the accessible version match is correct | Derived | PDFs with a possible match only. From 0.8 to 1. A match only counts as an accessible version at 0.9 or more. |
| is_pdf_with_accessible_version | boolean | Whether an accessible version of a PDF exists | Derived | All rows. `TRUE` only for PDFs with a match at a confidence of 0.9 or more. |

---

## Issue flags

CART looks for issues in 4 areas: freshness, functionality, user engagement and accessibility. Not every area applies to every type of row. See [What the labels mean](#what-the-labels-mean).

Each area has 3 fields:

- a **flag**: how serious the issues are
- the **reasons**: a list of the issues found
- a **score**: the issues' scores added up

[Issue labels](#issue-labels) lists every reason, with its severity and score.

| Field | Format | Description | Source | Logic |
|-------|--------|-------------|--------|-------|
| freshness_flag | set[string] | Whether the content appears out of date and how severely | Derived | All rows. `{}` when no issue was found. |
| freshness_reasons | array[string] | Reason the content appears out of date | Derived | All rows. `[]` when no issue was found. |
| freshness_score | numeric | Score indicating the severity of a page or file's freshness issues | Derived | All rows. `0` when no issue was found. |
| functionality_flag | set[string] | Whether the content has technical issues and how severe they are | Derived | All rows. `{}` when no issue was found. |
| functionality_reasons | array[string] | Details of any technical issues found | Derived | All rows. `[]` when no issue was found. |
| functionality_score | numeric | Score indicating the severity of a page or file's functionality issues | Derived | All rows. `0` when no issue was found. |
| negative_user_engagement_flag | set[string] | Whether user engagement appears low and the severity of the issue | Derived | All rows. `{}` when no issue was found. |
| negative_user_engagement_reasons | array[string] | Reason the content was flagged for low engagement | Derived | All rows. `[]` when no issue was found. |
| negative_user_engagement_score | numeric | Score indicating the severity of a page or file's user engagement issues | Derived | All rows. `0` when no issue was found. |
| accessibility_flag | set[string] | Whether accessibility or usability issues were found and how severe they are | Derived | All rows. `{}` when no issue was found. A page or file can have multiple accessibility issues, so data shows one severity flag for each issue. For example, content that's hard to read and hard to scan shows `{high,high}`. |
| accessibility_reasons | array[string] | Details of accessibility or usability issues found | Derived | All rows. `[]` when no issue was found. |
| accessibility_score | numeric | Score indicating the severity of a page or file's accessibility and usability issues | Derived | All rows. `0` when no issue was found. |

---

## Scores and ranking

| Field | Format | Description | Source | Logic |
|-------|--------|-------------|--------|-------|
| base_score | numeric | Combined score before normalisation and adjustments for user impact | Derived | All rows. The 4 area scores added up. Withdrawn content always has a base score of `1`. |
| normalised_score | numeric | Adjusted score that allows pages and files to be compared on a consistent scale | Derived | All rows. `base_score` multiplied by 5 for main HTML pages and HTML attachments, and by 4 for files, so they can be compared on the same scale. |
| score_multiplier | numeric | Adjustment factor based on user demand that affects prioritisation | Derived | All rows. Based on `sessions`, from 0.6 to 2. It rises steadily with the number of visits, between set bands. `0.6` when there were no visits. `1` when there's no visit data. |
| adjusted_score | numeric | Final score used to prioritise content | Derived | All rows. `normalised_score` multiplied by `score_multiplier`. |
| priority_rank | numeric | Position of page or file in the priority list, based on overall score (lower rank numbers indicate content that may need attention sooner) | Derived | All rows. `1` is the highest `adjusted_score`. Each row has its own rank, even when scores are the same. |
| ranking_reasons | set[string] | Indication of where the page or file's rank has been affected by a lack of data | Derived | All rows. `{}` when the rank isn't affected. A label can appear more than once. See [Ranking reasons](#ranking-reasons). |

---

## Recommendations

| Field | Format | Description | Source | Logic |
|-------|--------|-------------|--------|-------|
| recommendation | string | Suggested editorial action for each page or file | Derived | All rows. `Review`, `Remove` or `No action`. See [Recommendation values](#recommendation-values). |
| recommend_convert | boolean | Whether a PDF would be better published as HTML | Derived | All rows. `TRUE` for PDFs with a `Review` recommendation and a pre-2018 or post-2018 'no accessible alternative' issue. |
| recommend_transfer_to_tna | boolean | Whether the content may be suitable for removal from GOV.UK and transfer to The National Archives | Derived | All rows. `TRUE` for withdrawn content. |
| issue_summary | string | Summary of the main issues identified | Derived | Explains the recommendation in a sentence. For `No action`, it's either empty or `No issues found`. |

---

## Labels

These are the values the data uses, written exactly as they appear in the CSV file.

### Severity levels

The 4 flag fields use these severity levels, from least to most serious:

1. `moderate`: for an issue that scores between 1 and 2
2. `high (lower)`: for an issue that scores between 2 and 3
3. `high`: for an issue that scores 3 or 4
4. `critical`: for an issue that scores 5

### Issue labels

In accessibility, a page or file can have more than one issue. Their scores are added together, and the flag shows a severity for each one. For example, a post-2018 PDF with no accessible alternative (5) that is also hard to read (3) has an accessibility score of 8 and the flag `{critical,high}`.

Functionality only counts the highest-scoring issue. `more than 50% of links on page are broken` needs at least 2 broken links, so a page whose only link is broken shows `1 broken link`.

| Area | Label in the data | Severity | Score |
|------|-------------------|----------|-------|
| Freshness | No updates in the last 3-5 years | moderate | 1 to 2 (continuous scaling in this band) |
| Freshness | No updates in the last 5-10 years | high (lower) | 2 to 3 (continuous scaling in this band) |
| Freshness | No updates for 10+ years | high | 3 |
| Functionality | 1 broken link | high | 3 |
| Functionality | 2 broken links | high | 4 |
| Functionality | 3 or more broken links | critical | 5 |
| Functionality | more than 50% of links on page are broken | critical | 5 |
| Functionality | Page returns an error (e.g. 404) | critical | 5 |
| User engagement | Eng time per session falls below P10 threshold | moderate | 1 |
| Accessibility | Post-2018 content with no accessible alternative | critical | 5 |
| Accessibility | Pre-2018 content with no accessible alternative | high (lower) | 2 |
| Accessibility | Content is hard to read (dense, complex language) | high | 3 |
| Accessibility | Content is hard to scan (poor headings / structure) | high | 3 |

### What the labels mean

- **Freshness**: how long it is since the content was last updated, counted on the day of the audit. For main HTML pages and HTML attachments, this uses `public_updated_at`. For PDFs, it uses `pdf_modified`. Other files, and PDFs with no `pdf_modified` date, aren't checked. Within each band, the score rises steadily with age.
- **P10 threshold**: P10 means the lowest 10%. This label is for pages where user engagement is in the lowest 10% of pages in the audit. Files aren't checked.
- **Pre-2018 and post-2018**: these only apply to PDFs with no accessible version. They're based on the PDF's `pdf_modified` date: before or after 23 September 2018, when the accessibility regulations came in. Other files aren't checked.
- **Hard to read**: a `flesch_reading_ease_score` below 50.
- **Hard to scan**: more than 500 words for each heading (`word_to_heading_ratio`). A page with no headings and more than 500 words counts as hard to scan.

### Recommendation values

| Value | When it's used |
|-------|----------------|
| Review | One or more issues were found. |
| Remove | The content is withdrawn. Or it had no visits (`sessions` is `0`) in the 12 months and hasn't been updated for more than 10 years. `Remove` takes priority over `Review`. |
| No action | No issues were found. |

### Readability labels

Scores have decimals. "Up to 90" means below 90, so a score of 89.9 is `Easy`.

| Label | `flesch_reading_ease_score` |
|-------|-----------------------------|
| Very Easy | 90 or more |
| Easy | 80 up to 90 |
| Fairly Easy | 70 up to 80 |
| Normal | 60 up to 70 |
| Fairly Hard | 50 up to 60 |
| Hard | 30 up to 50 |
| Very Hard | Below 30 |

### Ranking reasons

| Label | Meaning |
|-------|---------|
| Incomplete audit data | Some audit data is missing, for example there's no web crawl data. |
| Missing demand data | There's no visit data, so `score_multiplier` is set to `1`. |
| Withdrawn content | The content is withdrawn, so `base_score` is set to `1`. |
