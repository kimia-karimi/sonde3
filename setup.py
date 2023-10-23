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
    version='3.11',
    license='BSD',
    author='Evan Turner',
    author_email='evan.turner@twdb.state.tx.us',
    description='A utility library for reading various water quality '
                'data formats',
    long_description=__doc__,
    keywords='sonde water quality format environment ysi',
    packages=find_packages(),
    include_package_data=True,
    platforms='any',
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
