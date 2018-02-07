import utils
import requests
import pandas as pd
import io


def _GetRequests(name, verbose=True):
    token = utils.ReadFileToken()
    urls = utils.ReadFileURL("urls/{}.url".format(name))

    session = requests.Session()
    reqs = {'success':[], 'failure':[]}
    for i, u in enumerate(urls):
        r = session.get(u, headers={'Token': token})
        if r.ok:
            reqs['success'].append(r)
        else:
            reqs['failure'].append(r)

        if verbose:
            count = "[{0:03}/{1:03}]:".format(i+1, len(urls))
            print("{0:^10}{1:^60}{2:^10}".format(count, ".../" + r.url[31:], str(r.ok)))

    with open("urls/failures.url", 'w') as f:
        for r in reqs['failure']:
            f.write(r.url + '\n')

    return reqs['success']


def _RequestsToDataframe(reqs, name, verbose=True):
    try:
        dfs = [pd.DataFrame(r.json()) for r in reqs]
    except ValueError:
        dfs = [pd.DataFrame(r.json(), index=[i]) for i, r in enumerate(reqs)]

    dfs = pd.concat(dfs)

    dfs.to_csv("output/{}.csv".format(name), index=False)

    return dfs


def _GenerateUrls(df, target, verbose=True):
    target_url = {
                    'experiments' : "https://www.optimizelyapis.com/experiment/v1/projects/{}/experiments/",
                    'stats'       : "https://www.optimizelyapis.com/experiment/v1/experiments/{}/stats",
                    'variations'  : "https://www.optimizelyapis.com/experiment/v1/variations/{}"
                 }[target]

    if target == 'variations':
        ids = [item for sublist in df['variation_ids'] for item in sublist]
    else:
        ids = df['id']

    urls = [target_url.format(i) for i in ids]
    
    with open("urls/{}.url".format(target), 'w') as f:
        for u in urls:
            f.write(u + '\n')


def Main():
    print("-"*80)
    print(" "*30 + "GETTING REQUESTS")
    print("-"*80)

    print("{0:^10}{1:^60}{2:^10}".format("#", "REQUEST (https://www.optimizelyapis.com/...)", "SUCCESS"))
    print("-"*80)

    name = "projects"
    reqs = _GetRequests(name)

    print("-"*80)

    df = _RequestsToDataframe(reqs, name) 
    _GenerateUrls(df, "experiments")

    print("\n***\n")

    print("-"*80)
    print(" "*30 + "GETTING REQUESTS")
    print("-"*80)

    print("{0:^10}{1:^60}{2:^10}".format("#", "REQUEST (https://www.optimizelyapis.com/...)", "SUCCESS"))
    print("-"*80)

    name = "experiments"
    reqs = _GetRequests(name)

    print("-"*80)

    df = _RequestsToDataframe(reqs, name) 
    _GenerateUrls(df, "stats")


if __name__ == "__main__":
    Main()
