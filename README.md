# REST API for Praat and ELAN#

### To run locally on port 5000: ###
```
#!bash

python runLocal.py
```
### To run on port 80: ###
```
#!bash
sudo python run.py
```

### To run all tests: ###
```
#!bash
python test.py
```

### Praat installation ###
The directory praat is a submodule linked to the github repository for praat. If you do not wish to compile praat yourself, or have praat already installed on your computer, you may create a symbolic link to the praat executable inside the praat folder.
```

#!bash
cd praat
ln -s /path/to/praat praat
```
### Praat API Documentation ###
The API documentation is provided in static/praatapidocs.html. If you are running the server, visit /praatapidocs.

### ELAN installation ###
A python module for processing ELAN annotation files, pympi-ling 1.69, can be downloaded and installed from https://pypi.python.org/pypi/pympi-ling/. API documentation for any version can be found at http://dopefishh.github.io/pympi/Elan.html.


### ELAN API Documentation ###
The API documentation is provided in static/elanapidocs.html. If you are running the server, visit /elanapidocs.
