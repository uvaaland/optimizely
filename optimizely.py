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
import time
import sys
from aiohttp import ClientSession, ContentTypeError
from requests import Session
import pandas as pd


# Print formatting
HEADER = "{1}{0:^78}{1}"
STATUS_BAR = "{0:^10}{1:^60}{2:^10}"
HORIZONTAL_RULE = "{0}"*80


class Logger:

    def __init__(self):
        self.terminal = sys.stdout
        self.log = open("{}.log".format(time.strftime("%Y-%m-%d")), "a")
        self.elapsed = {
            "projects"    : 0.0,
            "experiments" : 0.0,
            "stats"       : 0.0,
            "variations"  : 0.0
        }
        self.request_status = {
            "projects"    : (0, 0),
            "experiments" : (0, 0),
            "stats"       : (0, 0),
            "variations"  : (0, 0)
        }

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)

    def flush(self):
        pass


async def fetch_all(urls, token):
    """Launch requests for all web pages.

    Takes in a list of urls and a token and asynchronously launches a request
    for each url in the list with the given token.

    Args:
        urls: A list of all the urls to be fetched.
        token: A string with token that is needed to make requests.

    Returns:
        A dictionary that maps url keys to a tuple containing the status and
        json content of the corresponding request. For example:

        {"https://example.com" : (200, [{"name" : "John", "city" : "New York"};])
    """

    tasks = []
    tracker = [0, len(urls)]
    async with ClientSession() as session:
        for url in urls:
            task = asyncio.ensure_future(fetch(url, token, session, tracker))
            tasks.append(task) # create list of tasks
        responses = await asyncio.gather(*tasks) # gather task responses

        return responses


async def fetch(url, token, session, tracker):
    """Fetch a url asynchronously, using specified ClientSession.

    Makes a request for the given url and extracts status and json content of
    the request asynchronously. Stores the status and json content in
    a dictionary that maps it to the corresponding url.

    Args:
        url: A string containing a web page address.
        token: A string with token that is needed to make requests.
        session: A ClientSession object used to make requests.
        tracker: A list containing the current iteration and the total number
            of iterations.

    Returns:
        A dictionary that maps the url to a tuple containing the request status
        and a list of the json content of said request.
    """

    header = {'Token': token}
    async with session.get(url, headers=header) as response:
        try:
            content = await response.json()
        except ContentTypeError:
            content = []
        status = response.status

        # Print status
        tracker[0] = tracker[0] + 1
        count = "[{0:03}/{1:03}]:".format(tracker[0], tracker[1])
        print(STATUS_BAR.format(count, ".../" + url[31:], str(status == 200)))

        return {url : (status, content)}


def _get_requests_async(urls, token):
    """Fetch list of web pages asynchronously.

    Fetches a list of web pages asynchronously and extracts the request status
    and json content which is mapped to the url in a dictionary.

    Args:
        urls: A list of web pages.
        token: A string with token that is needed to make requests.

    Returns:
        A dictionary that maps url keys to a tuple containing the status and
        json content of the corresponding request. For example:

        {"https://example.com" : (200, [{"name" : "John", "city" : "New York"};])
    """

    loop = asyncio.get_event_loop()
    future = asyncio.ensure_future(fetch_all(urls, token))
    responses = loop.run_until_complete(future)

    return {k : v for d in responses for (k, v) in d.items()}


def _get_requests_sync(urls, token):
    """Fetch list of web pages sequentially.

    Fetches a list of web pages sequentially and extracts the request status
    and json content which is mapped to the url in a dictionary.

    Args:
        urls: A list of web pages.
        token: A string with token that is needed to make requests.

    Returns:
        A dictionary that maps url keys to a tuple containing the status and
        json content of the corresponding request. For example:

        {"https://example.com" : (200, [{"name" : "John", "city" : "New York"};])
    """

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

        # Print status
        count = "[{0:03}/{1:03}]:".format(i+1, len(urls))
        print(STATUS_BAR.format(count, ".../" + url[31:], str(status == 200)))

    return responses


def get_requests(urls, token, async=True):
    """Launches the fetching of web pages in either asynchronous or sequential mode.

    Takes in a list of web pages and a token and launches a routine for
    fetching the web pages which can be asyncronous or sequential, depending on
    the async parameter.

    Args:
        urls: A list of web pages.
        token: A string with token that is needed to make requests.
        async: Optional argument for running in asynchronous mode.

    Returns:
        A dictionary that maps url keys to a tuple containing the status and
        json content of the corresponding request. For example:

        {"https://example.com" : (200, [{"name" : "John", "city" : "New York"};])
    """

    if async:
        responses = _get_requests_async(urls, token)
    else:
        responses = _get_requests_sync(urls, token)

    return responses


def content_to_dataframe(content):
    """Converts a list of json data to a dataframe.

    Takes a list of json data and converts each element to a dataframe. Then
    concatenates all the dataframes to a single dataframe and returns.

    Args:
        content: A list of json data.

    Returns:
        A single dataframe containing all the data in the input json list.
    """

    try:
        dfs = [pd.DataFrame(c) for c in content]
    except ValueError:
        dfs = [pd.DataFrame(c, index=[i]) for i, c in enumerate(content)]

    return pd.concat(dfs)


def _generate_urls(dataframe, target):
    """Generates a list of urls based on data from the dataframe.

    Takes in a dataframe and a target for which urls will be generated. Chooses
    a url extension and ids based on the given target and formats the output
    urls accordingly.

    Args:
        dataframe: A dataframe containing information from a set of web pages.
        target: A string with the name for which urls should be generated.

    Returns:
        A list of urls formatted according to the given target.
    """

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


def generate_url_files(dataframe, targets):
    """Writes a file of urls for the given targets.

    Takes in a dataframe and a list of targets and generates a url file for
    each of the targets based on the information in the dataframe. The output
    url file can be found in the urls/ folder.

    Args:
        dataframe: A dataframe containing information from a set of web pages.
        targets: A list of strings with the name for which a url file should be
            generated.

    Returns:
        None
    """

    for target in targets:
        urls = _generate_urls(dataframe, target)

        with open("urls/{}.url".format(target), 'w') as outfile:
            for url in urls:
                outfile.write(url + '\n')

        # Print status
        print("Saved '{0}' urls to 'urls/{0}.url'.".format(target))


def write_summary(logger):

    print(HORIZONTAL_RULE.format('*'))
    print(HEADER.format("SUMMARY", '*'))
    print(HORIZONTAL_RULE.format('*'))
    print()

    print(HORIZONTAL_RULE.format('-'))
    print(HEADER.format("SUCCESSFUL REQUESTS", ' '))
    print(HORIZONTAL_RULE.format('-'))

    total_success = 0
    total_attempt = 0
    for key, value in logger.request_status.items():
        print("{0:<70}[{1:03}/{2:03}]".format(key, value[0], value[1]))
        total_success += value[0]
        total_attempt += value[1]

    print(HORIZONTAL_RULE.format('-'))
    print("{0:<70}[{1:03}/{2:03}]".format("Total:", total_success, total_attempt))
    print()

    print(HORIZONTAL_RULE.format('-'))
    print(HEADER.format("ELAPSED TIME", ' '))
    print(HORIZONTAL_RULE.format('-'))

    total_elapsed = 0.0
    for key, value in logger.elapsed.items():
        print("{0:14}{1:63.2f}s".format(key, value))
        total_elapsed += value

    print(HORIZONTAL_RULE.format('-'))
    print("{0:14}{1:63.2f}s".format("Total:", total_elapsed))
    print('\n')

    print(HORIZONTAL_RULE.format('*'))
    print(HEADER.format("END SUMMARY", '*'))
    print(HORIZONTAL_RULE.format('*'))


def write_loop_end(par, targets):
    print(HORIZONTAL_RULE.format('-'))
    print("Saved '{0}' frame to 'output/{0}.csv'.".format(par))
    for target in targets[par]:
        print("Saved '{0}' urls to 'urls/{0}.url'.".format(target))
    print('\n')


def write_loop_start(par):
    print(HORIZONTAL_RULE.format('-'))
    print(HEADER.format(par.upper(), ' '))
    print(HORIZONTAL_RULE.format('-'))

    print(STATUS_BAR.format("#", "REQUEST (https://www.optimizelyapis.com/...)", "SUCCESS"))
    print(HORIZONTAL_RULE.format('-'))



def write_program_start():
    print('\n')
    print(HORIZONTAL_RULE.format('#'))
    print(HEADER.format("OPTIMIZELY", '#'))
    print(HORIZONTAL_RULE.format('#'))
    print('\n')



def main():
    """Pulls data for every project, experiment, stat, and variation and writes
    it to file.

    Loops through all the projects, experiments, stats, and variations and
    pulls down data from the optimizely web pages. The data is stored as .csv
    files and can be found in the output/ folder.

    Args:
        None

    Returns:
        None
    """

    write_program_start()

    logger = Logger()

    with open("token/token.txt", 'r') as infile:
        token = infile.read().rstrip('\n')

    targets = {
        "projects"    : ["experiments"],
        "experiments" : ["stats", "variations"],
        "stats"       : [],
        "variations"  : []
    }

    parameters = ["projects", "experiments", "stats", "variations"]
#    parameters = ["projects", "experiments"]
    for par in parameters:

        urls_in = []
        urls_fail = []
        urls_out = {}

        write_loop_start(par)

        start_time = default_timer()

        with open("urls/{}.url".format(par), 'r') as infile:
            urls_in = infile.read().splitlines()

        responses = get_requests(urls_in, token)

        for url in urls_in:
            if responses[url][0] != 200:
                responses.pop(url, None)
                urls_fail.append(url)

#        urls_fail = [url for url in urls if responses[url][0] != 200]
#        logger.request_status[par] = (len(urls)-len(urls_fail), len(urls))
#        with open("urls/failures.url", 'w' if par == 'projects' else 'a') as outfile:
#            for url in urls_fail:
#                outfile.write(url + '\n')
#                responses.pop(url, None)

        content = [v[1] for v in list(responses.values())]

        dataframe = content_to_dataframe(content)

        for target in targets[par]:
            urls_out[target] = _generate_urls(dataframe, target)
    
#            with open("urls/{}.url".format(target), 'w') as outfile:
#                for url in urls_out:
#                    outfile.write(url + '\n')

        # Write to files
        dataframe.to_csv("output/{}.csv".format(par), index=False)

        with open("urls/failures.url", 'w' if par == 'projects' else 'a') as outfile:
            for url in urls_fail:
                outfile.write(url + '\n')

        for target in urls_out:
            with open("urls/{}.url".format(target), 'w') as outfile:
                for url in urls_out[target]:
                    outfile.write(url + '\n')

        # Update logger
        logger.request_status[par] = (len(responses), len(urls_in))
        logger.elapsed[par] = default_timer() - start_time

        write_loop_end(par, targets)

    write_summary(logger)

if __name__ == "__main__":
    main()
