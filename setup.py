from os import path
from setuptools import setup, find_packages

here = path.abspath(path.dirname(__file__))

with open(path.join(here, "README.md"), encoding="utf-8") as f:
    readme = f.read()

setup(
    name="hackedu-cli",
    version="0.1.7",
    description="HackEDU's command line interface allows customer's to interact directly with HackEDU resources "
                "from the command line.",
    long_description=readme,
    long_description_content_type="text/markdown",
    url="https://github.com/hack-edu/hackedu-cli",
    author="HackEDU",
    author_email="matt@hackedu.com",
    license="Copyright HackEDU",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "requests==2.25.1",
        "click==7.1.2",
        "tabulate==0.8.9",
        "python-sonarqube-api==1.2.1"
    ],
    scripts=["bin/hackedu"],
)
