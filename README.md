# sonde3

[![Binder](http://mybinder.org/badge.svg)](https://beta.mybinder.org/v2/gh/evanleeturner/sonde3/master)

.. image:: https://zenodo.org/badge/97947845.svg
   :target: https://zenodo.org/badge/latestdoi/97947845
   
   
> sonde3 is a python3 library for extracting and processing binary and text output data from scientific environmental logging instruments.

sonde3 is a python3 port of the package [sonde](https://github.com/twdb/sonde) that was originally developed in 2010.  Sonde3 is a library for interacting with instrument data collected by scientific environmental data loggers (e.g., YSI, Hydrolab, Eureka, Greenspan).  sonde3 can auto-convert between raw, proprietary data formats, comma separated files, and Microsoft Excel.

Sonde3 is used principally to support water quality instrument files collected since 1986 by the Texas Water Development Board which is housed on the [Coastal Water Data for Texas website](https://waterdatafortexas.org/coastal). 

In addition to reading instrument data files sonde3 can help with creating uniformity across multiple instrument datasets.  Convert all your instrument files to similar units (e.g., report all datetimes as UTC, convert depth from feet to meters).  By using the seawater package, generate salinity (PSU) using the UNESCO 1981 and UNESCO 1983 (EOS-80) standards.  This is useful because salinity is calculated using different standards depending on the manufacturer of the instrument.  

## Supported Instrument Formats

  - __YSI__: binary '*.dat', Comma Separated, ASCII-TXT
  - __Greenspan__: Microsoft Excel '*.xls', Comma Separated
  - __Eureka__: Microsoft Excel '*.xls', Comma Separated
  - __MacroCDT__: binary, Comma Separated
  - __Hydrolab__: Comma Separated
  - __Solinst__: Comma Separated
  - __Espey__: Comma Separated

## Team

  - __Lead Developer__: Evan Lee Turner
  - __Original Developer__: Dharhas Pothina
  - __Development Team Members__: Andy Wilson

## Requirements

- pandas
- seawater 3.3.4 (for salinity conversion)
- pytz (for timezone processing)
- Node (for unit tests)
- Sphynx (for documentation)


