from setuptools import find_packages
from setuptools import setup

setup(
    name='dsjk-docker',
    version='0.0.1',
    author='',
    author_email='',
    url='',
    description='',
    packages=find_packages(exclude=('tests', )),
    install_requires=[
        'dsjk-core',
        'docker>=3.1.3',
    ],
    include_package_data=True,
)
