REST API for Praat

To run locally on port 5000:
   python runLocal.py

To run on port 80:
   sudo python run.py

To run all tests:
   python test.py

The directory praat is a submodule linked to the github repository for praat. If you do not wish to
compile praat yourself, or have praat already installed on your computer, you may create a symbolic
link to the praat executable inside the praat folder.

   cd praat
   ln -s /path/to/praat praat

