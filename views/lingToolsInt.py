from flask import jsonify, request
from xml.etree import cElementTree as etree
import os
import time
import re
import sys

import praat
import utils
from praat import app

import subprocess
from flask import Flask
from flask_cors import CORS
from flask import send_from_directory
from flask import abort, send_file
from werkzeug import secure_filename
from shutil import copyfile
from pympi import Eaf
from pydub import AudioSegment
from pylab import *
import pympi
import datetime

@app.route('/link-elan-praat/<sound>/<startTime>/<endTime>')
def linkElanPraat(sound, start, end):

    print "I am inside link method"
    ## Prep input data 

    #Strip off letters after dot
    x = sound.index('.')
    nameoffile = sound[0:x] + "_" + str(datetime.datetime.now().microsecond)

    #Create a new EAF file
    filepath = praat._linkElanPraat_dir + nameoffile + ".eaf"
    startTime = int(start)
    endT = int(end)

    # Initialize the xml file
    eafob = pympi.Elan.Eaf()

    #Add linguistic type constraint - right now just one - Time_Subdivision
    ltcon = "Time_Subdivision"

    #prep variables for media descriptor
    soundpath = praat._sounds_dir + sound
    #soundpath_url = pathlib.Path(soundpath).as_uri()
    soundpath_url = pathlib.Path(soundpath)
    relpath = "./" + sound
    mimetype = "audio/" + sound[x+1:len(sound)]


    #set media descriptor
    if(soundpath != ""):
        eafob.add_linked_file(soundpath_url, relpath, mimetype)

    #add annotation to default tier
    if (tier == "default"):
        eafob.add_annotation(tier, startTime, endTime, textP)

    #Write the object to a file
    if(filepath != ""):
        eafob.to_file(filepath)
        appendto_xml(filepath, nameoffile)

    return "xml file created by the name: " + nameoffile


def appendto_xml(file_path, file_name, pretty=True):

    """Write an xml object to file.

    :param str file_path: Filepath to write to, - for stdout.
    :param str file_name: append to this file.
    :param bool pretty: Flag to set pretty printing.
    """

    adocument = {
        'AUTHOR': author,
        'VERSION': '2.8',
        'xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance',
    }

    # Annotation Document
    ADOCUMENT = etree.Element('COMBINED_DOCUMENT', eaf_obj.adocument)
