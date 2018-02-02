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


def Tinker(reqs, verbose=True):
    dfs = [pd.DataFrame(r.json()) for r in reqs]
    dfs = pd.concat(dfs)

    dfs.to_csv("test.csv", index=False)

    ids = dfs['id']

    base_url = {
                'projects' : "https://www.optimizelyapis.com/experiment/v1/projects/{}/experiments/"
               }
    
if __name__ == "__main__":
    urlfile = "urls/projects.url"
    reqs = Fetch(urlfile)
    Tinker(reqs)

