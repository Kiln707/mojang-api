#!/usr/bin/env python3

from attrdict import AttrDict

from enum import Enum


class BaseURL:
    def __init__(self, base_url=''):
        self._base_url = base_url

    def __get__(self, instance, owner):
        return self._base_url


class Endpoint(Enum):
    BASE_URL = BaseURL()

    def __init__(self, endpoint_uri):
        self._endpoint_uri = endpoint_uri
        self._url = self.BASE_URL + self.endpoint_uri

    @property
    def endpoint_uri(self):
        return self._endpoint_uri

    @property
    def url(self):
        return self._url

    def __str__(self):
        return self.url


class APIResponseMixin:
    def __init__(self, response, *args, **kwargs):
        self._response = response
        super().__init__(*args, **kwargs)

    @property
    def response(self):
        return self._response


class APIResponseDict(APIResponseMixin, AttrDict):
    def __init__(self, cls, response):
        data = response.json()
        super(cls, self).__init__(response, data)


class APIResponseList(APIResponseMixin, list):
    def __init__(self, cls, response):
        data = response.json()
        super(cls, self).__init__(response, (AttrDict(json) for json in data))


class APIResponse:
    @staticmethod
    def from_response(response):
        try:
            data = response.json()
        except ValueError:
            raise ValueError('response must contain JSON data')

        if isinstance(data, dict):
            base_class = APIResponseDict
        elif isinstance(data, list):
            base_class = APIResponseList
        else:
            raise TypeError(
                'response\'s JSON data must be of type \'dict\' or \'list\'')

        bases = base_class.__bases__
        dct = dict(base_class.__dict__)
        cls = globals()['APIResponse']
        dct['from_response'] = cls.__dict__['from_response']
        APIResponse = type('APIResponse', bases, dct)
        instance = APIResponse(APIResponse, response)
        APIResponse = cls
        return instance
