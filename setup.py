from setuptools import setup, find_packages


setup(
    name='core-cli',
    version='0.0.2',
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
