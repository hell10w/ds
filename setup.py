from setuptools import find_packages
from setuptools import setup

import ds

setup(
    name='ds',
    version=ds.__version__,
    author='',
    author_email='',
    url='',
    description='',
    long_description=open('README.md').read().strip(),
    packages=find_packages(),
    install_requires=[
        'six',
        'docopt',
    ],
    test_suite='tests',
    entry_points={
        'console_scripts': [
            'ds=ds.__main__:main',
        ],
    },
)
