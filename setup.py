from setuptools import setup, find_packages
from sys import platform

# read the contents of the README file
import os
from os import path

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

def get_version():
    """Load the version from version.py, without importing it.
    This function assumes that the last line in the file contains a variable defining the
    version string with single quotes.
    """
    try:
        with open('rehoused_nlp/_version.py', 'r') as f:
            return f.read().split('\n')[0].split('=')[-1].replace('\'', '').strip()
    except IOError:
        raise IOError

setup(
    name="rehoused_nlp",
    version=get_version(),
    description="medspaCy NLP pipeline for detecting patient housing stability.",
    author="alec.chapman",
    author_email="alec.chapman@hsc.utah.edu",
    packages=find_packages(),
    install_requires=[
        "medspacy>=0.1.0.2",
    ],
    long_description=long_description,
    long_description_content_type="text/markdown",
)