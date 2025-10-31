import streamlit as st
import json
import requests
from urllib.parse import urljoin

API_URL = "https://api.congress.gov/"
API_VERSION = "v3"
API_KEY = "123"
API_STRING = f"api_key=[{API_KEY}]"
RESPONSE_FORMAT = "json" # can't get xml to work

CONGRESS = "119"
BILL_TYPE = "s"
BILL_NUM = "2296"

class _MethodWrapper:
    """ Wrap request method to facilitate queries.  Supports requests signature. """

    def __init__(self, parent, http_method):
        self._parent = parent
        self._method = getattr(parent._session, http_method)

    def __call__(self, endpoint, *args, **kwargs):  # full signature passed here
        response = self._method(
            urljoin(self._parent.base_url, endpoint), *args, **kwargs
        )
        # unpack
        if response.headers.get("content-type", "").startswith("application/json"):
            return response.json(), response.status_code
        else:
            return response.content, response.status_code

class CDGClient:
    """ A sample client to interface with Congress Dot Gov """

    def __init__(
        self,
        api_url,
        api_key,
        api_version,
        response_format,
    ):
        self.base_url = urljoin(api_url, api_version) + "/"
        self._session = requests.Session()

        # do not use url parameters, even if offered, use headers
        self._session.params = {"format": response_format}
        self._session.headers.update({"x-api-key": api_key})
        self._session.hooks = {
            "response": lambda r, *args, **kwargs: r.raise_for_status()
        }

    def __getattr__(self, method_name):
        """Find the session method dynamically and cache for later."""
        method = _MethodWrapper(self, method_name)
        self.__dict__[method_name] = method
        return method

class CDG:
    def __init__(
        self,
        api_url,
        api_key,
        api_version,
        response_format
    ):
       self.client = CDGClient(api_url,
                               api_key,
                               api_version,
                               response_format)

    def get_bill_text(self, congress, bill_type, bill_num):
        """ Returns a URL to the HTML or XML of the bill text """
        endpoint = f"bill/{congress}/{bill_type}/{bill_num}/text"
        data, status_code = self.client.get(endpoint)
        return data

    def get_amendment(client):
        return

    def get_amendments(client):
        return

if __name__ == "__main__":
    cdg = CDG(api_url=API_URL,
              api_key=API_KEY,
              api_version=API_VERSION,
              response_format=RESPONSE_FORMAT)
    data = cdg.get_bill_text(CONGRESS, BILL_TYPE, BILL_NUM)
    print(json.dumps(data, indent=4))