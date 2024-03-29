from setuptools import setup, find_packages
import os
import re

if os.environ.get('USER', '') == 'vagrant':
    del os.link

requirements = [r.strip() for r in open('requirements.txt').readlines() if not r.startswith('--')]
requirements = [r if ('git+' not in r) else re.sub(r".*egg=(.*)", r"\1", r).strip() for r in requirements]

setup(
    name='crypto-miner-webui',
    version='0.1',
    author='Ronan Delacroix',
    author_email='ronan.delacroix@gmail.com',
    url='https://github.com/ronhanson/python-crypto-miner-webui',
    packages=find_packages(where='.', exclude=[]) + ['crypto-miner-webui'],
    include_package_data=True,
    package_data={}, #done in MANIFEST.in
    scripts=['bin/crypto-miner-webui'],
    data_files=[],
    license=open('LICENCE.txt').read().strip(),
    description='Crypto Miner Web UI - Sponsored by Kontron',
    long_description=open('README.md').read().strip(),
    setup_requires=requirements,
    classifiers=[
        'Topic :: Utilities',
        'Topic :: Software Development :: Libraries',
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Manufacturing',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
    ],
)
