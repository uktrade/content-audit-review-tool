import json
import os
import re
from itertools import chain

import numpy as np
import pandas as pd
from dwutils import db, s3

import audit_tool_streamlit.derived_columns as dc
from audit_tool_streamlit.RuleEngine import MultiCategoryRuleEngine


def read_csv_from_shared_folder(
    file_name, path="path/to/crawl_data/", team="example_team", **kwargs
):
    """
    Wrapper function for reading csv files from s3 shared folder.
    """

    with s3.read(path=os.path.join(path, file_name), team=team) as f:
        data = pd.read_csv(f, **kwargs)
    return data


def read_xlsx_from_shared_folder(
    file_name, path="path/to/ga_data/", team="example_team", **kwargs
):
    """
    Wrapper function for reading xlsx files from s3 shared folder.
    """
    with s3.read(path=os.path.join(path, file_name), team=team) as f:
        data = pd.read_excel(f, **kwargs)
    return data


def safe_mode(x):
    """
    Function that takes the mode of a pandas series, ignoring NA values.
    We use this as a way of deduplicating data by grouping by public_url and taking the most common value.

    pd.Series.mode() returns a series, therefore if a column has all NA values, it will return an pd.Series([]), and attempting to index it will
    cause an error. For this reason, we use a wrapper to return None if no mode is returned.
    params:
        x: pd.Series
    returns:
        dtype of x

    """
    m = x.dropna().mode()
    return m.iloc[0] if len(m) > 0 else None


def deduplicate_by_grouping(data, group_col):
    """
    Screaming frog data has duplicates with slightly different values.
    We group by public_url and take the most common (mode) value in each column.
    Before this, 404 rows are dropped for any address that also has a 200 row (the 404 rows
    have no data and would otherwise win the mode). Addresses with no 200 row keep their 404s.
    params:
        data: pd.DataFrame
        group_col: string. The column you want to group on
    returns:
        pd.DataFrame
    """
    status = pd.to_numeric(data["Status Code"], errors="coerce")
    has_200 = (status == 200).groupby(data[group_col]).transform("any")
    data = data[~((status == 404) & has_200)]
    return data.groupby(group_col).agg(lambda col: safe_mode(col)).reset_index()


def write_to_s3(data, table_name, schema="example_shared_schema", convert_cols=None):
    """
    Wrapper function for writing DataTables to s3 shared folder as tables.
    SQL doesn't know how to handle columns of lists or dictionaries, so we use json.dumps to convert them into strings so we
    can convert them back upon reading

    params:
        data: pd.Dataframe
        table_name: string. The name of the table in the shared folder you want to write to
        schema: string. The name of the shared folder you want to write to
        convert_cols: list(str). a list of columns in data that you want converted to strings using json.dumps
    returns:
        None
    """
    import sqlalchemy
    from sqlalchemy.engine.base import Engine

    engine: Engine = sqlalchemy.create_engine("dialect://")

    if convert_cols is not None:
        for col in convert_cols:
            data[col] = data[col].apply(json.dumps)

    with engine.connect() as connection:
        data.to_sql(
            table_name, con=connection, schema=schema, index=False, if_exists="replace"
        )


def write_to_catalogue(
    df,
    catalogue_schema="example_catalogue_schema",
    catalogue_table_name="example_content_table",
    team_name="example_shared_schema",
    table_name="example_master_table",
    convert_cols=None,
    comment=None,
):
    """
    Wrapper function around write_to_s3 and db.execute for writing a dataframe to a catalogue page.
    Used only for the main joined dataset.
    db execute moves a sql table to a catalogue page, therefore we must first write it to our shared area.
    db execute deletes the table from the shared area when doing this.

    params:
        df: pd.Dataframe
        catalogue_schema: string. schema of the catalogue item
        catalogue_table_name: string. table name of the catalogue item
        table_name: string. The name of the table in the shared folder you want to write to
        schema: string. The name of the shared folder you want to write to
        convert_cols: list(str). a list of columns in data that you want converted to strings using json.dumps
        comment: string. an optional comment to say why you are updating the catalogue table.
    returns:
        None
    """
    write_to_s3(df, table_name, team_name, convert_cols)
    db.execute(
        f"CALL publish_procedure('{team_name}', '{table_name}', '{catalogue_schema}', '{catalogue_table_name}', '{comment}');"
    )


################################################
# GA
################################################


def read_ga_files(file_names, **kwargs):
    """
    Uses a list comprehension to read all GA files at once
    """
    return [
        read_xlsx_from_shared_folder(file_name, **kwargs) for file_name in file_names
    ]


def concat_ga_data(ga_data_list, keep_columns=None):
    """
    Takes a list of GA dataframes (html content , html attachments, non-html attachments),
     concatenates them together and keeps only the columns specified.
    """
    ga_data = pd.concat(ga_data_list, ignore_index=True)
    if keep_columns is not None:
        ga_data = ga_data[keep_columns]
    return ga_data


def ga_data_pipeline(write=True):
    """
    Wrapper function that takes the raw GA files, joins them together and saves to s3 shared folder.
    """
    print("ga_data_pipeline: starting")
    file_names = [
        "CART non html attachments combined.xlsx",
        "CART html attachments combined.xlsx",
        "CART pages output combined.xlsx",
    ]

    column_names = [
        "public_url",
        "sessions",
        "engaged_sessions",
        "users",
        "engagement_time_secs",
        "total_file_downloads",
        "file_downloads",
        "navigation",
    ]

    print(f"ga_data_pipeline: reading {len(file_names)} GA files")
    ga_data_list = read_ga_files(file_names)
    print("ga_data_pipeline: concatenating GA files")
    ga_data = concat_ga_data(ga_data_list, column_names)
    print("ga_data_pipeline: deduplicating by public_url")
    ga_data = deduplicate_by_grouping(ga_data, "public_url")
    if write:
        print("ga_data_pipeline: writing to s3")
        write_to_s3(ga_data, "example_ga_table")
    print("ga_data_pipeline: done")
    return ga_data


################################################
# SF
################################################


def prepare_screaming_frog_data(screaming_frog_df, depth_df, url_list=None):
    """
    Function takes the Screaming Frog output and joins it to the content data
    params:
        screaming_frog_df: pd.DataFrame - the URL level data from screaming frog. Contains columns like "Word Count" and "average_words_per_sentence"
        depth_df: pd.DataFrame - A dataframe that with "From" and "To" columns that show the traversal SF took to find the pages. Used to connect SF data to parent pages.
        url_list: list - a list of urls in the gov.uk content dataframe and its attachments. Filter the results to only include these URLs which we have other data for.
    """
    print(f"prepare_screaming_frog_data: starting with {len(screaming_frog_df)} rows")

    # join the depth_df to get a parent relationship (left join because not all results have one)
    sf_df = screaming_frog_df.merge(
        depth_df[["From", "To"]],
        left_on="Address",
        right_on="To",
        how="left",
        validate="1:m",
    )
    print("prepare_screaming_frog_data: joined depth data")

    sf_df = sf_df.rename(columns={"From": "parent_public_url", "Address": "public_url"})
    print("prepare_screaming_frog_data: joined content data for parent urls")

    # we can have duplicates here, where an Address was associated with multiple parent URLs that were not in the content df, so they all show up as NA
    # drop these dupes
    sf_df = sf_df.drop_duplicates(subset=["parent_public_url", "public_url"])

    # derive metrics
    sf_df["is_broken"] = sf_df["Status Code"] == 404
    sf_df["is_redirecting"] = ~sf_df["Redirect Type"].isna()
    print("prepare_screaming_frog_data: derived is_broken and is_redirecting")

    broken_redirect_summary_df = (
        sf_df.groupby("parent_public_url")
        .agg(
            n_links=("parent_public_url", "size"),
            n_broken_links=("is_broken", "sum"),
            n_redirecting_links=("is_redirecting", "sum"),
        )
        .reset_index()
    )

    broken_urls_df = (
        sf_df[sf_df["is_broken"]]
        .groupby("parent_public_url")["public_url"]
        .apply(list)
        .reset_index(name="broken_urls")
    )
    broken_redirect_summary_df = broken_redirect_summary_df.merge(
        broken_urls_df, on="parent_public_url", how="left"
    )
    broken_redirect_summary_df["broken_urls"] = broken_redirect_summary_df[
        "broken_urls"
    ].apply(lambda x: x if isinstance(x, list) else [])
    print("prepare_screaming_frog_data: built broken/redirect summary")

    # we are DONE with parent_url, so can drop it and deduplicate by public_url to remove duplicates caused by multiple parent urls
    sf_df = sf_df.drop(columns=["parent_public_url"]).drop_duplicates("public_url")

    # filter to only include these URLs which we have other data for.
    if url_list is not None:
        sf_df = sf_df[sf_df["public_url"].isin(url_list)]

    # we can have duplicates here, where an Address was associated with multiple parent URLs that were not in the content df, so they all show up as NA
    # drop these dupes
    print(f"prepare_screaming_frog_data: done ({len(sf_df)} rows)")
    return sf_df.reset_index(drop=True), broken_redirect_summary_df


def combine_data(output_dfs, link_summary_dfs):
    """
    Concatenates the SF data together and
    """
    print(f"combine_data: starting, combining {len(output_dfs)} dataframes")

    assert len(output_dfs) == len(link_summary_dfs)

    # get the total number of links across all summary dfs
    # these are from different sources, so adding is fine, as they cannot be the same links in both!

    link_summary_df = (
        pd.concat(link_summary_dfs)
        .groupby("parent_public_url")
        .agg(
            n_links=("n_links", "sum"),
            n_broken_links=("n_broken_links", "sum"),
            n_redirecting_links=("n_redirecting_links", "sum"),
            broken_urls=("broken_urls", lambda x: list(set(chain.from_iterable(x)))),
        )
        .reset_index()
        .rename(columns={"parent_public_url": "public_url"})
    )
    print("combine_data: built combined link summary")

    output_df = pd.concat(output_dfs)

    # tidy column names
    output_df.columns = (
        output_df.columns.str.lower()
        .str.replace(" ", "_")
        .str.replace("-", "_")
        .str.replace("(", "")
        .str.replace(")", "")
    )

    keep_cols = [
        "public_url",
        "title_1",
        "word_count",
        "sentence_count",
        "average_words_per_sentence",
        "flesch_reading_ease_score",
        "readability",
        "pdf_modified",
        "pdf_created",
        "pdf_page_count",
        "is_broken",
        "is_redirecting",
    ]

    output_df = output_df[keep_cols]

    output_df = output_df.drop_duplicates(subset="public_url")
    print(f"combine_data: deduplicated output data ({len(output_df)} rows)")

    # and merge the lists of parent info back on
    output_df = output_df.merge(
        link_summary_df, how="left", on="public_url", validate="1:1"
    )
    # pages with no link summary get a float NaN from the left merge, which json.dumps writes as the string "NaN"
    output_df["broken_urls"] = output_df["broken_urls"].apply(
        lambda x: x if isinstance(x, list) else []
    )
    output_df["screaming_frog_available"] = True
    date_columns = ["pdf_modified", "pdf_created"]
    for col in date_columns:
        output_df[col] = pd.to_datetime(output_df[col], errors="coerce")

    print("combine_data: done")
    return output_df


def sf_data_pipeline(write=True):
    """
    Hardcoding all the nonsense required to read each of these messy csvs
    """
    print("sf_data_pipeline: starting")

    SF_DATA_KEEP_COLS = [
        "Address",
        "Title 1",
        "Word Count",
        "Sentence Count",
        "Average Words Per Sentence",
        "Flesch Reading Ease Score",
        "Readability",
        "PDF Modified",
        "PDF Created",
        "PDF Page Count",
        "Status Code",
        "Redirect Type",
    ]
    SF_DATA_DTYPES = {
        "Address": str,
        "Title 1": str,
        "Word Count": "Int64",
        "Sentence Count": "Int64",
        "Average Words Per Sentence": "float64",
        "Flesch Reading Ease Score": "float64",
        "Readability": str,
        "PDF Page Count": "Int64",
        "Status Code": "Int64",
        "Redirect Type": str,
    }
    SF_DATA_DATE_COLS = ["PDF Modified", "PDF Created"]

    # external html
    print("sf_data_pipeline: reading external html files")

    print("sf_data_pipeline: reading depth df")
    screaming_frog_depth_df_html_ext = read_csv_from_shared_folder(
        file_name="html_external/all_html.csv", dtype={"Alt Text": str}
    )

    print("sf_data_pipeline: deduplicating")
    screaming_frog_depth_df_html_ext = screaming_frog_depth_df_html_ext.drop_duplicates(
        subset=["From", "To"]
    )

    print("sf_data_pipeline: reading data df")
    screaming_frog_data_df_html_ext = read_csv_from_shared_folder(
        file_name="html_external/Html_ext_data.csv",
        usecols=SF_DATA_KEEP_COLS,
        dtype=SF_DATA_DTYPES,
        parse_dates=SF_DATA_DATE_COLS,
        lineterminator="\n",
    )

    print("sf_data_pipeline: deduplicating")
    screaming_frog_data_df_html_ext = deduplicate_by_grouping(
        screaming_frog_data_df_html_ext, "Address"
    )

    # internal html
    print("sf_data_pipeline: reading internal html files")
    print("sf_data_pipeline: reading depth df")
    screaming_frog_depth_df_html_int = read_csv_from_shared_folder(
        file_name="html_internal/all_int_html.csv",
        dtype={"Alt Text": str, "Target": str, "Rel": str},
    )

    print("sf_data_pipeline: deduplicating")
    screaming_frog_depth_df_html_int = screaming_frog_depth_df_html_int.drop_duplicates(
        subset=["From", "To"]
    )

    print("sf_data_pipeline: reading data df")
    screaming_frog_data_df_html_int = read_csv_from_shared_folder(
        file_name="html_internal/html_int_data.csv",
        usecols=SF_DATA_KEEP_COLS,
        dtype=SF_DATA_DTYPES,
        parse_dates=SF_DATA_DATE_COLS,
        lineterminator="\n",
    )

    print("sf_data_pipeline: deduplicating")
    screaming_frog_data_df_html_int = deduplicate_by_grouping(
        screaming_frog_data_df_html_int, "Address"
    )

    # pdf
    print("sf_data_pipeline: reading pdf files")
    print("sf_data_pipeline: reading depth df")
    screaming_frog_depth_df_pdf = read_csv_from_shared_folder(
        file_name="pdf/all_pdfs.csv"
    )

    print("sf_data_pipeline: deduplicating")
    screaming_frog_depth_df_pdf = screaming_frog_depth_df_pdf.drop_duplicates(
        subset=["From", "To"]
    )

    print("sf_data_pipeline: reading data df")
    screaming_frog_data_df_pdf = read_csv_from_shared_folder(
        file_name="pdf/all_pdfs_data.csv",
        usecols=SF_DATA_KEEP_COLS,
        dtype=SF_DATA_DTYPES,
        parse_dates=SF_DATA_DATE_COLS,
        lineterminator="\n",
    )

    print("sf_data_pipeline: deduplicating")
    screaming_frog_data_df_pdf = deduplicate_by_grouping(
        screaming_frog_data_df_pdf, "Address"
    )

    # html data should never have a pdf page count but sometimes it's 0 instead of missing.
    screaming_frog_data_df_html_ext["PDF Page Count"] = screaming_frog_data_df_html_ext[
        "PDF Page Count"
    ].replace(0, np.nan)
    screaming_frog_data_df_html_int["PDF Page Count"] = screaming_frog_data_df_html_int[
        "PDF Page Count"
    ].replace(0, np.nan)

    print("sf_data_pipeline: preparing pdf data")
    pdf_output, pdf_link_summary = prepare_screaming_frog_data(
        screaming_frog_data_df_pdf, screaming_frog_depth_df_pdf
    )
    print("sf_data_pipeline: preparing external html data")
    html_ext_output, html_ext_link_summary = prepare_screaming_frog_data(
        screaming_frog_data_df_html_ext, screaming_frog_depth_df_html_ext
    )
    print("sf_data_pipeline: preparing internal html data")
    html_int_output, html_int_link_summary = prepare_screaming_frog_data(
        screaming_frog_data_df_html_int, screaming_frog_depth_df_html_int
    )

    print("sf_data_pipeline: combining all screaming frog data")
    full_screaming_frog_data = combine_data(
        output_dfs=[pdf_output, html_ext_output, html_int_output],
        link_summary_dfs=[
            pdf_link_summary,
            html_ext_link_summary,
            html_int_link_summary,
        ],
    )

    if write:
        print("sf_data_pipeline: writing to s3")
        write_to_s3(
            full_screaming_frog_data,
            "example_crawl_table",
            convert_cols=["broken_urls"],
        )

    print("sf_data_pipeline: done")
    return full_screaming_frog_data


################################################
# attachments
################################################


def is_extension(end_of_url, ban_list=["gov", "uk", "org", "net", "com"]):
    letters_only = re.match("[A-Za-z]{0,5}$", end_of_url)
    not_banned = end_of_url.lower() not in ban_list
    return bool(letters_only) & not_banned


def identify_child_content(df):
    """
    function that identifies linked child content in the data by finding matches in linked_content_raw to
    content id and public url in the main dataset. This function returns a subset of the child pages, along with their relevant
    parent content id and public url
    """
    print(f"identify_child_content: starting with {len(df)} rows")

    df["attachment_titles"] = df["attachment_titles"].apply(
        lambda x: x if isinstance(x, list) else []
    )

    # explode only works if the lists are the same length ie attachment title exists.
    atmt_df_1 = df[df["attachment_titles"].apply(len).ge(1)].explode(
        ["attachments", "attachment_titles"], ignore_index=True
    )
    # use two
    atmt_df_2 = df[df["attachment_titles"].apply(len).eq(0)].explode(
        ["attachments"], ignore_index=True
    )
    atmt_df_2["attachment_titles"] = None

    atmt_df = (
        pd.concat([atmt_df_1, atmt_df_2], ignore_index=True)
        .dropna(subset="attachments")
        .drop_duplicates(subset=["public_url", "attachments"])
        .drop(columns=["linked_content_raw"])
    )

    atmt_df = atmt_df.rename(
        columns={
            "content_id": "parent_content_id",
            "public_url": "parent_public_url",
            "attachments": "public_url",
        }
    )

    atmt_df["public_url"] = atmt_df["public_url"].str.replace(
        "^/", "https://www.gov.uk/", regex=True
    )
    atmt_df["file_extension"] = (
        atmt_df["public_url"]
        .str.split(".")
        .apply(lambda x: x[-1].lower() if is_extension(x[-1]) else "html")
    )
    print(f"identify_child_content: exploded attachments ({len(atmt_df)} rows)")

    linked_content = (
        df.explode("linked_content_raw")
        .dropna(subset="linked_content_raw")
        .drop_duplicates(subset=["public_url", "linked_content_raw"])
        .drop(columns=["attachments", "attachment_titles"])
    )

    linked_content = linked_content.rename(
        columns={"content_id": "parent_content_id", "public_url": "parent_public_url"}
    )

    linked_content["file_extension"] = "html"

    is_url = linked_content["linked_content_raw"].str.startswith("/")

    urls_df = linked_content[is_url]
    cids_df = linked_content[~is_url]
    print(
        f"identify_child_content: exploded linked content ({len(linked_content)} rows)"
    )

    urls_df["public_url"] = urls_df["linked_content_raw"].str.replace(
        "^/", "https://www.gov.uk/", regex=True
    )
    urls_df = urls_df.drop("linked_content_raw", axis=1)

    cids_df = cids_df.rename(columns={"linked_content_raw": "content_id"})
    cids_df["content_id"] = cids_df["content_id"]

    joining_df = df.drop(
        columns=["linked_content_raw", "attachments", "attachment_titles"]
    )

    joining_df = (
        joining_df.sort_values("public_updated_at", ascending=False)
        .drop_duplicates(subset=["public_url"], keep="first")
        .drop(columns="public_updated_at")
    )

    print("identify_child_content: joining child content to parent data")
    cids_child = cids_df.merge(
        joining_df,
        how="left",
        on="content_id",
        validate="m:1",
        suffixes=["_parent", None],
    )
    urls_child = urls_df.merge(
        joining_df,
        how="left",
        on="public_url",
        validate="m:1",
        suffixes=["_parent", None],
    )
    atmt_child = atmt_df.merge(
        joining_df,
        how="left",
        on="public_url",
        validate="m:1",
        suffixes=["_parent", None],
    )

    child_content = (
        pd.concat([urls_child, cids_child, atmt_child])
        .drop_duplicates(subset=["public_url", "parent_public_url"])
        .dropna(subset="public_url")
        .drop(columns="public_updated_at")
    )
    # if attachment_titles exists, this should have priority over the parent title
    child_content["title"] = child_content["title"].fillna(
        child_content["attachment_titles"]
    )
    child_content = child_content.drop(columns="attachment_titles")
    # fill missing values with parent cols
    parent_cols = child_content.columns[child_content.columns.str.endswith("_parent")]

    # category is often an empty list.
    # remove these so they can be replaced with parent categories
    child_content["categories"][
        child_content["categories"]
        .apply(lambda x: len(x) if isinstance(x, list) else 0)
        .eq(0)
    ] = np.nan

    print("identify_child_content: filling missing values from parent columns")
    for parent_col in parent_cols:
        col = parent_col.replace("_parent", "")
        child_content[col] = child_content[col].fillna(child_content[parent_col])

    child_content = child_content.drop(columns=parent_cols)

    # group by content_id and merge parents
    print(f"identify_child_content: done ({len(child_content)} rows)")
    return child_content


def attachments_data_pipeline(write=True):
    print("attachments_data_pipeline: starting")
    query = "select CAST(content_id AS text), public_url, public_updated_at, title, publishing_orgs, primary_publishing_org, document_type,categories, publishing_app, attachments, attachment_titles, withdrawn, linked_content_raw from example_catalogue_schema.example_content_table_notaxons"

    print("attachments_data_pipeline: querying gov_uk_content")
    gov_uk_content = db.query(query)

    gov_uk_content["withdrawn"] = gov_uk_content["withdrawn"].fillna(False)

    print(
        f"attachments_data_pipeline: identifying child content ({len(gov_uk_content)} rows)"
    )
    child_content = identify_child_content(gov_uk_content)

    # do not include certain types of content
    drop_types = [
        "hmrc_manual_section",
        "hmrc_manual",
        "manual_section",
        "manual",
        "promotional",
        "map",
    ]

    child_content = child_content[~child_content["document_type"].isin(drop_types)]

    child_content["primary_publishing_org"] = child_content[
        "primary_publishing_org"
    ].str.replace(r"(^\[')|('\]$)", "", regex=True)
    child_content["primary_publishing_org"] = child_content[
        "primary_publishing_org"
    ].str.replace(r'(^\[")|("\]$)', "", regex=True)

    # document type should be "html_publication" if html, else N/A
    child_content["document_type"] = "N/A"
    child_content["document_type"][child_content["file_extension"] == "html"] = (
        "html_publication"
    )

    child_content["is_attachment"] = True
    if write:
        print("attachments_data_pipeline: writing to s3")
        write_to_s3(
            child_content,
            "example_attachments_table",
            convert_cols=["publishing_orgs", "categories"],
        )

    print(f"attachments_data_pipeline: done ({len(child_content)} rows)")
    return child_content


################################################
# MASTER DATASET
################################################


def get_total_headings(df):
    """
    used to count the number of headings in html content pages.
    This uses regex to count the number of heading tags in the html column
    """

    def count_matches(string, pattern):
        if isinstance(string, str):
            return len(re.findall(pattern, string))
        else:
            return None

    print(f"get_total_headings: starting for {len(df)} rows")
    # heading count
    h1_count = df["html"].apply(lambda x: count_matches(x, "<h1 .*</h1>"))
    h2_count = df["html"].apply(lambda x: count_matches(x, "<h2 .*</h2>"))
    h3_count = df["html"].apply(lambda x: count_matches(x, "<h3 .*</h3>"))
    h4_count = df["html"].apply(lambda x: count_matches(x, "<h4 .*</h4>"))
    h5_count = df["html"].apply(lambda x: count_matches(x, "<h5 .*</h5>"))

    total_headings = h1_count + h2_count + h3_count + h4_count + h5_count
    print("get_total_headings: done")
    return total_headings


def get_pdf_text_lookup():
    """
    This function reads the pdf text dataframe and formats it in order to join it to the content_df
    We could consider saving this as a sql table so we do not need to repeat this conversion everytime we update the content table

    """
    print("get_pdf_text_lookup: starting")
    with s3.read(
        path="path/to/crawl_data/pdf/pdf_full_text_dataframe.csv",
        team="example_team",
    ) as f:
        pdf_text_df = pd.read_csv(f)

    pdf_text_df = pdf_text_df.set_index("url").dropna()
    print(f"get_pdf_text_lookup: read pdf text data ({len(pdf_text_df)} rows)")

    query = "select distinct(public_url) from example_shared_schema.example_attachments_table where file_extension = 'pdf'"
    pdf_attachment_data = db.query(query)
    print(
        f"get_pdf_text_lookup: queried pdf attachment data ({len(pdf_attachment_data)} rows)"
    )

    # pdf url is badly formatted. Apply the same formatting to public url so we can match it
    pdf_attachment_data["matching_url"] = pdf_attachment_data["public_url"].copy()
    pdf_attachment_data.loc[:, "matching_url"] = pdf_attachment_data[
        "matching_url"
    ].str.replace(r"://", "_")
    pdf_attachment_data.loc[:, "matching_url"] = pdf_attachment_data[
        "matching_url"
    ].str.replace(r"/", "_")
    pdf_attachment_data.loc[:, "matching_url"] = (
        "pdf_texts/" + pdf_attachment_data["matching_url"] + ".txt"
    )

    pdf_text_lookup = pdf_attachment_data.merge(
        pdf_text_df,
        left_on="matching_url",
        right_index=True,
        validate="1:1",
        how="inner",
    )
    print(f"get_pdf_text_lookup: done ({len(pdf_text_lookup)} rows)")
    return pdf_text_lookup


def fill_na_from_parent(
    df, column, id_column="public_url", parent_id_column="parent_public_url"
):
    """
    Certain column values we want to inherit missing values from the parent url if applicable.
    this is used on categories and is_historic
    """
    lookup = df.loc[:, [id_column, column]].dropna().drop_duplicates(id_column)
    data = df[[parent_id_column, column]].merge(
        lookup,
        how="left",
        left_on=parent_id_column,
        right_on=id_column,
        suffixes=(None, "_parent"),
        validate="m:1",
    )
    parent_column = f"{column}_parent"
    data.loc[:, column] = data[column].fillna(data[parent_column])

    return data[column]


def create_full_data(
    content_table="example_catalogue_schema.example_content_table_notaxons",
    attachments_table="example_shared_schema.example_attachments_table",
    ga_table="example_shared_schema.example_ga_table",
    sf_table="example_shared_schema.example_crawl_table",
    rules_config="rules.yaml",
    max_text_length=10000,
):
    """
    This used to be the load_data function, however since we switched to using a master dataset
    instead of doing the joins, this is now used only to combine the datasets.

    steps:
        Performs two queries to handle attachment and non-attachment content differently.
        Joins the content to the google analytics and screaming frog data sets.
        Does some cleaning
        Derives some additional columns
        Uses tf-idf to derive the html equivalent for pdf pages
        Uses rules.yaml to make recommendations

    this function returns a dataframe so you can run it for testing without needing to save it to s3 or catalogue
    """
    print("create_full_data: starting")
    # this query is for attachments that do not have a content_id, and therefore must inherit some
    # attributes from their parent

    attachment_query = f"""
    SELECT
      attachments.*,
      google_analytics.*,
      screaming_frog.*
    FROM
      {attachments_table} AS attachments
    LEFT JOIN
      {ga_table} AS google_analytics
        ON 
          attachments.public_url = google_analytics.public_url
    LEFT JOIN
      {sf_table} AS screaming_frog
        ON 
          attachments.public_url = screaming_frog.public_url
    WHERE
      attachments.content_id IS NULL
      
    """
    # this query is for main content
    # must be a separate query, as we only want the parent info

    content_query = f"""
    SELECT
      gov_uk_content.*,
      attachments.parent_content_id,
      attachments.parent_public_url,
      attachments.is_attachment,
      google_analytics.*,
      screaming_frog.*
      
    FROM
      {content_table} AS gov_uk_content
    LEFT JOIN
      {ga_table} AS google_analytics
        ON 
          gov_uk_content.public_url = google_analytics.public_url
    LEFT JOIN
      {sf_table} AS screaming_frog
        ON 
          gov_uk_content.public_url = screaming_frog.public_url
    LEFT JOIN
      {attachments_table} AS attachments
        ON 
          gov_uk_content.public_url = attachments.public_url
    """

    attachment_data = db.query(attachment_query)
    print(f"create_full_data: queried attachment data ({len(attachment_data)} rows)")
    content_data = db.query(content_query)
    print(f"create_full_data: queried content data ({len(content_data)} rows)")

    list_cols = ["publishing_orgs", "categories"]

    for col in list_cols:
        attachment_data[col] = attachment_data[col].apply(eval)

    # remove the multiple public_urls from the join
    attachment_data = attachment_data.loc[:, ~attachment_data.columns.duplicated()]
    content_data = content_data.loc[:, ~content_data.columns.duplicated()]

    content_data["file_extension"] = "html"
    content_data["primary_publishing_org"] = content_data[
        "primary_publishing_org"
    ].str.replace(r"(^\[')|('\]$)", "", regex=True)
    content_data["primary_publishing_org"] = content_data[
        "primary_publishing_org"
    ].str.replace(r'(^\[")|("\]$)', "", regex=True)
    all_data = pd.concat([content_data, attachment_data], ignore_index=True)
    print(
        f"create_full_data: concatenated content and attachment data ({len(all_data)} rows)"
    )

    # use sf title if available
    all_data["title"] = all_data["title"].fillna(all_data["title_1"])

    # convert content_id from uuid to string where appropriate
    all_data["content_id"] = all_data["content_id"].astype(str)

    fill_na_from_parent_columns = ["is_historic", "categories"]
    # replace empty lists with na in categories so we can use fillna
    all_data.loc[
        all_data["categories"]
        .apply(lambda x: len(x) if isinstance(x, list) else 0)
        .eq(0),
        "categories",
    ] = np.nan

    for col in fill_na_from_parent_columns:
        all_data[col] = fill_na_from_parent(all_data, col)
    print("create_full_data: filled na from parent columns")

    # put the remaining na categories back into empty list form
    all_data.loc[:, "categories"] = all_data["categories"].apply(
        lambda x: x if isinstance(x, list) else []
    )

    # fill na with False on boolean columns
    bool_columns = [
        "is_attachment",
        "screaming_frog_available",
        "is_broken",
        "is_redirecting",
        "is_historic",
        "withdrawn",
    ]
    for col in bool_columns:
        all_data[col] = all_data[col].fillna(False)

    # label all parents
    no_of_attachments_data = (
        all_data["parent_public_url"]
        .value_counts()
        .reset_index()
        .rename(
            columns={"parent_public_url": "public_url", "count": "no_of_attachments"}
        )
    )

    all_data = all_data.merge(no_of_attachments_data, on="public_url", how="left")
    all_data["no_of_attachments"] = all_data["no_of_attachments"].fillna(0)
    all_data["is_parent"] = all_data["no_of_attachments"].ge(1)

    # set id
    grouping_id = all_data.apply(
        lambda row: row.parent_content_id
        if (row.is_attachment and not row.is_parent)
        else row.content_id,
        axis=1,
    )
    all_data["grouping_id"] = grouping_id
    all_data = all_data.sort_values(
        by=["grouping_id", "is_parent"], ascending=[True, False]
    )
    print("create_full_data: set grouping_id and is_parent")

    date_columns = [
        "public_updated_at",
        "date_published",
        "pdf_modified",
        "pdf_created",
    ]
    for col in date_columns:
        all_data[col] = pd.to_datetime(all_data[col])

    print("create_full_data: fetching pdf text lookup")
    pdf_text_lookup = get_pdf_text_lookup()
    all_data = all_data.merge(
        pdf_text_lookup, on="public_url", how="left", validate="m:1"
    )

    n_text_rows = (~all_data["pdf_clean"].isna()).sum()

    print(f"pdf text rows matched: {n_text_rows}")
    all_data["text"] = all_data["text"].fillna(all_data["pdf_clean"])
    all_data = all_data.drop(columns="pdf_clean")
    print("create_full_data: merged pdf text lookup")

    # use actual word count if it exists.
    word_count = all_data["text"].str.split().str.len()
    word_count = word_count.fillna(all_data["word_count"])
    all_data["word_count"] = word_count

    text_columns = [
        "title",
        "abstract",
        "text",
        "primary_publishing_org",
        "format",
        "readability",
        "document_type",
    ]

    all_data[text_columns] = all_data[text_columns].fillna("")

    # this removes all line breaks and replaces with ' '. Could affect LLM performance.
    all_data["text"] = all_data["text"].apply(
        lambda x: " ".join(str(x).split()[:max_text_length])
    )

    drop_cols = [
        "format",
        "attachments",
        "attachment_titles",
        "attachment_types",
        "mimetypes",
        "updated_at",
        "linked_content_raw",
        "linked_content",
        "title_1",
    ]
    all_data = all_data.drop(drop_cols, axis=1)

    print("create_full_data: computing heading counts")
    total_headings = get_total_headings(all_data)
    # avoid div by zero
    word_to_heading_ratio = all_data["word_count"] / total_headings.apply(
        lambda x: x if x > 0 else 1
    )

    all_data["total_headings"] = total_headings
    all_data["word_to_heading_ratio"] = word_to_heading_ratio
    all_data.loc[all_data["total_headings"].isna(), "word_to_heading_ratio"] = None

    all_data["expected_reading_time_mins"] = round(all_data["word_count"] / 250, 0)

    all_data["file_download_navigated"] = (
        all_data["file_downloads"] + all_data["navigation"]
    )

    all_data = all_data.drop_duplicates(subset=["parent_public_url", "public_url"])
    print(f"create_full_data: finding accessible pdf versions ({len(all_data)} rows)")
    pdf_lookup = dc.find_accessible_version_of_pdf(all_data, threshold=0.8)

    all_data = all_data.merge(
        pdf_lookup, how="left", on=["parent_public_url", "public_url"], validate="1:1"
    )
    all_data["accessible_url"] = all_data.apply(
        lambda row: row["public_url"]
        if row["file_extension"] == "html"
        else row["accessible_url"],
        axis=1,
    )
    all_data["is_pdf_with_accessible_version"] = (
        (all_data["file_extension"] == "pdf")
        & all_data["screaming_frog_available"]
        & (all_data["accessible_url_confidence_score"] >= 0.9)
    )

    print("create_full_data: running rule engine")
    engine = MultiCategoryRuleEngine(all_data)

    all_data = engine.pipeline("../audit_tool_streamlit/rules.yaml")

    # redirecting pages are not useful to show in the final dataset
    all_data = all_data[~all_data["is_redirecting"]]

    print(f"create_full_data: done ({len(all_data)} rows)")
    return all_data


if __name__ == "__main__":
    """
    
    """
    update_attachments = False
    update_ga = False
    update_sf = False
    update_content = False
    save_new_content = False

    if update_attachments:
        attachments_data_pipeline()
    if update_ga:
        ga_data_pipeline()
    if update_sf:
        sf_data_pipeline()
    if update_content:
        data = create_full_data()
        if save_new_content:
            write_to_catalogue(
                data,
                "example_catalogue_schema",
                "example_content_table",
                convert_cols=[
                    "publishing_orgs",
                    "categories",
                    "negative_user_engagement_reasons",
                    "accessibility_reasons",
                    "freshness_reasons",
                    "functionality_reasons",
                ],
            )
