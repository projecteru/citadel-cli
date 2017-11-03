import sys

from setuptools import setup, find_packages


if sys.version_info < (3, 3):
    error = """
Must use Python 3.3 or above, pip >= 9.0.1
Python {py} detected.
""".format(py=sys.version_info)
    sys.exit(1)

setup(
    name='core-cli',
    version='0.5.0',
    author='tonic',
    zip_safe=False,
    author_email='tonic@wolege.ca',
    description='Citadel client cli and lib',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'requests',
        'setuptools',
        'prettytable',
        'pyyaml',
        'envoy',
        'click',
        'six',
        'simplejson',
    ],
    entry_points={
        'console_scripts': [
            'corecli=corecli.cli.cli:main',
        ],
    },
)
