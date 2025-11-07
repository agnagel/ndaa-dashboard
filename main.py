from cdg import *
from configparser import ConfigParser
import json
import os
import pandas as pd
import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode


config = ConfigParser()
config.read("../secrets.ini")
# API_KEY = config.get("cdg_api", "api_auth_key")
# API_STRING = f"api_key=[{API_KEY}]"

CONGRESS = "119"
BILL_TYPE = "s"
BILL_NUM = "2296"

# Temporary files to avoid unnecessary API calls
AMENDMENT_LIST_FILE = "amendment_list.txt"
AMENDMENT_LIST_SHORT = "amendment_list_short.txt"

if __name__ == "__main__":
    # cdg = CDG(api_key=API_KEY)

    # Check to see how many amendments exist for this bill
    # bill_details = cdg.get_bill_details(CONGRESS, BILL_TYPE, BILL_NUM)
    # amendment_count = bill_details['amendments']['count']

    # Check if we have a cached list already
    old_amendment_count = 0
    if os.path.exists(AMENDMENT_LIST_FILE):
        try:
            with open(AMENDMENT_LIST_FILE, 'r') as f:
                amendments = json.load(f)
                old_amendment_count = len(amendments)
        except Exception as e:
            print(f"ERROR opening amendments: {e}")

    # There must be new amendments (or ones deleted?)
    # if amendment_count != old_amendment_count:
    #     print("WARNING: There are new or removed amendments on Congress.gov.")

    #     # TODO: put a warning on the web app saying the list needs to be updated
    #     amendments = cdg.get_amendments(CONGRESS, BILL_TYPE, BILL_NUM)
    #
    #     # Get amendment text for each amendment
    #     # TODO: fetch only the diff instead of the entire list - create a smaller, searchable data structure
    #     retries = 3
    #     for i, amendment in enumerate(amendments):
    #         print(f"Processing amendment {i+1}...")
    #         amendment_type = amendment['type'].lower()
    #         amendment_num = amendment['number']
    #         for _ in range(retries):
    #             try:
    #                 # TODO: How to best handle amendments of amendments?
    #                 details = cdg.get_amendment_details(CONGRESS, amendment_type, amendment_num)
    #                 amendments[i].update(details)
    #                 cosponsors = cdg.get_amendment_cosponsors(CONGRESS, amendment_type, amendment_num)
    #                 amendments[i].update({'cosponsors': cosponsors})
    #                 text = cdg.get_amendment_text(CONGRESS, amendment_type, amendment_num)
    #                 amendments[i].update({'text': text})
    #                 break
    #             except Exception as e:
    #                 print(f"ERROR on {i}: {e}")
    #
    #     # Dump the amendments with their text into the cache file
    #     with open(AMENDMENT_LIST_FILE, 'w') as f:
    #         json.dump(amendments, f, indent=4)

    # Create a new data structure with just the relevant data
    # amendments_short = []
    # for amendment in amendments:
    #     amendment_short = {'Number': amendment['number'],
    #                        'Amended Amdt.': amendment.get('amendedAmendment', {}).get('number', ''),
    #                        'Submission Date': amendment['submittedDate'],
    #                        'Sponsor': amendment['sponsors'][0]['lastName'] + ', ' + amendment['sponsors'][0][
    #                            'firstName'],
    #                        'Party': amendment['sponsors'][0]['party'],
    #                        'State': amendment['sponsors'][0]['state'],
    #                        'Cosponsors': ', '.join([x.get('lastName')
    #                                                 for x in amendment['cosponsors']]),
    #                        'Text': amendment['text']}
    #     amendments_short.append(amendment_short)
    # with open(AMENDMENT_LIST_SHORT, 'w') as f:
    #     json.dump(amendments_short, f, indent=4)

    # Read in the relevant data
    with open(AMENDMENT_LIST_SHORT, 'r') as f:
        data = json.load(f)

    # Create a pandas dataframe with row number
    df = pd.DataFrame(data)
    df.insert(0, '#', range(1, len(df) + 1))

    # Obnoxious hacky code to get HTML in cells to render in Streamlit
    cell_renderer = JsCode("""
        class UrlCellRenderer {
              init(params) {
                this.eGui = document.createElement('a');
                this.eGui.innerText = params.value;
                this.eGui.setAttribute('href', "https://www.congress.gov/amendment/119th-congress/senate-amendment/" + params.value);
                this.eGui.setAttribute('target', "_blank");
              }
              getGui() {
                return this.eGui;
              }
            }                        
        """)

    # Set up page
    st.set_page_config(layout="wide")
    st.title("Senate FY 2026 NDAA Dashboard")

    # Configure all columns
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_default_column(filter=True, sortable=True, autoHeight=True)
    gb.configure_column("#", width=60, pinned='left')
    gb.configure_column("Number",
                        cellRenderer=cell_renderer,
                        width=100,
    )
    gb.configure_column("Amended Amdt.",
                        cellRenderer=cell_renderer,
                        width=100)
    gb.configure_column("Submission Date",
                        width=100,
                        type=["dateColumnFilter", "customDateTimeFormat"],
                        custom_format_string='MM/dd/yyyy'
    )
    gb.configure_column("Sponsor", width=200)
    gb.configure_column("State", width=60)
    gb.configure_column("Party", width=60)
    gb.configure_column("Cosponsors", width=200, wrapText=True)
    gb.configure_column("Text", width=400)

    # Build page
    grid_options = gb.build()
    AgGrid(df,
           gridOptions=grid_options,
           height=600,
           allow_unsafe_jscode=True,
           enable_enterprise_modules=False,
           fit_columns_on_grid_load=True)
