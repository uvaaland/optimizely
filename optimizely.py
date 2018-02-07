import utils
import requests
import pandas as pd
import io


def GetRequests(name, verbose=True):
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
            print(i, r.url, r.ok)

    with open("urls/failures.url", 'w') as f:
        for r in reqs['failure']:
            f.write(r.url + '\n')

    return reqs['success']


def RequestsToDataframe(reqs, name, verbose=True):
    try:
        dfs = [pd.DataFrame(r.json()) for r in reqs]
    except ValueError:
        dfs = [pd.DataFrame(r.json(), index=[i]) for i, r in enumerate(reqs)]

    dfs = pd.concat(dfs)

    dfs.to_csv("output/{}.csv".format(name), index=False)

    return dfs


def GenerateUrls(df, target, verbose=True):
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


if __name__ == "__main__":
    name = "projects"
    reqs = GetRequests(name)
    df = RequestsToDataframe(reqs, name) 
    GenerateUrls(df, "experiments")
