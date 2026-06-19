## Data Pipleline and Sources

CART uses multiple data sources to gain insight into the quality of GOV.UK content. These data sources are the GOV.Uk Search and Content API for direct access to the content, webiste crawler data for common Search Engine Optimisation issues and Google Analytics. This file explains how content, analytics, and crawl data are collected and prepared for CART

### Gov.uk search and content API
how content is retrieved and key fields
DBT has a ingestion pipeline which utilises the search API to apply filters on GOV.UK content that are related to regulation/business. More information on the GOV.UK Search API :https://www.api.gov.uk/gds/gov-uk-search/

The search API allows us to define filters and fetch the content to be ingested (html pages from GOV.UK). The content is fetched based on the last updated date (since 2020), and a list of 'content_store_document_type' tags e.g. guidance, html_publication. Another government department or affiliated body looking for content would apply different filters, potineially including taxons e.g. 'construction' or publishing departments. 

The Content API returns data in the form of JSONs for each content id/html page. These JSONs have a variety of data included, ranging from the unique content_id, dates, type of content, taxonomy tags and the full text of the page. CART requires the data to be in tabular format/data frame. The pipeline code therefore manipulates the content API JSON data into one row per piece of contennt, with the column variables our interested metadata fields from the JSON.

The exhuastive list of metadata fields we extract and ingest are listed below. The data is used throughout the repo and is mandatory for data insights. At the time of writing, the pipeline ingests ~50K pieces of content/rows.

**Name**
content_id, public_url, document_type, format, categories, publishing_orgs, primary_publishing_org,	title, abstract, html, text, attachments, mimetypes, attachment_titles, attachment_types, linked_content_raw, linked_content, date_published, updated_at, public_updated_at, publishing_app, withdrawn, is_historic,


### Crawl data 
#### Screaming frog
Screaming frog (SF) is a Search Optimisation Engine (SEO) software that crawls websites (in our case, GOV.UK content pages) and audits them. This auditing identifies a significant amount of metrics, including but not limited to, broken links and missing metadata (titles, descriptions). SF allows you to export csv files with all of this data, providing vast information on the quality of content. Sf is not the only SEO software for crawling sites. The extra advantage of SF and Google Anaytics, is that they can provide metadata on pdf pages that the GOV.UK Content API does not. The API data only has full metadata for html pages (as they have content ids). 

Screaming frog can take a variety of input types in order to start crawling. These are Spider, List, SERP, API and Compare. We choose ‘List’ as we simply take all the GOV.UK public URLs ingested from the Content API pipeline, and upload to for SF to audit. The crawler outputs large tables with data on each url it hit. We extract information from the pdf attachments, html pages themselves, but also from the all the pages that link to/or lead from said pages (depth = 1). This allows us to see if there is broken links going into or leadsing from a GOV.UK page, which would impact it's quality and need for review. For more information on how the exported csv data from SF is transformed for use within CART, see the TRANSFORMATION.md file.

Those looking to adapt this methodology may use a different software to collate the metrics used in CART, but must ensure the below are present (or patch the code to use different data from an SEO crawler). These data are a mixture of integers and dates, for example the reading score is between 1 and 100, while pdf count has no numeric ceiling. SF has hundreds of metrics but the below are the ones we are using within CART and the ones that are selected from the exported csv.

"public_url", "title_1", 'word_count', 'sentence_count','average_words_per_sentence', 'flesch_reading_ease_score', 'readability','pdf_modified', "pdf_created", 'pdf_page_count', "is_broken", "is_redirecting"
 
### Google Analytics
