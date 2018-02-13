import utils
import requests
import asyncio
import pandas as pd
import io
from aiohttp import ClientSession
from timeit import default_timer


HEADER = "{0:^80}"
STATUS_BAR = "{0:^10}{1:^60}{2:^10}"
HORIZONTAL_RULE = "-"*80


async def FetchAll(urls, token):
    """Launch requests for all web pages."""

    tasks = []
    async with ClientSession() as session:
        for i, url in enumerate(urls):
            task = asyncio.ensure_future(Fetch(i, url, token, session))
            tasks.append(task) # create list of tasks
        responses = await asyncio.gather(*tasks) # gather task responses

        return responses


async def Fetch(i, url, token, session, verbose=True):
    """Fetch a url, using specified ClientSession."""

    header = {'Token': token}
    async with session.get(url, headers=header) as r:
        _ = await r.read()

        if verbose:
            count = "[{0:03}/{1:03}]:".format(i+1, 100)
            print(STATUS_BAR.format(count, ".../" + url[31:], str(r.status == 200)))

        return r


def _GetRequestsAsync(urls, token, verbose):
    """Fetch list of web pages asynchronously."""

    loop = asyncio.get_event_loop()
    future = asyncio.ensure_future(FetchAll(urls, token))
    responses = loop.run_until_complete(future)

    return responses


def _GetRequestsSync(urls, token, verbose):
    """Fetch list of web pages sequentially."""

    responses = {}
    session = requests.Session()
    header = {'Token': token}
    for i, url in enumerate(urls):
        r = session.get(url, headers=header)

        if verbose:
            count = "[{0:03}/{1:03}]:".format(i+1, len(urls))
            print(STATUS_BAR.format(count, ".../" + r.url[31:], str(r.ok)))

        responses[url] = (r.json(), r.status_code)

    return responses

def _GetRequests(urls, token, async=False, verbose=True):
    """Takes in a list of urls and a token and makes a request for each url in
    the list. Returns a dictionary with two keys, 'success' and 'failure',
    which map to lists containing the request objects for the successful and
    failed requests.
    """

    if async:
        responses = _GetRequestsAsync(urls, token, verbose)
    else:
        responses = _GetRequestsSync(urls, token, verbose)

    if verbose:
        print(HORIZONTAL_RULE)

    print(responses[urls[0]])

    reqs = {"success":[], "failure":[]}
    if async:
        for r in responses:
            if r.status == 200:
                reqs["success"].append(r)
            else:
                reqs["failure"].append(r)
    else:
        for r in responses:
            if r.ok:
                reqs["success"].append(r)
            else:
                reqs["failure"].append(r)



    with open("urls/failures.url", 'w') as f:
        for r in reqs["failure"]:
            f.write(r.url + '\n')

    return reqs["success"]


def _RequestsToDataframe(reqs, param, verbose=True):
    try:
        dfs = [pd.DataFrame(r.json()) for r in reqs]
    except ValueError:
        dfs = [pd.DataFrame(r.json(), index=[i]) for i, r in enumerate(reqs)]

    dfs = pd.concat(dfs)
    dfs.to_csv("output/{}.csv".format(param), index=False)
    
    if verbose:
        print("Saved '{0}' frame to 'output/{0}.csv'.".format(param))

    return dfs


def _GenerateUrls(df, target, verbose=True):
    target_url = {
                    "experiments" : "https://www.optimizelyapis.com/experiment/v1/projects/{}/experiments/",
                    "stats"       : "https://www.optimizelyapis.com/experiment/v1/experiments/{}/stats",
                    "variations"  : "https://www.optimizelyapis.com/experiment/v1/variations/{}"
                 }[target]

    if target == "variations":
        ids = [item for sublist in df["variation_ids"] for item in sublist]
    else:
        ids = df["id"]

    urls = [target_url.format(i) for i in ids]
    
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
        print(STATUS_BAR.format("#", "REQUEST (https://www.optimizelyapis.com/...)", "SUCCESS"))
        print(HORIZONTAL_RULE)


    token = utils.ReadFileToken()
    urls = utils.ReadFileURL("urls/{}.url".format(param))[:1]


    reqs = _GetRequests(urls, token, verbose=verbose)
    dataframe = _RequestsToDataframe(reqs, param, verbose=verbose) 

#    if param == "projects":
#        _GenerateUrls(dataframe, "experiments", verbose=verbose)
#    elif param == "experiments":
#        _GenerateUrls(dataframe, "stats", verbose=verbose)
#        _GenerateUrls(dataframe, "variations", verbose=verbose)

    if verbose:
        print(HORIZONTAL_RULE)


if __name__ == "__main__":
    #parameters = ["projects", "experiments", "stats", "variations"]
    parameters = ["projects", "experiments"]
    parameters = ["experiments"]
    for param in parameters:
        Main(param)
