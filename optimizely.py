import utils
import requests
import pandas as pd
import io


HEADER = "{0:^80}"
STATUS_BAR = "{0:^10}{1:^60}{2:^10}"
HORIZONTAL_RULE = "-"*80


def _GetRequests(param, verbose=True):
    token = utils.ReadFileToken()
    urls = utils.ReadFileURL("urls/{}.url".format(param))

    session = requests.Session()
    reqs = {"success":[], "failure":[]}
    for i, u in enumerate(urls):
        r = session.get(u, headers={'Token': token})
        if r.ok:
            reqs["success"].append(r)
        else:
            reqs["failure"].append(r)

        if verbose:
            count = "[{0:03}/{1:03}]:".format(i+1, len(urls))
            print(STATUS_BAR.format(count, ".../" + r.url[31:], str(r.ok)))

    if verbose:
        print(HORIZONTAL_RULE)

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

    reqs = _GetRequests(param, verbose=verbose)
    dataframe = _RequestsToDataframe(reqs, param, verbose=verbose) 

    if param == "projects":
        _GenerateUrls(dataframe, "experiments", verbose=verbose)
    elif param == "experiments":
        _GenerateUrls(dataframe, "stats", verbose=verbose)
        _GenerateUrls(dataframe, "variations", verbose=verbose)

    if verbose:
        print(HORIZONTAL_RULE)


if __name__ == "__main__":
    parameters = ["projects", "experiments", "stats", "variations"]
    for param in parameters:
        Main(param)
