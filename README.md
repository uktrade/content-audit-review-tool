# CART (Content Audit Review Tool)

## What this is

Content Audit Review Tool (CART) is a scalable content auditing tool that applies data-driven and rule-based approaches to evaluate GOV.UK content.

It is not a plug-and-play product or package. The repository defines a structured framework and modular components that teams can adapt to their own data sources, content and audit requirements.

## What CART does

CART audits content by combining multiple data sources and applying defined rules to identify potential issues.

It brings together:

- GOV.UK content and publishing metadata
- Google Analytics 4 (GA4) data (for traffic and engagement signals)
- Crawl data (for structural and content insights)
- Derived data – variables calculated from existing data to generate new insights, such as expected reading time

The output is a set of flags and metrics that help teams prioritise content improvements.

## What is included in this repo

This repository contains the core components needed to run CART:

- Audit rules: definitions of the checks used to flag content issues
- Metrics definitions: standardised definitions for analytics and content metrics
- Data pipeline approach: how content, analytics, and crawl data are collected and prepared
- Transformation logic: processes for cleaning, standardising and joining datasets
- Rules engine: Executable logic that applies rules and generates audit outputs

Together, these components provide a consistent, repeatable way to audit large volumes of content.

## Key constraints

CART is designed around a specific technical setup and is not directly portable:

- Implemented in DBT's Data Workspace - a secure data environment
- Uses Streamlit for presenting outputs
- Assumes access to GA4 export data and crawl outputs
- Built around GOV.UK-specific structures (for example URLs, document types and formats), so would require adaptation to work with other content platforms

Teams adopting CART will need to adapt it to their own environment and data sources.

## How to use

If you are new to CART, start with:

- docs/OVERVIEW to understand the purpose, users and value
- docs/ADAPT_FOR_YOUR_DEPT for guidance on implementing CART in your context

Then explore:

- Data pipeline and transformation documentation
- Data dictionary
- Rules logic

## Repository structure

At a high level, the repository is organised as follows:
- /audit_tool_streamlit contains all code and analysis, including audit logic
- /docs contains all supporting documentation (data dictionary, adaptation guidance, data sources etc)

(See individual files for more detail.)

## Feedback and contributions

If you have feedback, questions, or suggestions, please use GitHub Issues in this repository.

This helps us track improvements and support others using CART.
