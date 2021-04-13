#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

# with open('README.md') as readme_file:
#     readme = readme_file.read()

# with open('requirements.txt') as requirements_file:
#     requirements = requirements_file.read().splitlines()

requirements = ['pandas>=1.2.3', 'numpy>=1.20.0']

setup_requirements = []

test_requirements = []

setup(
    author="Haokui Zhou, Shuo Chen, Xilan Yang",
    author_email='haokui.zhou@gmail.com',
    python_requires='>=3.7',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
    description="A python module for bioinformatics to organize, manage, and package omics datasets, serving as data portal for modeling.",
    install_requires=requirements,
    license="BSD 3-Clause License",
    # long_description=readme,
    include_package_data=True,
    name='octobus',
    packages=find_packages(),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/haokui/octobus',
    download_url='https://github.com/haokui/octobus/archive/refs/tags/v0.1.2.tar.gz',
    version='0.1.2',
    zip_safe=False,
)
