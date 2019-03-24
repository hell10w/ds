from setuptools import find_packages
from setuptools import setup

import ds

setup(
    name='dsjk-core',
    version=ds.__version__,
    author='',
    author_email='',
    url='',
    description='',
    long_description=open('README.md').read().strip(),
    packages=find_packages(exclude=('tests', )),
    install_requires=[
        'six',
        'docopt',
        'cachetools',
    ],
    extras_require={
        'repl': ['prompt_toolkit>=2.0.0'],
    },
    test_suite='tests',
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'ds=ds.__main__:main',
        ],
    },
)
