# App

This readme file explains how the dashboard works.

## app.py
The dashboard is created using streamlit. In order to preview the app while developing it, you need to run this command in the terminal:

```
streamlit run app/app.py --server.port 9000
```

Streamlit works by refreshing and re-running the entire `app.py` script every time something changes in the app. For this reason we make heavy use of streamlit's built-in session state which allows variables to persist when the script refreshes. For example, we use this to keep the underlying dataframe in memory and to avoid redrawing all of the graphs.

```
# Initialize session state
if "data" not in st.session_state:
      st.session_state.data = ds.load_data_with_filters(columns=st.session_state.columns)

```

### Searching / Filtering

Filtering is handled by a sidebar. Every time you click on the "Update Search!" button, the chosen filters are applied:

```
st.button("Update Search!", key="apply_all_filters", on_click=refresh_all)
```
All column names of the dataframe are saved to the session state, and the `get_all_column_types` function is used to also keep track of the type of each column. Each different type of column has a different filter type.

The column types supported are:
1. Text - A free text field.
2. Categorical (text but with fifty or fewer different values) - Dropdown multiselect.
3. Numeric - `st.number_input` with min and max values derived from the column
4. Boolean (True or False) - A checkbox
5. Date - `st.date_input` with min and max values derived from the column
6. List - Dropdown multiselect

Each filter is selected from a dropdown multiselect box.

Filters are stored as tuples in a list with all relevant information: 

```
if column_filter is not None:
    if column_filter != []:
        current_filters.append((column_selected, column_type, column_filter, column_invert))
```

This list is used when the `apply_all_filters` button is triggered in order to load filtered data.

### Loading filtered data

The function `load_data_with_filters` is used to create a sql query to apply the current filters and read the data. It parameterises the search using a class called `parameter_index_generator` or `pig` to generate unique parameter ids for each `WHERE` condition. 

The function effectively loops through the `current_filters` list and writes a `WHERE` condition for each one and concatenates them all together before passing the full query and the list of safe parameters to the database query function.

```
all_data = db.query(query, params=all_parameters)
```
Some minor cleaning is performed, such as converting list and date columns to the correct column type.

### Data Viewer

The dashboard's main panel starts with a `st.dataframe` that shows a preview of the top 100 rows under the current filters. There is an option here to download the data as a CSV file. Since streamlit download buttons require the data to already be converted to a CSV (taking up valuable time and space) we use a "prepare download" button to make sure that the CSV is only generated if required.

### Visualisations.

The dashboard's various visualisations are created by functions in the `data_visualisation.py` script. These visualisations are stored in the session space and only regenerated when the filters are updated.

### History tab

When filters are applied, the current filters are saved to a dictionary.

```
def save_current_filters(filter_name):
    st.session_state.saved_filters[filter_name] =  current_filters
```

This is used in the history tab to keep track of previously applied filters and to revert to them.

### Definition tab

Column descriptions are taken from the data dictionary and used to give definitions in the dashboard itself.