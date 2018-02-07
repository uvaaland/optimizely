import utils
import requests
import pandas as pd
import io

def Fetch(urlfile, verbose=True):
    token = utils.ReadFileToken()
    urls = utils.ReadFileURL(urlfile)

    session = requests.Session()
    reqs = {'success':[], 'failure':[]}
    for u in urls:
        r = session.get(u, headers={'Token': token})
        if r.ok:
            reqs['success'].append(r)
        else:
            reqs['failure'].append(r)

        if verbose:
            print(r.url, r.ok)

    with open("fail.txt", 'w') as f:
        for r in reqs['failure']:
            f.write(r.url + '\n')

    return reqs['success']


def Tinker(reqs, target, verbose=True):
    dfs = [pd.DataFrame(r.json()) for r in reqs]
    dfs = pd.concat(dfs)

    origin = {
                'experiments' : 'projects',
                'stats' : 'experiments'
             }[target]

    dfs.to_csv("output/{}.csv".format(origin), index=False)

    target_url = {
                    'experiments' : "https://www.optimizelyapis.com/experiment/v1/projects/{}/experiments/",
                    'stats' : "https://www.optimizelyapis.com/experiment/v1/experiments/{}/stats"
                 }[target]

    ids = dfs['id']

    urls = [target_url.format(i) for i in ids]
    
    with open("urls/{}.url".format(target), 'w') as f:
        for u in urls:
            f.write(u + '\n')

if __name__ == "__main__":
#    urlfile = "urls/projects.url"
#    reqs = Fetch(urlfile)
#    Tinker(reqs, "experiments")

#    urlfile = "urls/experiments.url"
#    reqs = Fetch(urlfile)
#    Tinker(reqs, "stats")

    urlfile = "urls/stats.url"
    reqs = Fetch(urlfile)
    Tinker(reqs, "stats")


