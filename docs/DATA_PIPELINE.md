# Data pipeline and sources 

CART uses multiple data sources to gain insight into the quality of GOV.UK content. These data sources are:  

- the GOV.UK Search and Content API for direct access to the content 

- website crawl data for issues that affect search engine optimisation 

- Google Analytics 

This file explains how content, analytics, and crawl data are collected and prepared for CART. 

## GOV.UK Search and Content API 

### HTML pages  

DBT has a pipeline which uses the GOV.UK Search and Content APIs to ingest large amount of GOV.UK content and associated metadata. 

The Search API is used to apply filters on GOV.UK content that are related to business regulation. (More information on the GOV.UK Search API: https://www.api.gov.uk/gds/gov-uk-search/) 

The Search API allows us to define filters and fetch the content to be ingested (HTML pages from GOV.UK). The content is fetched based on searching for content restricted to the filter_content_purpose_supergroup' of ‘guidance’ and ‘services’, as well as a list of about 500 taxonomies e.g.  ‘Oil’, ‘Export finance’ or ‘Pensions’. Another government department or affiliated body looking for content would apply different filters, potentially including different taxons e.g.  or filtering on publishing departments too. 

The Content API returns data in the form of JSONs for each content id/html page. These JSONs include a variety of data, ranging from the unique content_id, publishing dates, document types, taxonomy tags and the full text of the page. CART requires the data to be in tabular format/data frame. The pipeline code therefore manipulates the content API JSON data into one row per piece of content, with the column variables our interested metadata fields from the JSON. (More information on the GOV.UK Content API: https://www.api.gov.uk/gds/gov-uk-content/) 

The exhaustive list of metadata fields we extract and ingest are listed below. The data is used throughout the repo and is mandatory for data insights. At the time of writing in July 2026, the pipeline ingests ~50K pieces of content/rows. 

Name: content_id, public_url, document_type, format, categories, publishing_orgs, primary_publishing_org, title, abstract, html, text, attachments, mimetypes, attachment_titles, attachment_types, linked_content_raw, linked_content, date_published, updated_at, public_updated_at, publishing_app, withdrawn, is_historic, 

### Attachment pages 

It should be noted that during exploratory phase of ingesting the desired content from the GOV.UK Content API, we found that thousands of child publications and/or attachments were missing. Child publications and attachments are linked to within the JSON for the ‘parent’ html page. These content ids are embedded within the parent JSON are not found on the first Search API call; we extract these and then fetch all the remaining attachment/chil publication data. However, when fetching, as mentioned above, we filter the search API based certain metadata.  

Through extensive testing, we found that child publications **do not always inherit the parent pages metadata*, therefore were getting dropped. Other users of this methodolgy and the GOV.UK Search and Content API should be aware of this. To alleviate this issue, recursive calls for content ids found from a parent page, should not filter again on metadata criterion, but instead just grabs all the content. This is what we do, and it increased the ingested content by over 20K. 

## Crawl data 

### Screaming Frog 

Screaming Frog is an external agency that has developed search engine optimisation (SEO) software that crawls websites (in our case, GOV.UK content pages) and audits them. This can identify a significant number of metrics, including, but not limited to, broken links and missing metadata (titles, descriptions). The crawler allows you to export CSV files with all of this data.  

The Screaming Frog crawler is not the only SEO software for crawling sites. The  advantage of Screaming Frog and Google Analytics together, is that they can provide metadata on PDF pages that the GOV.UK Content API does not. The API data only has full metadata for HTML pages (as they have content ids). 

The Screaming Frog crawler can take a variety of input types in order to start crawling. These are Spider, List, SERP, API and Compare. We choose ‘List’ as we simply take all the GOV.UK public URLs ingested from the Content API pipeline, and upload to the crawler to audit. The crawler outputs large tables with data on each URL it hits. We extract information from the PDF attachments, HTML pages themselves, but also from the all the pages that link to/or lead from said pages (depth = 1). This allows us to see if there are broken links going into or leading from a GOV.UK page, which would impact it's quality and indicate a need for review.  

For more information on how the exported CSV data from the Screaming Frog tool is transformed for use within CART, see the TRANSFORMATION.md file. 

Those looking to adapt this methodology may use a different software to collate the metrics used in CART, but must ensure the below are present (or patch the code to use different data from an SEO crawler). These data are a mixture of integers and dates, for example the reading score is between 1 and 100, while PDF count has no numeric ceiling. The Screaming Frog crawler has hundreds of metrics but below are the ones we are using within CART and the ones that are selected from the exported CSV. 

Name: "public_url", "title_1", 'word_count', 'sentence_count', 'average_words_per_sentence', 'flesch_reading_ease_score', 'readability','pdf_modified', "pdf_created", 'pdf_page_count', "is_broken", "is_redirecting" 

As well as the urls from the, the other the data required from Screaming Frog (or another crawler), is detailed pdf data. After the List crawl from the urls ingested, you can go you can filter for all the pdfs the crawler found. This will be the pdfs on the html pages from the content API. These pages can now be run themselves to get the SF metadata.  

After exporting this page so you can take the list of pdfs URLs in the first column. Exactly as above, upload that list of pdf URLs with the same configurations, 

Like before, you let it run (ensuring that the configuration has all store pdf properties to be stored.) and then export the metadata. We also take one extra step with pdfs, extract the raw text. The pdf text is bulk exported as X number of text files (X being the number of pdfs SF extracted) into a folder, ready to be used within CART. We want this because the Content API gives us the full html text of a page, which is used to search for words in the audit tool. We use this feature of Screaming Frog to get the text from pdfs where possible, as we do not get it from the API. 

## GA4 data

### How it is gathered and cleaned

The GA4 data provides user interaction metrics for GOV.UK content, including page views, sessions, users and engagement behaviour. However, the structure and availability of these metrics varies depending on the type of content (HTML pages vs attachments), which required different handling approaches in the pipeline. 

GA4 data was housed in BigQuery as event-level tables (events_*) and processed datasets. These datasets contained raw event data and nested parameters, which were extracted and reshaped to make them usable for analysis.

### Joining GA4 data to content metadata 

GA4 data and GOV.UK content metadata were stored in different systems, which required an additional step before analysis. 

 - GA4 data was stored in BigQuery 
 - Content metadata is stored in DBTs internal system

To enable analysis, a curated content dataset was exported and manually uploaded into BigQuery.
This dataset defined the set of GOV.UK pages in scope and included the following key fields: 
 
- content_id
- public_url
- page_path
- document_type
- Categories
- primary_publishing_orgs
- publishing orgs
- Title
- Date_published
- Public_updated_ at
- linked_content
- is_historic
- Attachment count
- Linked content count
- Sessions
- Users
- New users
- Returning users
- Engagement time secs
- Total file downloads
- Users file downloads
- Content clicks
- Video views complete
- Total outbound clicks
- Total internal clicks
- Entrances
- Exits  
 
GA4 data was then joined to this dataset using a standardised URL field (page_path). This ensured that: 

- only in-scope content was included in analysis
- GA4 behavioural data could be aligned with content metadata
- outputs could be used consistently in downstream analysis 

*Another government department looking to replicate this process would likely need to find a similar, consistent join key across datasets.*

### Data extraction and cleaning 

The pipeline extracted relevant fields from GA4 event data, including page location, session identifiers and interaction events (e.g. downloads and clicks). Event parameters were stored in a nested structure (event_params). A standardised page_path field was derived from URLs, and URL fields were normalised (lowercased and trimmed) to ensure consistent joins across datasets. 

### Handling different content types in GA4 

A key consideration when working with GA4 data was that different types of content are measured differently. 

**HTML** pages collect GA4 data directly 
**Non-HTML** attachments (e.g. PDFs) do not generate GA4 events 
**HTML attachments** behave like pages but can be treated differently depending on how the data is structured 

This required different approaches to ensure the data remained meaningful and usable. 

### Deriving metrics for non-HTML attachments 

For non-HTML attachments, GA4 metrics were derived from user behaviour on parent pages (for example, users clicking download links or navigating to files). Metrics such as sessions, users and downloads therefore reflected interactions on the parent page rather than the attachment itself. 

To support this, GA4 data for attachments was structured using a parent-child relationship, where each row represented a parent page and an associated attachment. 

This approach preserved where interactions occurred, allowed the data to be joined back to the content dataset and ensured consistency with the structure of the original content data.

However, this introduced limitations as attachments could appear multiple times if they had multiple parent pages and user metrics could not be safely aggregated across those row.

*Another department implementing a similar approach may need to consider whether preserving interaction context is more important than simplifying the dataset for aggregation.* 

### Handling HTML attachments 

HTML attachments required a separate approach, as they could either be treated as standard HTML pages or handled in the same way as other attachments. 

Two approaches were considered: 

- treating HTML attachments as standalone pages (one row per page, full GA4 metrics)
- deriving metrics from parent pages (consistent with non-HTML attachments) 

We chose to treat HTML attachments as standalone pages and extract them as one row per page with full GA4 metrics. 

This ensured full engagement data was available and HTML attachments were consistent with other HTML content.

The trade-off was that parent-child relationships were not retained in the same structure, making it harder to attribute interactions back to the pages where they were accessed. 

*Another department replicating this approach would need to decide on analytical priorities here.*

### Session construction and aggregation 

Session identifiers were created by combining the GA4 session ID (ga_sessionid) with the user identifier (user_pseudo_id). This allowed events belonging to the same user visit to be grouped together and counted consistently as sessions. 

Metrics such as sessions, users and interaction counts (e.g. downloads and clicks) were then calculated by aggregating event data at page level. 

### Data standardisation and preparation 

Before analysis, several cleaning steps were applied: 

- extracting and selecting relevant event parameters
- standardising URL fields to create a consistent join key (page_path)
- separating content types (HTML vs attachments)
- retaining duplicated rows where necessary to preserve behavioural context 
