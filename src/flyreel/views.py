
import concurrent.futures
import logging
import os

from github         import Github
from pyramid.view   import view_config
from cornice        import Service

flyreel_srv = Service(name="fs",
                      path="/flyreel",
                      description="flyreel server")

#@view_config(route_name='home', renderer='templates/mytemplate.jinja2')
#def my_view(request):
#    return {'project': 'flyreel'}

#@flyreel_srv.get()
#def get_val(request):
#    return _VALUES.get(request.matchdict['val'])

FUTURE_LST= []
PROC_POOL = concurrent.futures.ProcessPoolExecutor(max_workers=4)

GITHUB_TOKEN = os.path.abspath(os.path.dirname(__file__)) + "/token.txt"

@flyreel_srv.post()
def notify_repo(request):
    #key = request.matchdict['val']

    try:
        #import pdb;pdb.set_trace()

        logging.debug("Received request =>\t""{0}""".format(request.body))

        if len(request.body) < 1:
            logging.error("Received empty POST")
            return False

        repo_data = request.json_body

        if "action" not in repo_data:
            logging.error("Received invalid request (missing 'action' key)")
            return False
        elif repo_data['action'] != 'created':
            logging.info(
                    "Received inconsequential request (action='{0}')".format(
                        repo_data['action']))
            return False

        logging.info(
                "Received create event for repository '{0}'".format(
                    repo_data['repository']['name']))

        #FUTURE_LST.append(
        #        PROC_POOL.submit(process_create_event, repo_data))

        process_create_event(repo_data)
    except ValueError as err:
        logging.error(
                "Encountered error in repo notification POST handler: {0}".format(
                    err))
        return False

    return True

def process_create_event(repo_evt_json):
    try:
        import pdb;pdb.set_trace()
        repo_name = repo_evt_json['repository']['full_name']

        logging.debug(
            "Process pool executing event for '{0}'".format(
                repo_name))

        gh_inst = Github(read_token(GITHUB_TOKEN))

        repo = gh_inst.get_repo(repo_name)
        if not repo:
            raise Exception("Could not locate repository '{0}'".format(
                repo_name))

        clone_url = repo.clone_url

        logging.info("Located repo at url '{0}'".format(clone_url))

    except Exception as err:
        logging.error(
                "Encountered error in process pool handler: {0}".format(
                    err))


def read_token(token_path):

    token = ""
    with open(token_path, "r") as token_file:
        token = str(token_file.read()).strip()

    return token

#@view_config(route_name='test', renderer='json')
#def my_view_2(request):
#    return {'hello': 'world'}
