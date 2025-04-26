#!/usr/bin/env python3
"""
notebook4m - ローカルLLMとチャットするためのシンプルなPythonパッケージ
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as f:
    requirements = f.read().splitlines()

setup(
    name="notebook4m",
    version="0.1.0",
    author="notebook4m",
    author_email="",
    description="ローカルLLMとチャットするためのシンプルなPythonパッケージ",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "notebook4m=notebook4m.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "notebook4m": ["data/*"],
    },
)
