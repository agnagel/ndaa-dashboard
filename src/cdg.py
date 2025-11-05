import bs4
import requests
from urllib.parse import urljoin

API_URL = "https://api.congress.gov/"
API_VERSION = "v3"

class CDG:
    """ A sample client to interface with Congress Dot Gov """

    def __init__(
        self,
        api_key,
        api_url=API_URL,
        api_version=API_VERSION
    ):
        self.base_url = urljoin(api_url, api_version) + '/'
        self._session = requests.Session()

        # do not use url parameters, even if offered, use headers
        self._session.headers.update({"x-api-key": api_key})
        self._session.hooks = {
            "response": lambda r, *args, **kwargs: r.raise_for_status()
        }

    def _get(self, endpoint, response_format='json', limit=100, offset=0):
        self._session.params = {"format": response_format,
                                "limit": limit,
                                "offset": offset}
        data = self._session.get(urljoin(self.base_url, endpoint))
        return data.json()

    def get_bill_details(self, congress, bill_type, bill_num):
        endpoint = f"bill/{congress}/{bill_type}/{bill_num}"
        data = self._get(endpoint)
        return data['bill']

    def get_amendment_details(self, congress, amendment_type, amendment_num):
        endpoint = f"amendment/{congress}/{amendment_type}/{amendment_num}"
        data = self._get(endpoint)
        return data['amendment']

    def get_amendments(self, congress, bill_type, bill_num):
        """ Returns a URL to the HTML or XML of the bill text """
        offset = 0
        total_count = 1
        limit = 100
        data = []
        while offset < total_count:
            data_page = self._get_amendments(congress, bill_type, bill_num, offset=offset, limit=limit)
            data.extend(data_page['amendments'])
            total_count = data_page['pagination']['count']
            offset += limit
        return data

    def _get_amendments(self, congress, bill_type, bill_num, **kwargs):
        endpoint = f"bill/{congress}/{bill_type}/{bill_num}/amendments"
        data = self._get(endpoint, kwargs)
        return data

    def get_amendment_text(self, congress, amendment_type, amendment_num):
        url = self._get_amendment_text_url(congress, amendment_type, amendment_num)
        print(f'Getting text from {url}...')
        if url:
            response = requests.get(url, timeout=10)
            return response.content.decode('utf-8')
        return ''

    def _get_amendment_text_url(self, congress, amendment_type, amendment_num):
        endpoint = f"amendment/{congress}/{amendment_type}/{amendment_num}/text"
        data = self._get(endpoint)
        formats = data['textVersions'][0]['formats']
        for format in formats:
            if format['type'].upper() == 'HTML':
                return format['url']
        return ''

    def get_amendment_amendments(self, congress, amendment_type, amendment_num):
        endpoint = f"amendment/{congress}/{amendment_type}/{amendment_num}/amendments"
        data = self._get(endpoint)
        return data
