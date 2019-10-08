from setuptools import setup, find_packages
setup(
    name='jobautomation',
    version='0.0.1',
    paskages=find_packages(),
    install_requires=[
        'ase',
        'paramiko',
    ],
)