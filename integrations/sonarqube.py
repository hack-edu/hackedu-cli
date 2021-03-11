from sonarqube import SonarQubeClient
import re

class SonarqubeBase(object):
    def __init__(self, url, username, password, app, branch):
        self.url = url
        self.username = username
        self.password = password
        self.app = app
        self.branch = branch
        self.client = SonarQubeClient(sonarqube_url=self.url, username=self.username, password=self.password)

    def get_vulnerabilities(self):
        issues = list(self.client.issues.search_issues(componentKeys=self.app, branch=self.branch))
        vulnerabilities = []

        severity_mapping = {
            "BLOCKER": 9,
            "CRITICAL": 7,
            "MAJOR": 5,
            "MINOR": 3
        }

        for issue in issues:
            rule = self.client.rules.get_rule(key=issue["rule"])

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
