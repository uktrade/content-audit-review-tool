# audit-tool-streamlit

## Project Info

### Description

A streamlit app to interact with the results of the audit tool for gov.uk rergulations removals


### Expected Outputs



### Data and Assumptions

 

## How to use the code

This project uses the ADS cookiecutter. Generic guidance for using and developing cookiecut projects is below:

### Development setup

After spinning up Theia/Jupyter, navigate to the project directory and run `. setup.sh` in the terminal. This will read from a previously cached conda environment and activate this if it exists, otherwise this will generate and cache this environment for future use. This will take a few minutes to install packages included in your `pyproject.toml`. 

After running `. setup.sh` in your terminal,  the environment `audit-tool-streamlit` should appear in brackets at the start of the new command:
```
(audit-tool-streamlit) ~$ 
```
This can be deactivated using `conda deactivate` or activated using `conda activate audit-tool-streamlit`. Ensure this environment is selected when opening or adding new files to your project. The kernel can be selected on the top-right of your Jupyter window or bottom-left of your Theia window.

The cookiecutter structure installs packages through the `pyproject.toml` file - if you have any new requirements to add to your project, you'll need to add these to the dependencies section of the pyproject.toml file and then run `. setup.sh recreate` to save these or `. setup.sh recreate_temp` to install without caching.  

### Importing from this project

To import functionality from this project into your own project, install it as a package:

```
pip install audit_tool_streamlit@git+ssh://git@gitlab.data.trade.gov.uk/ag-data-science/audit-tool-streamlit.git
```

Or add it to your pyproject.toml:

```
dependencies = [
    "audit_tool_streamlit@git+ssh://git@gitlab.data.trade.gov.uk/ag-data-science/audit-tool-streamlit.git"
]
```

## Other projects / resources / citations

<!--- _Refer to the repos of other's work that you've drawn on heavily, key resources for the project, or citing essential reading - all where required. This can also be a good place to link to the licensing in your repo if relevant._ -->


-------------------------

## Project Management

### Author 

Analytical Data Science

### Developer Team
<!--- _Details on the developer team and their roles in the project. Include any quality assurers._

Name - Team - Role

Name - Team - Role

Name - Team - Role -->


### Customer Details

<!--- _Details on the customer team and their role in the project (e.g. are they now looking after the project long-term?)._

Name - Team - Role

Name - Team - Role

Name - Team - Role

-->

### Project Status
Scoping/EDA/Development/Testing/Deployed/Paused

<!---_This can include versioning if relevant._ -->

<br />

This project was set-up using the ADS cookiecutter. See the [ReadMe](https://gitlab.data.trade.gov.uk/ag-data-science/ads-cookiecutter/-/blob/main/README.md) for details on creating a cookiecut project.

<p><small>Based on the <a target="_blank" href="https://drivendata.github.io/cookiecutter-data-science/">cookiecutter data science project template. </a>.</small></p>
