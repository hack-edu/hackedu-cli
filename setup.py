import pathlib
import setuptools
from setuptools import setup

HERE = pathlib.Path(__file__).parent

README = (HERE / "README.md").read_text()

VERSION = (HERE / "__version__.py").read_text().split("=")[1]

setup(
    name="hackedu-cli",
    version=VERSION,
    description="HackEDU's command line interface allows customer's to interact directly with HackEDU resources "
                "from the command line.",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/hack-edu/hackedu-cli",
    author="HackEDU",
    author_email="matt@hackedu.com",
    license="Copyright HackEDU",
    packages=setuptools.find_packages(),
    include_package_data=True,
    install_requires=[
        "requests==2.25.1",
        "click==7.1.2",
        "tabulate==0.8.9",
        "python-sonarqube-api==1.2.1"
    ],
    scripts=["bin/hackedu"],
)
