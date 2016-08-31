from setuptools import setup, find_packages

setup(
    name='core-cli',
    version='0.0.1',
    author='tonic',
    zip_safe=False,
    author_email='tonic@wolege.ca',
    description='Eru Core Cli',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'requests',
        'setuptools',
        'prettytable',
        'pyyaml',
        'envoy',
        'paramiko',
        'citadelpy',
    ],
    dependency_links=[
        'git+http://gitlab.ricebook.net/platform/citadel-py.git#egg=citadelpy-0.0.1',
    ],
    entry_points={
        'console_scripts': [
            'corecli=corecli.cli.cli:main',
        ],
    },
)
