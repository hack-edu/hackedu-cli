import click
from api import Api
from integrations.sonarqube import SonarqubeBase
import uuid
import json
from tabulate import tabulate
from urllib.parse import urlencode
import time

class State(object):

    def __init__(self):
        self.verbosity = 0
        self.debug = False
        self.api_key = None
        self.headers = None

pass_state = click.make_pass_decorator(State, ensure=True)


def api_key_option(f):
    def callback(ctx, param, value):
        state = ctx.ensure_object(State)
        state.api_key = value
        state.headers = {"X-API-Key": value}
        return value
    return click.option("--api_key",
                        expose_value=False,
                        help="Required X-API-Key header for interacting with the HackEDU Public API.",
                        callback=callback)(f)

def common_options(f):
    f = api_key_option(f)
    return f


@click.group()
def hackedu():
    """A CLI wrapper for the HackEDU Public API."""



@hackedu.command("issue-source")
@click.argument("argument")
@click.option("--title", help="Name of issue source.")
@click.option("--type", help="Name of issue source type.")
@common_options
@pass_state
def issue_source(state, argument, title, type):
    """List issue sources."""
    api = Api(state.headers)
    issue_source_path = "/v1-beta/issue-sources"
    # issue_source_types_path = "/v1-beta/issue-source-types"
    organization_path = "/v1-beta/organization"

    if argument == "ls":
        response = api.get(issue_source_path)
        if response.status_code == 200:
            items = response.json()["issue_sources"]
            if items:
                header = list(items[0].keys())[0:3]
                rows = [list(x.values())[0:3] for x in items]
                print(tabulate(rows, header))
            else:
                print("Warning: No issue sources returned.")
        else:
            print("Something went wrong. Please ensure your API Key is valid and that all issues "
                  "sources have the proper settings.")

    if argument == "create":
        if not title:
            print("Error: Missing required option '--title'")
            return

        # response = api.get("{}?key={}".format(issue_source_types_path, type))
        # key = response.json()["issue_source_types"][0]["issue_source_type_id"]

        #TODO: if we need to pick through multiple sources or source types use this
        # choice = click.prompt(
        #     "Please select a source type:",
        #     type=click.Choice([str(i) for i in types]),
        #     show_default=False,
        # )

        print("creating issue source...")
        organization_uuid = api.get(organization_path)

        payload = {
            "uuid":uuid.uuid4(),
            "title": title,
            # "type_": key,
            "organization_uuid": organization_uuid,
            "settings": json.dumps({}),
        }
        response = api.post(issue_source_path, payload)
        if response.status_code == 200:
            print("Success!")
            print(response.json()["uuid"])
        else:
            print("Something went wrong...")
            print (response.json())


#TODO: make these sonarqube options required only if create argument is used.
#TODO: see custom classes: https://stackoverflow.com/questions/44247099/click-command-line-interfaces-make-options-required-if-other-optional-option-is
@hackedu.command("issues")
@click.argument("argument")
@click.option("--url", required=False, help="Sonarqube URL.")
@click.option("--username", required=False, help="Sonarqube username.")
@click.option("--password", required=False, help="Sonarqube password")
@click.option("--branch", required=False, help="Repository branch name.")
@click.option("--app", required=False, help="Sonarqube app name.")
@click.option("--source", required=False, help="Issue source uuid.")
@common_options
@pass_state
def issues(state, argument, url, username, password, branch, app, source):
    """List issues from source uuid."""
    api = Api(state.headers)
    sonarqube = SonarqubeBase(url, username, password, app, branch)
    issues_path = "/v1-beta/issues"
    vulnerabilities_path = "/v1-beta/vulnerabilities"

    if argument == "ls":
        response = api.get(issues_path)
        issues = response.json()["issues"]
        header = ["issue uuid", "unique id"]
        rows = []
        for issue in issues:
            rows.append([issue["uuid"], issue["issue_source_unique_id"]])
        print(tabulate(rows, header))

    if argument == "sync":
        print("syncing sonarqube...")
        success = False
        sonarqube_vulnerabilities = sonarqube.get_vulnerabilities()
        print("found {} issues".format(len(sonarqube_vulnerabilities)))
        print('syncing issues to hackedu...')

        for sonarqube_vulnerability in sonarqube_vulnerabilities:
            response = api.get("{}?{}".format(vulnerabilities_path,
                                              urlencode(sonarqube_vulnerability["vulnerability_types"])))
            if response.status_code != 200:
                print("Something went wrong")
                print(response.json())
                return

            hackedu_vulnerability_id = response.json()['vulnerabilities'][0]["id"] #TODO: we might need to loop through this list?
            payload = {
                "title": sonarqube_vulnerability["title"],
                "description": "",
                "issue_source_uuid": source,
                "issue_source_unique_id": uuid.uuid4(),
                "app_id": app,
                "severity": sonarqube_vulnerability["severity"],
                "vulnerability": hackedu_vulnerability_id,
                "timestamp": sonarqube_vulnerability["timestamp"],
                "url": "{}/project/issues?id={}&types=VULNERABILITY".format(url, app)
            }
            response = api.post(issues_path, payload)
            if response.status_code != 200:
                print("Something went wrong")
                print(response.json())
                return

            success = True
            time.sleep(.5)

        if success:
            print("Success!")


if __name__ == "__main__":
    hackedu(prog_name="hackedu")
