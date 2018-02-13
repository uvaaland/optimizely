import asyncio
import pandas as pd
from requests import Session
from json import JSONDecodeError
from aiohttp import ClientSession, ContentTypeError
from timeit import default_timer


HEADER = "{0:^80}"
STATUS_BAR = "{0:^10}{1:^60}{2:^10}"
HORIZONTAL_RULE = "-"*80


async def FetchAll(urls, token):
    """Launch requests for all web pages."""

    tasks = []
    nurls = len(urls)
    i = [0]
    async with ClientSession() as session:
        for url in urls:
            task = asyncio.ensure_future(Fetch(url, token, session, i, nurls))
            tasks.append(task) # create list of tasks
        responses = await asyncio.gather(*tasks) # gather task responses

        return responses


async def Fetch(url, token, session, i, nurls, verbose=True):
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


def _GetRequestsAsync(urls, token, verbose):
    """Fetch list of web pages asynchronously."""

    loop = asyncio.get_event_loop()
    future = asyncio.ensure_future(FetchAll(urls, token))
    responses = loop.run_until_complete(future)

    return { k : v for d in responses for (k, v) in d.items() }


def _GetRequestsSync(urls, token, verbose):
    """Fetch list of web pages sequentially."""

    responses = {}
    session = Session()
    header = {'Token': token}
    for i, url in enumerate(urls):
        r = session.get(url, headers=header)
        try:
            content = r.json()
        except JSONDecodeError:
            content = []
        status = r.status_code

        responses[url] = (status, content)

        if verbose:
            count = "[{0:03}/{1:03}]:".format(i+1, len(urls))
            print(STATUS_BAR.format(count, ".../" + r.url[31:], str(status == 200)))

    return responses


def GetRequests(urls, token, async=False, verbose=True):
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
        responses = _GetRequestsAsync(urls, token, verbose)
    else:
        responses = _GetRequestsSync(urls, token, verbose)
    elapsed_time = default_timer() - start_time

    if verbose:
        print(HORIZONTAL_RULE)
        print("Elapsed time: {0:63.2f}s".format(elapsed_time))
        print(HORIZONTAL_RULE)

    return responses 


def RequestsToDataframe(reqs, param, verbose=True):
    try:
        dfs = [pd.DataFrame(r) for r in reqs]
    except ValueError:
        dfs = [pd.DataFrame(r, index=[i]) for i, r in enumerate(reqs)]

    return pd.concat(dfs)


def _GenerateUrls(df, target):
    target_url = {
                    "experiments" : "https://www.optimizelyapis.com/experiment/v1/projects/{}/experiments/",
                    "stats"       : "https://www.optimizelyapis.com/experiment/v1/experiments/{}/stats",
                    "variations"  : "https://www.optimizelyapis.com/experiment/v1/variations/{}"
                 }[target]

    if target == "variations":
        ids = [item for sublist in df["variation_ids"] for item in sublist]
    else:
        ids = df["id"]

    return [target_url.format(i) for i in ids]


def GenerateUrlFiles(df, targets, verbose=True):
    
    for target in targets:
        urls = _GenerateUrls(df, target)

        with open("urls/{}.url".format(target), 'w') as f:
            for u in urls:
                f.write(u + '\n')

        if verbose:
            print("Saved '{0}' urls to 'urls/{0}.url'.".format(target))


def Main(param, verbose=True):

    if verbose:
        print(HORIZONTAL_RULE)
        print(HEADER.format(param.upper()))
        print(HORIZONTAL_RULE)

    with open("token/token.txt", 'r') as f:
        token = f.read().rstrip('\n')

    with open("urls/{}.url".format(param), 'r') as f:
        urls = f.read().splitlines()

    responses = GetRequests(urls, token, verbose=verbose)

    urls_fail = [url for url in urls if responses[url][0] != 200]
    with open("urls/failures.url", 'w' if param == 'projects' else 'a') as f:
        for url in urls_fail:
            f.write(url + '\n')
            responses.pop(url, None)

    content = [v[1] for v in list(responses.values())]


    dataframe = RequestsToDataframe(content, param, verbose=verbose) 

    # Write to file
    dataframe.to_csv("output/{}.csv".format(param), index=False)
    
    if verbose:
        print("Saved '{0}' frame to 'output/{0}.csv'.".format(param))


    if param == "projects":
        GenerateUrlFiles(dataframe, ["experiments"])
    elif param == "experiments":
        GenerateUrlFiles(dataframe, ["stats", "variations"])

    if verbose:
        print(HORIZONTAL_RULE)


if __name__ == "__main__":
    parameters = ["projects", "experiments", "stats", "variations"]
    for param in parameters:
        Main(param)
