# AppBiopac-Python

A small script that can send BIOPAC data stream to [LabStreaming Layer](https://labstreaminglayer.readthedocs.io/info/intro.html).

## Usage

* Either edit the default config file (`config.ini`) or create your own based on the template
* Run `main.py`, using the `--cfg` switch if using a custom config file
* Press `Q` to stop the app

## Software requirements

* Windows
* Python >= 2.7
* pylsl

Also, you'll need to purchase and install the [BIOPAC Hardware API (BHAPI)](http://www.biopac.com/product/api-biopac-hardware/).

## Acknowledgments

This script heavily relies on [Ross Markello](https://github.com/rmarkello)'s [rtpeaks](https://github.com/rmarkello/rtpeaks), by using the `mpdev.py` API they developed.

## Disclaimers

BIOPAC is a trademark of BIOPAC Systems, Inc.
The authors of this software have no affiliation with BIOPAC Systems, Inc, and that company neither supports nor endorses this software package.
