import pytest
import requests
import httpretty
import json
from context import optimizely


@httpretty.activate
def test_get_requests_sync_single():
    # register url
    content = {'key' : 'value'}
    url = "http://test_url.com/"
    httpretty.register_uri(httpretty.GET, url, body=json.dumps(content))

    # send request
    response = optimizely._get_requests_sync([url], "dummy_token")
    for key in response:
        assert key == url
        assert response[key] == content


@httpretty.activate
def test_get_requests_sync_multiple():
    # register urls
    content = {'key' : 'value'}
    urls = ["http://test_url_{}.com/".format(i) for i in range(3)]
    for url in urls:
        httpretty.register_uri(httpretty.GET, url, body=json.dumps(content))

    # send requests
    response = optimizely._get_requests_sync(urls, "dummy_token")
    for i, key in enumerate(response):
        assert key == urls[i]
        assert response[key] == content
