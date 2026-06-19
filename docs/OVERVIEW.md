# Content audit tool overview

## Purpose of the audit tool

The content audit tool has been developed by the Proactive Content Management team in the Trade and Regulatory Services directorate of the Department for Business and Trade (DBT).

It identifies business guidance on GOV.UK that may need to be fixed, reviewed or removed.

It aims to support content designers and content owners across government to improve this guidance, making it easier for businesses to comply with regulation and reduce their admin burden.

The tool combines GOV.UK content metadata, Google Analytics data and crawl data. It then applies rules to identify red flags at scale.

Red flags are signals that content may not meet certain quality thresholds, such as usability, accessibility or user need.

The tool does not make final content decisions. It provides evidence and prioritisation signals to help content teams decide where human review is needed most.

## Background

DBT owns and contributes to a large amount of business guidance on GOV.UK. As part of its commitment to reducing the administrative burden on businesses, DBT also has an important role in helping ensure that regulatory guidance for businesses across GOV.UK is clear, usable, up to date and fit for purpose.

This includes content published by other departments and agencies.

Content improvement work starts with understanding what content already exists. But auditing large volumes of content is difficult. Current estimates suggest the GOV.UK business guidance estate could contain between 100,000 and 200,000 pages, and it continues to grow faster than teams can realistically review manually.

The audit tool has been developed to make large-scale content auditing quicker, more consistent, repeatable and evidence-based.

It is intended to support content improvement by:

- speeding up the audit process, reducing work that could take weeks to hours
- helping teams prioritise which content to review first
- giving teams more objective evidence to support content decisions
- creating clearer and more compelling evidence for stakeholders to engage with content improvement work

## Who the tool is for

The tool is currently used directly by a small number of DBT content designers in the Proactive Content Management team.

These content designers use the tool to explore content data, identify potential issues, prioritise content for review and produce outputs for other teams and stakeholders.

Other users are consumers of the tool’s outputs, rather than direct users of the tool itself.

These audiences include:

- content owners, such as policy teams and service owners in DBT and other government departments, who need to understand the state of their content
- content designers in DBT and other government departments, who may need to support content owners to review and improve content
- senior decision makers, such as heads of content, policy leads and service owners, who may need to agree priorities, resource or action for content improvement work

The tool’s outputs include raw CSV data, prioritised content recommendations and summary reports.

These outputs help teams:

- understand the issues in a specific area of content
- decide whether content improvement work is needed
- prioritise which content to review first
- develop a plan for reviewing, improving or removing content

## What the tool does

The tool currently has 6 main elements.

### 1. Data pipeline

The tool combines data from several sources, including:

- GOV.UK content and metadata
- GA4 analytics
- Screaming Frog crawl data

This creates a structured dataset that can be analysed, filtered and exported.

For more detail, see:

`docs/data-pipelines.md`

### 2. Red-flag rules

The tool applies rules to identify content that may not meet certain content quality thresholds.

The rules look at broad areas such as:

- usability
- accessibility
- freshness
- relevance to user needs

They flag issues such as:

- low or no traffic
- broken links
- outdated or potentially stale content
- PDFs without accessible HTML alternatives
- content that may be too long or hard to use

The rules are not proof that content is bad. They are signals that a human may need to consider the content for review, removal, improvement or conversion.

For more detail, see:

`docs/red-flag-rules.md`

### 3. Dashboard

The dashboard allows users to explore the dataset, filter content and download CSV subsets for further audit work.

It is currently built in Streamlit, an open-source Python framework.

The dashboard is intended for internal analysis and content review. It is not currently a fully fledged digital tool or service.

For more detail, see:

`docs/dashboard.md`

### 4. Topic and subset analysis

The tool includes early features to help users identify groups of related content.

These include:

- filtering by topic or taxon metadata
- keyword searching within HTML and PDF body text
- support for regex and Boolean operators in keyword search

This work is limited by the current data structure and platform.

More advanced search and discovery features, such as BM25 keyword search, semantic search or knowledge graphs, will likely need a more scalable technical approach.

Further developments in this area will be documented in this repository.

### 5. LLM-assisted fact checking

There has been early thinking and some experimentation around using large language models to support fact checking at scale.

The aim is to explore whether LLMs can help identify content that may contain factual inaccuracies or claims that need to be checked against trusted sources.

This work is exploratory.

Further developments in this area will be documented in this repository.

### 6. Content reports

DBT’s Proactive Content Management team has also developed a standalone tool that can convert CSV data from the audit tool into readable reports for content teams and senior stakeholders.

Reports are designed to summarise:

- the size and scope of a content dataset
- how many items are flagged
- common issue types
- recommended actions
- high-priority content items
- possible candidates for review, removal or conversion

As with the dashboard, the converter is intended for internal use, though its outputs are designed to be shared more widely. It is not currently a fully fledged digital tool or service.

For more detail, see:

`docs/content-reports.md`

## How the analysis works

The tool uses data signals to identify content that may need attention.

Behind the scenes, the typical flow is:

1. Content and metadata are collected from GOV.UK.
2. Analytics and crawl data are joined to the content dataset.
3. Red-flag rules are applied.
4. Content items receive issue flags and recommendations.

From a user’s point of view, DBT content designers can:

1. Explore the results in the dashboard.
2. Export CSV subsets for review or reporting.
3. Generate content reports from CSV data for stakeholders.

The tool separates 3 things.

### Signal

A signal is evidence that something may need attention.

Example: this page has broken links.

### Recommendation

A recommendation is the tool’s suggested next step based on one or more signals.

Example: strong candidate for review.

### Decision

A decision is made by a human reviewer or content owner.

Example: update the page because it is still needed but contains outdated guidance.

This distinction is important. The tool can support prioritisation, but final decisions require human judgement.

## Current status

The tool is currently an internal MVP.

It works from start to finish and can:

- bring together GOV.UK metadata, analytics and crawl data
- apply red-flag rules
- show results in a dashboard
- export filtered CSVs

A separate reporting tool also exists to convert CSV data into readable reports for stakeholders. This is less mature than the main dashboard and still needs to be productionised.

The next phases of work will focus on:

- improving and expanding the content pipeline from GOV.UK
- expanding the list of content issues the tool can detect
- refining the red-flag rules and related recommendations for action
- tracking offline decisions from content reviews and incorporating them into the tool, to avoid reviewed content being flagged again
- improving dashboard functionality and usability
- productionising content recommendation reports
- exploring whether LLMs can be used to flag potential inaccuracies in content
- exploring the ongoing suitability of Streamlit as a platform for the tool

For more detail, see:

`docs/roadmap.md`

## Limitations

The tool has important limitations.

### Rules support prioritisation, not final decisions

The tool identifies possible issues and helps teams prioritise review work. It does not decide whether content should be changed, removed or kept.

Content teams should review the evidence with content owners before action is taken.

### Data quality affects the outputs

The tool depends on the quality and completeness of its source data.

Known risks include:

- missing or inconsistent metadata
- gaps in analytics or crawl data
- publishing organisations may not always match who is responsible for content

Missing data means some content that should be flagged may not be flagged.

### Low traffic does not always mean low value

Some content may have low traffic but still be important because it is statutory, policy-critical or used by a small but important audience.

### The dashboard has platform constraints

The dashboard is currently built in Streamlit. This has helped the team move quickly, but may limit:

- performance
- usability
- decision tracking
- persistent data storage
- integration with other systems
- advanced search or topic analysis

### Decision tracking is not yet fully developed

The tool can identify content that may need action, but it does not yet provide a mature way to record review decisions, action status or ownership back into the tool.

This is a key area for future work.

## Related documentation

Detailed documentation sits outside this overview.

Recommended docs:

- `docs/data-pipelines.md`
- `docs/red-flag-rules.md`
- `docs/dashboard.md`
- `docs/content-reports.md`
- `docs/decision-tracking.md`
- `docs/limitations.md`
- `docs/roadmap.md`