# Adapting the tool for your department
 
## Purpose
 
This document explains what another government department or agency needs to consider before adapting the Content Audit Review Tool for its own GOV.UK content.
 
The tool was developed in the Department for Business and Trade (DBT). It depends on the data sources, access permissions, secure environment and technical support available to DBT.
 
Other organisations may be able to reuse the audit approach, rules, data model and documentation. They should not assume they can copy the tool and run it unchanged.
 
## Summary
 
The audit tool depends on:
 
- a secure environment for ingesting, joining and analysing data
- access to GOV.UK APIs and the ability to configure them into a content pipeline
- access to GOV.UK Google Analytics data that can be matched to the content pipeline
- access to a web crawl solution, such as Screaming Frog, and the ability to configure and process crawl data
- people with data pipeline and data analysis skills, including Python experience
- permission to run Streamlit, or an alternative dashboard tool, securely
- performance analysis expertise, especially if custom flag rules are needed
- content expertise to interpret and act on the audit outputs
 
Departments are most likely to reuse:
 
- the audit method
- the data dictionary
- the flag rules
- the recommendation logic
- the structure and principles of the audit reports
- parts of the code, if they use a similar technical stack
 
 
## 1. Secure data environment
 
DBT’s version of the tool ingests and analyses data in Data Workspace.
 
The tool combines several datasets, including GOV.UK analytics data that is not publicly available. Departments adapting the tool need a secure environment that can:
 
- store source data
- process and join datasets
- run Python code
- apply audit rules
- generate outputs
- control access to non-public data
 
Departments should confirm:
 
- where data will be stored and processed
- who can access the source data and outputs
- what data governance applies
- whether GOV.UK Google Analytics data can be used in the chosen environment
- what security, IT or information assurance approvals are needed
 
The tool should not be run from a local machine, shared drive or unmanaged environment unless that environment has been approved for the data being used.
 
## 2. Data sources
 
The tool uses 3 main external data sources:
 
- GOV.UK content and metadata
- GOV.UK Google Analytics data
- crawl data
 
The pipeline also creates derived and calculated fields. These are not gathered directly from one source. They are created by applying logic to one or more source fields.
 
Examples include:
 
- file extension
- heading count
- expected reading time
- whether PDF content has an accessible HTML equivalent
- flag issue fields
- recommendations for action
 
### GOV.UK Google Analytics data
 
The tool uses GOV.UK Google Analytics data to understand reach and engagement.
 
Depending on the audit scope, the pipeline may need analytics for both HTML and non-HTML content.
 
DBT’s performance analysts use GOV.UK GA4 data accessed through approved internal routes. This includes BigQuery-based GOV.UK GA4 datasets and a flattened production dataset that is easier to query for analysis and reporting.
 
Departments adapting the tool need to confirm:
 
- whether they have access to GOV.UK GA4 data
- whether they can query the flattened production dataset
- whether they need access to raw GA4 datasets
- whether their access includes the HTML and non-HTML content needed for their audit scope
- what approvals apply under the GOV.UK GA4 access policy
 
Analytics data should be treated as non-public data.
 
### Crawl data
 
DBT’s audit tool uses a web crawler developed by a third party, Screaming Frog, to produce crawl data.
Importantly, the crawler also scrapes PDFs for all text content, which allows for keyword filtering and textual analysis of PDFs.  
 
Departments that want to adopt this part of the approach need:
 
- access to a web crawler
- an appropriate licence, if using a commercial tool
- someone who can configure the crawl
- a process for exporting and cleaning crawl data
- a way to join crawl outputs into the master dataset
 
Departments can use a different crawler, but they will need to adapt the pipeline, transformation logic and data dictionary.

For field definitions, see `docs/DATA-DICTIONARY.md`
For collection and preparation steps, see `docs/DATA-PIPELINE.md`
For cleansing and standardisation logic, see `docs/TRANSFORMATION.md`
 
## 3. Running Streamlit in the secure data environment
 
DBT presents the analysed data through a Streamlit dashboard.
 
Streamlit is an open-source Python framework for building data apps. In DBT’s setup, Streamlit runs inside Data Workspace.
 
Departments that want to reuse the dashboard code need to confirm they can:
 
- run Python code
- use Streamlit
- deploy or host the dashboard securely
- control access to the dashboard
- connect the dashboard to the analysed dataset
- meet internal IT, cyber security and information assurance requirements
 
Using Streamlit may require approval from IT, security or platform teams.
 
If a department cannot use Streamlit, it may still be able to reuse the audit rules, data dictionary and recommendation logic. It is unlikely to be able to reuse the dashboard code without significant changes.
 
For executable logic, see`docs/FLAGGING_RULES.md`
For the flag rule descriptions, see `audit-tool-streamlit/rules.yaml`
 
## 4. Alternative dashboard or reporting tools
 
Departments do not have to use Streamlit.
 
They could present the analysed data through another tool or platform, such as:
 
- an internal dashboarding platform
- a managed analytics tool
- a custom web application
- a reporting pipeline
- spreadsheet-based outputs
 
Using a different front-end will usually mean rebuilding the dashboard layer.
 
They should expect to adapt or rewrite:
 
- dashboard code
- filters
- visualisations
- export functionality
- user interface logic
- Streamlit-specific components
 
The current report converter expects CSV exports in the structure produced by the dashboard. Departments using a different dashboard or reporting tool will need to reproduce that CSV structure or adapt the converter.
 
## 5. Skills and roles needed
 
Departments will need access to:
 
- data scientists or data engineers to build pipelines, join datasets and maintain the dashboard
- performance analysts to access and interpret GOV.UK GA4 data
- someone who can procure, configure and manage a crawl tool such as Screaming Frog
- content designers or content strategists to interpret outputs and decide what action is needed
- security, IT or platform colleagues to approve the data environment, Streamlit or any alternative dashboard tool
 
 
### 6. Audit method
 
The overall method can be reused:
 
1. Identify the content scope.
2. Collect content and metadata.
3. Join analytics and crawl data.
4. Apply rules.
5. Generate flags and recommendations.
6. Review outputs with content experts.
7. Produce reports or exports for stakeholders.

 
## 7. Suggested implementation approach
 
Departments should start with a limited implementation.
 
1. **Confirm the content scope** 
   Decide which GOV.UK content is in scope.
 
2. **Confirm the data environment** 
   Identify where data will be stored, processed and accessed.
 
3. **Confirm data access** 
   Check access to GOV.UK metadata, GOV.UK GA4 data and crawl data.
 
4. **Create a test dataset** 
   Build a small, joined dataset before attempting to scale.
 
5. **Apply a small set of rules** 
   Start with a limited number of high-confidence flag rules.
 
6. **Review outputs with content experts** 
   Check whether the rules produce useful and credible results.
 
7. **Decide how users will access outputs** 
   Confirm whether to use Streamlit, another dashboard tool, CSV exports or reports.
 
8. **Adapt rules and reports** 
   Adjust thresholds, labels and report wording for the department’s context.
 
9. **Document limitations** 
   Record what the tool can and cannot show.
 
10. **Plan the next phase** 
   Decide whether to scale, integrate with content lifecycle tools, or develop a more production-ready service.
 
## 8. Readiness checklist
 
Before adapting the tool, departments should confirm that they have:
 
[ ] a clear content scope
[ ] a secure environment for processing data
[ ] access to GOV.UK content and metadata
[ ] access to relevant GOV.UK GA4 data
[ ] access to a crawl tool or equivalent crawl data
[ ] people with the skills to build pipelines, analyse data and maintain the dashboard
[ ] content specialists who can interpret outputs
[ ] approval to use Streamlit or an alternative dashboard/reporting tool
[ ] a plan for reviewing and acting on the findings
