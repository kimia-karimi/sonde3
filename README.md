# sonde3

> sonde3 is a python3 library for extracting and processing binary data from scientific environmental logging instruments.

sonde3 is a python3 port of the package [sonde](https://github.com/twdb/sonde) that was originally developed in 2010.  Sonde3 is a library for interacting with instrument data collected by scientific environmental data loggers (e.g., YSI, Hydrolab, Eureka, Greenspan).  sonde3 can auto-convert between raw, proprietary data formats, comma separated files, and Microsoft Excel.

Sonde3 is used principally to support water quality instrument files collected since 1986 by the Texas Water Development Board which is housed on the [Coastal Water Data for Texas website](https://waterdatafortexas.org/coastal). 

In addition to reading instrument data files sonde3 can help with creating uniformity across multiple instrument datasets.  Convert all your instrument files to similar units (e.g., report all datetimes as UTC, convert depth from feet to meters).  By using the seawater package, generate salinity (PSU) using the UNESCO 1981 and UNESCO 1983 (EOS-80) standards.  This is useful because salinity is calculated using different standards depending on the manufacturer of the instrument.  

## Team

  - __Lead Developer__: Evan Lee Turner
  - __Original Developer__: Dharhas Pothina
  - __Development Team Members__: Andy Wilson

## Table of Contents

1. [Usage](#usage)
1. [Requirements](#requirements)
1. [Development](#development)
    1. [Installing Dependencies](#installing-dependencies)
    1. [Tasks](#tasks)
1. [Team](#team)
1. [Contributing](#contributing)

## Requirements

- pandas
- seawater 3.3.4 (for salinity conversion)
- pytz (for timezone processing)
- Node (for unit tests)
- Sphynx (for documentation)


## Development

### Installing Dependencies

### Roadmap

## Contributing

