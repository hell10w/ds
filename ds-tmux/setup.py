from setuptools import find_packages
from setuptools import setup

setup(
    name='dsjk-tmux',
    version='0.0.1',
    author='',
    author_email='',
    url='',
    description='',
    packages=find_packages(exclude=('tests', )),
    install_requires=[
        'dsjk-core',
        'libtmux',
    ],
    include_package_data=True,
)
