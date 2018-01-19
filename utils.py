import os
import sys
import requests


def ReadFileToken(token="token/token.txt"):
    with open(token, 'r') as f:
        return f.read().rstrip('\n')


def ReadFileURL(urlfile):
    with open(urlfile, 'r') as f:
        return f.read().splitlines()


def WriteFileURL():
    pass

def WriteFileRequest():
    pass


def RequestURL(urls, token=None):
    reqs = []
    urls_fail = []
    for u in urls:
        r = requests.get(u, headers={'Token': token})
        if r.ok:
            reqs.append(r)
        else:
            urls_fail.append(r.url)
    return reqs, urls_fail


def RequestToDataframe():
    pass
