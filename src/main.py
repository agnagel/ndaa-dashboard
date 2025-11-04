import streamlit as st
from cdg import *
from configparser import ConfigParser
import json

API_URL = "https://api.congress.gov/"
API_VERSION = "v3"
RESPONSE_FORMAT = "json" # can't get xml to work

config = ConfigParser()
config.read("../secrets.ini")
API_KEY = config.get("cdg_api", "api_auth_key")
API_STRING = f"api_key=[{API_KEY}]"

CONGRESS = "119"
BILL_TYPE = "s"
BILL_NUM = "2296"

if __name__ == "__main__":
    cdg = CDG(api_url=API_URL,
              api_key=API_KEY,
              api_version=API_VERSION,
              response_format=RESPONSE_FORMAT)
    data = cdg.get_bill_text(CONGRESS, BILL_TYPE, BILL_NUM)
    print(json.dumps(data, indent=4))