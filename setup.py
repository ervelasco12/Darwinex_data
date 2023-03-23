"""darwinex-data setup script"""

from setuptools import setup, find_packages
from pathlib import Path

here = Path(__file__).parent.resolve()

__version__ = None
with open(here / 'version.py') as f:
    exec(f.read())
print(here)

setup(
    name='darwinex-data',
    version=__version__,
    description='Download Darwinex FTP darwins data',
    url='https://github.com/ervelasco12/darwinex_data',
    author='Eduardo R. de Velasco',
    author_email='ervelasco12@yahoo.es',
    license='MIT',
    python_requires='>=3.6',
    install_requires=['pandas'],
    packages=find_packages(),
    platforms = ['any'],
    keywords='darwinex finance ftp download data python python3'
    )

