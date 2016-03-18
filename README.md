# REST API for Praat #

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
The directory praat is a submodule linked to the github repository for praat. If you do not wish to
compile praat yourself, or have praat already installed on your computer, you may create a symbolic
link to the praat executable inside the praat folder.

```
#!bash
cd praat
ln -s /path/to/praat praat
```

### API Documentation ###
The API documentation is provided in static/apidocs.html. If you are running the server, visit /apidocs.