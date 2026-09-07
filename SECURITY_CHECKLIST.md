# Code Security Checklist

Download this checklist from [GitHub](https://github.com/uktrade/platform-documentation/blob/main/docs-managed/docs/features/code-repository-hardening/code_security_checklist.md) and copy to the root of your repo.

Work through the checklist from top to bottom, ticking each item once you have confirmed it is true. Each item links to detailed guidance available in the [Code Repository Hardening guidelines](https://platform.readme.trade.gov.uk/managed/features/code-repository-hardening/).

Last updated: _add date_

## 1. Contributor controls

Actions each contributor takes for themselves, so everyone knows what the controls are and why they exist.

- [X] [All internal contributors have read the Code Repository Hardening guidelines](https://platform.readme.trade.gov.uk/managed/features/code-repository-hardening/)
- [X] [All internal contributors have completed code security training in the last year](https://platform.readme.trade.gov.uk/managed/features/code-repository-hardening/#security-training)
- [X] [All internal contributors have reviewed the GitHub Safety Tips on coding in the open](https://platform.readme.trade.gov.uk/managed/features/code-repository-hardening/#github-safety-tips)

## 2. Repository-level controls

Defences set up within the repository itself.

- [X] [A `.pre-commit-config.yaml` file exists so the organisation-approved hooks run before commits](https://platform.readme.trade.gov.uk/managed/features/code-repository-hardening/#pre-commit-hooks)
- [X] [Repository access has been reviewed](https://platform.readme.trade.gov.uk/managed/features/code-repository-hardening/#repository-access)
- [X] [A `CODEOWNERS` file exists so the right people review changes](https://platform.readme.trade.gov.uk/managed/features/code-repository-hardening/#codeowners)
- [X] [The pull request template reminds reviewers to check for secrets](https://platform.readme.trade.gov.uk/managed/features/code-repository-hardening/#pull-request-template)
- [X] [The repository security policy is inherited from the BIST GitHub Security Policy](https://platform.readme.trade.gov.uk/managed/features/code-repository-hardening/#repository-github-policy)
- [X] [The mandatory custom GitHub properties are set](https://platform.readme.trade.gov.uk/managed/features/code-repository-hardening/#custom-github-properties)
- [X] [Advanced CodeQL is set up if the repository accepts PRs from forks (optional)](https://platform.readme.trade.gov.uk/managed/features/code-repository-hardening/#codeql-for-fork-based-prs-optional)

## 3. Organisation-applied controls

Controls applied by an organisation administrator and verified by a repository administrator.

- [X] [The standard GitHub security configuration is applied to the repository](https://platform.readme.trade.gov.uk/managed/features/code-repository-hardening/#github-security-configuration)
- [X] [The default branch protection ruleset is applied to the default branch](https://platform.readme.trade.gov.uk/managed/features/code-repository-hardening/#branch-protection-rules)
- [X] [GitHub Secret Protection is enabled and blocking secrets](https://platform.readme.trade.gov.uk/managed/features/code-repository-hardening/#github-secret-protection)
- [X] [The relevant vulnerability scans are active](https://platform.readme.trade.gov.uk/managed/features/code-repository-hardening/#vulnerability-scanning)