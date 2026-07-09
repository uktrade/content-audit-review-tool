# CART Data Dictionary

This document defines all the data ingested into the master dataset that underpins CART, including:
- GOV.UK Content API metadata
- Analytics (GA4)
- Crawl data from a third-party web crawler
- Derived data

Where data is only partially available or conditions apply, we explain the rules we've used in the **Logic** column.

---

## Core content metadata

| Field | Format | Description | Source | Logic |
|------|--------|-------------|--------|-------|
| content_id | string | A unique identifier for an HTML GOV.UK page. | Content API | Applies only if the content item is an HTML GOV.UK page. No inheritance for attachments. |
| public_url | string | Public-facing web address for a content item. | Content API | Always applies. |
| document_type | string | The editorial category for a GOV.UK content item (e.g. guidance, HTML publication, policy paper). | Content API | Applies only if the content item is an HTML GOV.UK page. No inheritance for attachments. |

---

## Taxonomy and ownership

| Field | Format | Description | Source | Logic |
|------|--------|-------------|--------|-------|
| categories | array[string] | The list of topics or taxons tagged to a GOV.UK content item. | Content API | Most HTML pages have at least one taxon. Some document types do not (e.g. HMRC manuals). For HTML and non-HTML attachments, we derive categories from the parent content item where the parent has them. |
| publishing_orgs | array[string] | All organisations associated with a GOV.UK content item. | Content API | Most HTML pages have at least one publishing organisation. For attachments, we derive publishing organisations from the parent content item where available. |
| primary_publishing_org | string | The primary publishing organisation responsible for the content item. | Content API | Most HTML pages have a primary publishing organisation. For attachments, we derive from the parent content item where the parent has one. |

---

## Content fields

| Field | Format | Description | Source | Logic |
|------|--------|-------------|--------|-------|
| title | string | The title of a content item. | Content API | Most content items have their own title. For attachments that do not, we derive from the parent content item for analytical purposes. |
| abstract | string | A summary describing what a content item is about. | Content API | Applies only to document types that include an abstract (or equivalent summary field). No inheritance applied. |
| html | string | Full HTML content within the `<body>` of a GOV.UK page. | Content API | Applies only to HTML GOV.UK pages. |
| text | string | Full extracted text from an HTML page or PDF. | Content API (derived), Screaming Frog | HTML: applies where text exists within the `<body>` tags. PDF: applies only if the PDF was successfully scraped via Screaming Frog. |

---

## Publishing metadata

| Field | Format | Description | Source | Logic |
|------|--------|-------------|--------|-------|
| date_published | timestamp | Initial publication date | Content API | Applies only to HTML GOV.UK pages |
| public_updated_at | timestamp | Date of last significant editorial update | Content API | Shared across all HTML pages within a publication (for example, HTML publications with multiple parts) |
| publishing_app | string | Application used to publish content (for example, Publisher, Whitehall) | Content API | Applies to all non-attachment HTML pages. For attachments, we derive this from the parent.|
| is_historic | boolean | Whether content is in ‘history mode’ (associated with a previous government) | Content API | For attachments, we derive this from the parent content item |

---

## Hierarchy and structure

| Field | Format | Description | Source | Logic |
|------|--------|-------------|--------|-------|
| parent_content_id | string | Content ID of the parent item. | Content API | Applies only to attachments. |
| parent_public_url | string | Public URL of the parent item. | Content API | Applies only to attachments. |
| is_attachment | boolean | Whether the content item is an attachment. | Derived | Always applies. |
| is_parent | boolean | Whether the content item has attachments. | Derived | Applies to HTML pages. |
| grouping_id | string | Identifier used to group parent content and its attachments. | Derived | Attachments inherit the grouping ID from the parent content item. |
| no_of_attachments | numeric | Number of attachments associated with a content item. | Derived | Primarily applies to HTML pages. |

---

## Analytics (GA4)

| Field | Format | Description | Source | Logic |
|------|--------|-------------|--------|-------|
| sessions | numeric | Total sessions where content was viewed. | Google Analytics | Always applies. |
| users | numeric | Total unique users (cookie-based). | Google Analytics | Always applies. |
| new_users | numeric | Users whose first visit included this page. | Google Analytics | Applies only to HTML pages. |
| returning_users | numeric | Users who have previously visited GOV.UK. | Google Analytics | Applies only to HTML pages. |
| engagement_time_secs | numeric | Total engaged time. | Google Analytics | Applies only to HTML pages. |
| entrances | numeric | Sessions starting on this page. | Google Analytics | Applies only to HTML pages. |
| exits | numeric | Sessions ending on this page. | Google Analytics | Applies only to HTML pages. |

---

## File interaction metrics

| Field | Format | Description | Source | Logic |
|------|--------|-------------|--------|-------|
| total_file_downloads | numeric | Total downloads of attachments linked from a page. | Google Analytics | Applies only to HTML pages. |
| users_file_download | numeric | Number of who downloaded attachments. | Google Analytics | Applies only to HTML pages. |
| file_downloads | numeric | Downloads of non-HTML content items (e.g. PDFs). | Google Analytics | Applies only to non-HTML content items. |
| navigation | numeric | Access via file navigation interactions. | Google Analytics | Applies only to non-HTML content items. |
| file_download_navigated | numeric | Combined downloads and navigation interactions. | Derived | Applies only to non-HTML content items. |

---

## Crawl and readability (Screaming Frog)

| Field | Format | Description | Source | Logic |
|------|--------|-------------|--------|-------|
| word_count | numeric | Total word count of HTML or PDF content | Screaming Frog | Requires successful scrape |
| sentence_count | numeric | Total number of sentences in HTML or PDF content | Screaming Frog | Requires successful scrape |
| average_words_per_sentence | numeric | Average sentence length in HTML or PDF content | Screaming Frog | Requires successful scrape |
| flesch_reading_ease_score | numeric | Readability score (0–100) of HTML or PDF content | Screaming Frog | Requires successful scrape |
| readability | string | Readability classification label for HTML or PDF content | Screaming Frog | Requires successful scrape |
| is_broken | boolean | Whether the URL returns a 404 | Screaming Frog | Applies to HTML and PDF || is_redirecting | boolean | Whether the URL redirects | Screaming Frog | Applies to HTML and PDF |
| screaming_frog_available | boolean | Whether crawl data exists | Screaming Frog | Always applies |

---

## Derived structural and usability metrics

| Field | Format | Description | Source | Logic |
|------|--------|-------------|--------|-------|
| n_links | numeric | Total number of links on a page | Derived | HTML pages only |
| n_broken_links | numeric | Number of broken links on a page| Derived | HTML pages only |
| n_redirecting_links | numeric | Number of redirecting links | Derived | HTML pages only |
| total_headings | numeric | Count of headings (H1–H5) | Derived | HTML pages only |
| word_to_heading_ratio | numeric | Ratio of content density to structure | Derived | Applies where both word count and headings exist |
| expected_reading_time_mins | numeric | Estimated reading time of HTML or PDF content based on word count | Derived | Applies where word count exists |

---

## Accessibility

| Field | Format | Description | Source | Logic |
|------|--------|-------------|--------|-------|
| accessible_url | string | URL of an accessible version of a content item | Derived | Applies to HTML or qualifying PDFs |
| accessible_url_confidence_score | numeric | Confidence score for accessible match | Derived | ≥0.8 for PDFs; 1 for HTML |
| has_accessible_version | boolean | Whether an accessible version exists | Derived | TRUE if confidence ≥0.9 |

---

## Quality flags and recommendations

| Field | Format | Description | Source | Logic |
|------|--------|-------------|--------|-------|
| user_relevance_flag | boolean | Indicates low user relevance. | Derived | TRUE if any relevance rule is triggered. |
| user_relevance_reasons | array[string] | Reasons for relevance flag. | Derived | From controlled vocabulary. |
| usability_flag | boolean | Indicates usability issues. | Derived | TRUE if any usability rule is triggered. |
| usability_reasons | array[string] | Reasons for usability flag. | Derived | From controlled vocabulary. |
| freshness_flag | boolean | Indicates lack of editorial freshness. | Derived | TRUE if any freshness rule is triggered. |
| freshness_reasons | string | Reason for freshness flag. | Derived | From controlled vocabulary. |
| recommendation | string | Recommended editorial action. | Derived | Based on triggered flags. |

