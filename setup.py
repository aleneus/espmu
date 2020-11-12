from setuptools import setup, find_packages
from espmu import __version__

AUTHORS = ['Information Trust Institute',
           'Engineering Center Energoservice']

setup(
    name='espmu',

    version=__version__,

    description='C37.118 (PMU) data parser',
    long_description='C37.118 (PMU) data parser',

    url='https://github.com/aleneus/espmu',

    author='; '.join(AUTHORS),
    author_email='aleneus@gmail.com',

    license='MIT',

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Interface Engine/Protocol Translator',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Environment :: MacOS X',
        'Environment :: Win32 (MS Windows)',
        'Environment :: Console'
    ],

    keywords='development PMU Phasor',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    install_requires=['pythoncrc'],
)
