
import base64
import concurrent.futures
import hmac
import hashlib
import json
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

GITHUB_SECRET = os.path.abspath(os.path.dirname(__file__)) + "/secret.txt"
GITHUB_TOKEN = os.path.abspath(os.path.dirname(__file__)) + "/token.txt"
README_FILE = os.path.abspath(os.path.dirname(__file__)) + "/README.md"

@flyreel_srv.post()
def notify_repo(request):
    #key = request.matchdict['val']

    try:
        #import pdb;pdb.set_trace()

        logging.info("Received a request from ""{0}""".format(request.client_addr))

        logging.debug("Validating request source")
        if not 'X-Hub-Signature' in request.headers:
            logging.warn("Could not locate GitHub signature header in request.")
            return False

        if not verify_github_secret(
                request.body,
                read_secret(GITHUB_SECRET),
                request.headers['X-Hub-Signature']):
            logging.warn("WARNING!!! - received incorrect HMAC from request source (potential attacker?)")
            return False

        logging.debug("Request payload =>\t""{0}""".format(request.body))

        if len(request.body) < 1:
            logging.warn("Received empty POST")
            return False

        repo_data = request.json_body

        if "action" not in repo_data:
            logging.warn("Received invalid request (missing 'action' key)")
            return False
        elif repo_data['action'] != 'created':
            logging.info(
                    "Received inconsequential request, action='{0}; ignoring')".format(
                        repo_data['action']))
            return False

        logging.info(
                "Received create event for repository '{0}'".format(
                    repo_data['repository']['name']))

        FUTURE_LST.append(
                PROC_POOL.submit(process_create_event, repo_data))

        #process_create_event(repo_data)
    except ValueError as err:
        logging.error(
                "Encountered error in repo notification POST handler: {0}".format(
                    err))
        return False

    return True

def process_create_event(repo_evt_json):
    try:
        #import pdb;pdb.set_trace()
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

        # Use first commit add README
        logging.info("Commiting initial README")
        readme_str = read_README(README_FILE)
        result = repo.create_file("/README.md", "Initial commit", readme_str)

        commit = result['commit']
        logging.debug("Using sha='{0}' as first commit".format(commit))

        # Create an "unstable" branch/ref
        logging.info("Creating 'unstable' branch")
        unstable_commit = repo.create_git_ref(
                            "refs/heads/unstable",
                            commit.sha)

        # Create a "test" branch/ref
        logging.info("Creating 'test' branch")
        unstable_commit = repo.create_git_ref(
                            "refs/heads/test",
                            commit.sha)

        logging.info("Successfully initialized new repo '{0}'.".format(repo_name))

    except Exception as err:
        logging.error(
                "Encountered error in process pool handler: {0}".format(
                    err))

def read_token(token_path):

    token = ""
    with open(token_path, "r") as token_file:
        token = str(token_file.read()).strip()

    return token

def read_secret(secret_path):

    secret = ""
    with open(secret_path, "r") as secret_file:
        secret = str(secret_file.read()).strip()

    return secret.encode('utf-8')

def read_README(readme_path):

    readme = ""
    with open(readme_path, "r") as readme_file:
        readme = readme_file.read()

    return readme

def verify_github_secret(payload, secret, their_digest):

    my_hmac = hmac.new(secret, payload, hashlib.sha1)

    my_sha = my_hmac.hexdigest()
    their_sha = their_digest[str.find(their_digest, "=") + 1:]

    return hmac.compare_digest(my_sha, their_sha)

#@view_config(route_name='test', renderer='json')
#def my_view_2(request):
#    return {'hello': 'world'}
