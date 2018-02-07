import utils
import requests
import pandas as pd
import io

def Fetch(name, verbose=True):
    token = utils.ReadFileToken()
    urls = utils.ReadFileURL("urls/{}.url".format(name))

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


def Store(reqs, name, verbose=True):
    dfs = [pd.DataFrame(r.json()) for r in reqs]
    dfs = pd.concat(dfs)

    dfs.to_csv("output/{}.csv".format(name), index=False)

    return dfs


def Tinker(df, target, verbose=True):
    target_url = {
                    'experiments' : "https://www.optimizelyapis.com/experiment/v1/projects/{}/experiments/",
                    'stats'       : "https://www.optimizelyapis.com/experiment/v1/experiments/{}/stats",
                    'variations'  : "https://www.optimizelyapis.com/experiment/v1/variations/{}"
                 }[target]

    if target == 'variations':
        ids = [item for sublist in df['variation_ids'] for item in sublist]
        print(len(ids))
    else:
        ids = df['id']

    urls = [target_url.format(i) for i in ids]
    
    with open("urls/{}.url".format(target), 'w') as f:
        for u in urls:
            f.write(u + '\n')


if __name__ == "__main__":
#    name = "projects"
#    reqs = Fetch(name)
#    df = Store(reqs, name) 
#    Tinker(df, "experiments")

#    name = "experiments"
#    reqs = Fetch(name)
#    df = Store(reqs, name) 
#    Tinker(df, "stats")
    
    name = "experiments"
    reqs = Fetch(name)
    df = Store(reqs, name) 
    Tinker(df, "variations")
