"""
MIT License

Copyright (c) 2018 Uno Brosten Vaaland

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""


from json import JSONDecodeError
from timeit import default_timer
import asyncio
from aiohttp import ClientSession, ContentTypeError
from requests import Session
import pandas as pd


HEADER = "{0:^80}"
STATUS_BAR = "{0:^10}{1:^60}{2:^10}"
HORIZONTAL_RULE = "-"*80


async def fetch_all(urls, token):
    """Launch requests for all web pages."""

    tasks = []
    nurls = len(urls)
    i = [0]
    async with ClientSession() as session:
        for url in urls:
            task = asyncio.ensure_future(fetch(url, token, session, i, nurls))
            tasks.append(task) # create list of tasks
        responses = await asyncio.gather(*tasks) # gather task responses

        return responses


async def fetch(url, token, session, i, nurls, verbose=True):
    """Fetch a url, using specified ClientSession."""

    header = {'Token': token}
    async with session.get(url, headers=header) as response:
        try:
            content = await response.json()
        except ContentTypeError:
            content = []
        status = response.status

        if verbose:
            i[0] = i[0] + 1
            count = "[{0:03}/{1:03}]:".format(i[0], nurls)
            print(STATUS_BAR.format(count, ".../" + url[31:], str(status == 200)))

        return {url : (status, content)}


def _get_requests_async(urls, token):
    """Fetch list of web pages asynchronously."""

    loop = asyncio.get_event_loop()
    future = asyncio.ensure_future(fetch_all(urls, token))
    responses = loop.run_until_complete(future)

    return {k : v for d in responses for (k, v) in d.items()}


def _get_requests_sync(urls, token, verbose):
    """Fetch list of web pages sequentially."""

    responses = {}
    session = Session()
    header = {'Token': token}
    for i, url in enumerate(urls):
        response = session.get(url, headers=header)
        try:
            content = response.json()
        except JSONDecodeError:
            content = []
        status = response.status_code

        responses[url] = (status, content)

        if verbose:
            count = "[{0:03}/{1:03}]:".format(i+1, len(urls))
            print(STATUS_BAR.format(count, ".../" + url[31:], str(status == 200)))

    return responses


def get_requests(urls, token, async=True, verbose=True):
    """Takes in a list of urls and a token and makes a request for each url in
    the list. Returns a dictionary with two keys, 'success' and 'failure',
    which map to lists containing the request objects for the successful and
    failed requests.
    """

    if verbose:
        print(STATUS_BAR.format("#", "REQUEST (https://www.optimizelyapis.com/...)", "SUCCESS"))
        print(HORIZONTAL_RULE)

    start_time = default_timer()
    if async:
        responses = _get_requests_async(urls, token)
    else:
        responses = _get_requests_sync(urls, token, verbose)
    elapsed_time = default_timer() - start_time

    if verbose:
        print(HORIZONTAL_RULE)
        print("Elapsed time: {0:63.2f}s".format(elapsed_time))
        print(HORIZONTAL_RULE)

    return responses


def content_to_dataframe(content):
    try:
        dfs = [pd.DataFrame(c) for c in content]
    except ValueError:
        dfs = [pd.DataFrame(c, index=[i]) for i, c in enumerate(content)]

    return pd.concat(dfs)


def _generate_urls(dataframe, target):
    target_url = {
        "experiments" : "experiment/v1/projects/{}/experiments/",
        "stats"       : "experiment/v1/experiments/{}/stats",
        "variations"  : "experiment/v1/variations/{}"
        }[target]

    if target == "variations":
        ids = [item for sublist in dataframe["variation_ids"] for item in sublist]
    else:
        ids = dataframe["id"]

    return ["https://www.optimizelyapis.com/" + target_url.format(i) for i in ids]


def generate_url_files(dataframe, targets, verbose=True):
    for target in targets:
        urls = _generate_urls(dataframe, target)

        with open("urls/{}.url".format(target), 'w') as outfile:
            for url in urls:
                outfile.write(url + '\n')

        if verbose:
            print("Saved '{0}' urls to 'urls/{0}.url'.".format(target))


def main(verbose=True):

    with open("token/token.txt", 'r') as infile:
        token = infile.read().rstrip('\n')

    parameters = ["projects", "experiments", "stats", "variations"]
#    parameters = ["projects", "experiments"]
    for par in parameters:

        if verbose:
            print(HORIZONTAL_RULE)
            print(HEADER.format(par.upper()))
            print(HORIZONTAL_RULE)

        with open("urls/{}.url".format(par), 'r') as infile:
            urls = infile.read().splitlines()
    
        responses = get_requests(urls, token)
    
        urls_fail = [url for url in urls if responses[url][0] != 200]
        with open("urls/failures.url", 'w' if par == 'projects' else 'a') as outfile:
            for url in urls_fail:
                outfile.write(url + '\n')
                responses.pop(url, None)
    
        content = [v[1] for v in list(responses.values())]
    
        dataframe = content_to_dataframe(content)
    
        # Write to file
        dataframe.to_csv("output/{}.csv".format(par), index=False)
    
        if verbose:
            print("Saved '{0}' frame to 'output/{0}.csv'.".format(par))
    
        if par == "projects":
            generate_url_files(dataframe, ["experiments"])
        elif par == "experiments":
            generate_url_files(dataframe, ["stats", "variations"])
    
        if verbose:
            print(HORIZONTAL_RULE)


if __name__ == "__main__":
    main()
