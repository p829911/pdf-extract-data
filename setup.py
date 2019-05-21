from setuptools import setup, find_packages

setup(
    name="pdf_extract_data",
    version="1.0",
    description="Python package for extracting data from pdf",
    author="p829911",
    author_email="p829911@gmail.com",
    url="https://github.com/p829911/pdf_extract_data",
    install_requires=["pandas", "numpy", "pdfminer.six", "camelot-py[cv]"],
    packages=find_packages(),
    keywords=["pdf extract", "extract data from pdf", "extract from pdf"],
    python_requires=">=3"
)