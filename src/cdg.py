import requests
from urllib.parse import urljoin

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
        response_format='json',
        limit=100,
        offset=0
    ):
        self.base_url = urljoin(api_url, api_version) + "/"
        self.limit = limit
        self.response_format = response_format
        self.offset = offset
        self._session = requests.Session()

        # do not use url parameters, even if offered, use headers
        self._session.headers.update({"x-api-key": api_key})
        self._session.hooks = {
            "response": lambda r, *args, **kwargs: r.raise_for_status()
        }
        self.update_params()

    def update_params(self, response_format='', limit=0, offset=None):
        self.response_format = response_format if response_format else self.response_format
        self.limit = limit if limit else self.limit
        self.offset = offset if offset is not None else self.offset
        self._session.params = {"format": self.response_format,
                                "limit": self.limit,
                                "offset": self.offset}

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
    ):
       self.client = CDGClient(api_url,
                               api_key,
                               api_version)

    def get_bill_details(self, congress, bill_type, bill_num):
        endpoint = f"bill/{congress}/{bill_type}/{bill_num}"
        data, status_code = self.client.get(endpoint)
        return data['bill']

    def get_amendment_details(self, congress, amendment_type, amendment_num):
        endpoint = f"amendment/{congress}/{amendment_type}/{amendment_num}"
        data, status_code = self.client.get(endpoint)
        return data['amendment']

    def get_amendments(self, congress, bill_type, bill_num):
        """ Returns a URL to the HTML or XML of the bill text """
        offset = 0
        total_count = 1
        limit = self.client.limit
        data = []
        while offset < total_count:
            self.client.update_params(offset=offset)
            data_page = self._get_amendments(congress, bill_type, bill_num)
            data.extend(data_page['amendments'])
            total_count = data_page['pagination']['count']
            offset += limit
        self.client.update_params(offset=0)
        return data

    def _get_amendments(self, congress, bill_type, bill_num):
        endpoint = f"bill/{congress}/{bill_type}/{bill_num}/amendments"
        data, status_code = self.client.get(endpoint)
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
        data, status_code = self.client.get(endpoint)
        formats = data['textVersions'][0]['formats']
        for format in formats:
            if format['type'].upper() == 'HTML':
                return format['url']
        return ''

    def get_amendment_amendments(self, congress, amendment_type, amendment_num):
        endpoint = f"amendment/{congress}/{amendment_type}/{amendment_num}/amendments"
        data, status_code = self.client.get(endpoint)
        return data
