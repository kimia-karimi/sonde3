"""
sonde3
-------
PySonde is a module for reading water quality data from various sensor
formats.
"""
from setuptools import Command, setup, find_packages

# note: the minimum version numbers are just what I know will work,
# but they could probably be a few versions lower
setup(
    name='sonde3',
    version='0.2',
    license='BSD',
    author='Evan Turner',
    author_email='evan.turner@twdb.state.tx.us',
    description='A utility library for reading various water quality '
                'data formats',
    long_description=__doc__,
    keywords='sonde water quality format environment ysi',
    packages=find_packages(),
    package_data={'': ['data/ysi_definitions.csv']},
    platforms='any',
    install_requires=[
        'pandas>=0.20.1',
        'pytz>=2010o',
        'seawater>=3.3.4',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Scientific/Engineering :: Interface Engine/Protocol Translator',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    tests_require=[
        'nose>=1.3.7',
        'configobj>=4.7.2',
    ],
    test_suite='nose.collector',
)
