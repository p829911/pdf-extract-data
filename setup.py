from setuptools import setup, find_packages

setup(
    name="pdfextractdata",
    version="4.8",
    description="Python package for extracting data from pdf",
    author="p829911",
    author_email="p829911@gmail.com",
    url="https://github.com/p829911/pdf-extract-data",
    install_requires=["camelot-py[cv]"],
    packages=find_packages(),
    keywords=["pdf extract", "extract data from pdf", "extract from pdf"],
    python_requires=">=3"
)
