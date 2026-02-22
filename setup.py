"""
Geographic Risk Data - Python Package
Extracts HIFCA and HIDTA county-level geographic risk data
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="geo-risk-data",
    version="1.0.0",
    author="Jyothichandra Praneeth Abburi",
    author_email="pranabburi@gmail.com",
    description="Extract HIFCA and HIDTA county-level geographic risk data from official sources",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pran-gamya/geo-risk-data",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Financial and Insurance Industry",
        "Topic :: Office/Business :: Financial",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.7",
    install_requires=requirements,
    extras_require={
        "pdf": ["pdfplumber>=0.9.0"],
        "dev": ["pytest>=7.0", "pytest-cov>=3.0", "black>=22.0", "flake8>=4.0"],
    },
    entry_points={
        "console_scripts": [
            "geo-risk-data=geo_risk_data.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "geo_risk_data": ["data/*.json"],
    },
)
