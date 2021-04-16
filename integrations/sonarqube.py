from sonarqube import SonarQubeClient, SonarEnterpriseClient, SonarCloudClient
import click
import sys
import re

class SonarqubeBase(object):
    def __init__(self, organization, url, username, password, token, app, branch, edition):
        self.organization = organization
        self.url = url
        self.username = username
        self.password = password
        self.token = token
        self.app = app
        self.branch = branch
        self.edition = edition

        if not self.token and not (self.username and self.password):
            print("Failed!")
            print("Either token or username and password must be provided.")
            sys.exit()

        if not self.url:
            print("Failed!")
            print("Sonarqube URL is required.")
            sys.exit()

        if not self.app:
            print("Failed!")
            print("Sonarqube app is required.")
            sys.exit()

        if not self.branch:
            print("Failed!")
            print("Branch is required.")
            sys.exit()

        if self.username and self.password:
            if self.edition == 'cloud':
                print("Failed!")
                print("Sonar Cloud only accepts token based authentication.")
                sys.exit()

            if self.edition == "community":
                self.client = SonarQubeClient(sonarqube_url=self.url, username=self.username, password=self.password)
            elif self.edition == "enterprise":
                self.client = SonarEnterpriseClient(sonarqube_url=self.url, username=self.username, password=self.password)
            else:
                self.client = SonarQubeClient(sonarqube_url=self.url, username=self.username, password=self.password)

        if token:
            if self.edition == "community":
                self.client = SonarQubeClient(sonarqube_url=self.url, token=self.token)
            elif self.edition == "enterprise":
                self.client = SonarEnterpriseClient(sonarqube_url=self.url, token=self.token)
            elif self.edition == "cloud":
                if not self.organization:
                    print("Failed!")
                    print("Organization is required.")
                    sys.exit()
                self.client = SonarCloudClient(sonarcloud_url=self.url, token=self.token)
            else:
                self.client = SonarQubeClient(sonarqube_url=self.url, token=self.token)


    def get_vulnerabilities(self):
        issues = list(self.client.issues.search_issues(componentKeys=self.app, branch=self.branch))
        vulnerabilities = []

        severity_mapping = {
            "BLOCKER": 9,
            "CRITICAL": 7,
            "MAJOR": 5,
            "MINOR": 3
        }

        with click.progressbar(issues) as _issues:
            for issue in _issues:

                rule = self.client.rules.get_rule(key=issue["rule"])

                if self.edition == 'cloud':
                    rule = self.client.rules.get_rule(key=issue["rule"], organization=self.organization)

                if rule["rule"]["type"] == "VULNERABILITY":

                    timestamp = issue["creationDate"]
                    desc = rule["rule"]["htmlDesc"]
                    severity =  rule["rule"]["severity"]

                    m_cwe = re.search("CWE-[0-9]+", desc)
                    m_cve = re.search("CVE-[0-9]+", desc)
                    m_capec = re.search("CAPEC-[0-9]+", desc)
                    readable_list = list(set([m_cwe.group(0) if m_cwe else None,
                                                     m_cve.group(0) if m_cve else None,
                                                     m_capec.group(0) if m_capec else None]))

                    vulnerability_obj = {
                        "title": issue["message"],
                        "severity": severity_mapping[severity],
                        "timestamp": timestamp,
                        "vulnerabilities": [x for x in readable_list if x is not None],
                        "vulnerability_types": {
                            "cwe": m_cwe.group(0).split("-")[1] if m_cwe else "",
                            "cve": m_cve.group(0).split("-")[1] if m_cve else "",
                            "capec": m_capec.group(0).split("-")[1] if m_capec else ""
                        }
                    }

                    vulnerabilities.append(vulnerability_obj)

        return vulnerabilities
