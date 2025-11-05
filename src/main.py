from cdg import *
from configparser import ConfigParser
import json
import os
import pandas
import streamlit

config = ConfigParser()
config.read("../secrets.ini")
API_KEY = config.get("cdg_api", "api_auth_key")
API_STRING = f"api_key=[{API_KEY}]"

CONGRESS = "119"
BILL_TYPE = "s"
BILL_NUM = "2296"

# Temporary files to avoid unnecessary API calls
AMENDMENT_LIST_FILE = "amendment_list.txt"

if __name__ == "__main__":
    cdg = CDG(api_key=API_KEY)

    # Check to see how many amendments exist for this bill
    bill_details = cdg.get_bill_details(CONGRESS, BILL_TYPE, BILL_NUM)
    amendment_count = bill_details['amendments']['count']

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
    if amendment_count != old_amendment_count:
        # TODO: put a warning on the web app saying the list needs to be updated
        amendments = cdg.get_amendments(CONGRESS, BILL_TYPE, BILL_NUM)

        # Get amendment text for each amendment
        # TODO: fetch only the diff instead of the entire list - create a smaller, searchable data structure
        retries = 3
        for i, amendment in enumerate(amendments):
            print(f"Processing amendment {i+1}...")
            amendment_type = amendment['type'].lower()
            amendment_num = amendment['number']
            for _ in range(retries):
                try:
                    # TODO: How to handle amendments of amendments?
                    details = cdg.get_amendment_details(CONGRESS, amendment_type, amendment_num)
                    amendments[i].update(details)
                    # TODO: Add cosponsors which are not automatically included in details? >:(
                    # TODO: Turn this HTML into regular text (in CDG class)
                    text = cdg.get_amendment_text(CONGRESS, amendment_type, amendment_num)
                    amendments[i].update({'text': text})
                    break
                except Exception as e:
                    print(f"ERROR on {i}: {e}")

        # Dump the amendments with their text into the cache file
        with open(AMENDMENT_LIST_FILE, 'w') as f:
            json.dump(amendments, f, indent=4)




