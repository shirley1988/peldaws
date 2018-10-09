from flask import jsonify, request, g
from flask_login import login_required

#from xml.etree import cElementTree as ET
import xml.etree.ElementTree as ET
import lxml.etree as etree
#from lxml import etree
from shutil import copyfile

import os
import time

import praat
import utils
from praat import app

## added from ElanLocal.py
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
import wave
import pympi
import datetime
import re
import sys
import pathlib
##


#################################################################################################
## added to test elan waveform individually

@app.route('/draw-elan/<sound>/<startTime>/<endTime>/')
@login_required
def drawElan(sound, startTime, endTime):

    #if(endTime<0)
    #resp = drawSound1(sound)

    showPitch = '0'

    # Script file
    script = praat._scripts_dir + "drawWaveform";

    # Parameters to the script
    params = [sound, startTime, endTime, showPitch,
             praat._sounds_dir, praat._images_dir];

    # Image name will be a combination of relevant params joined by a period.
    if "wav" not  in sound:
        image = praat._images_dir + str(sound.replace("mp3", "png"))
    else:
        image = praat._images_dir + str(sound.replace("wav", "png"))

    # Add image name to params list
    params.append(image)

    # If image does not exist, run script
    if not os.path.isfile(image):
       praat.runScript(script, params)
       utils.resizeImage(image)

    # Image should be available now, generated or cached
    resp = app.make_response(open(image).read())
    resp.content_type = "image/png"
    return resp

## Add a new annotation
@app.route('/annotation/<eaffilename>/<sound>/<ltype>/<start>/<end>/<text0>/<text1>/<text2>')
@login_required
def annotationTimeSelection(eaffilename, sound, ltype, start, end, text0, text1, text2):
    print "Saving annotation %s for sound %s" % (eaffilename, sound)
    extension = sound.split('.')[-1]

    s_filename = secure_filename(eaffilename)
    #Create a new EAF file
    _eaf_dir = get_eaf_dir(g.user, sound)
    utils.mkdir_p(_eaf_dir)
    filepath = _eaf_dir + s_filename + ".eaf"

    startTime = int(round(float(start)))
    endTime = int(round(float(end)))

    # Initialize the elan file
    eafob = pympi.Elan.Eaf()

    #Add linguistic type constraint - right now just one - Time_Subdivision
    ltcon = "Time_Subdivision"

    #prep variables for media descriptor
    soundpath = praat._sounds_dir + sound
    #soundpath_url = pathlib.Path(soundpath).as_uri()
    soundpath_url = pathlib.Path(soundpath)
    relpath = "./" + sound
    mimetype = "audio/" + extension

    #set media descriptor
    if(soundpath != ""):
        eafob.add_linked_file(soundpath_url, relpath, mimetype)

    defaulttier = "default"
    tier1 = "Tier1"
    tier2 = "Tier2"

    if (text0 != "undefined" and text1 != "undefined" and text2 != "undefined"):
        eafob.add_annotation(defaulttier, startTime, endTime, text0)
        eafob.add_linguistic_type(ltype, ltcon)
        eafob.add_tier(tier1)
        eafob.add_annotation(tier1, startTime, endTime, text1)
        eafob.add_tier(tier2, ltype, tier1)
        eafob.add_annotation(tier2, startTime, endTime, text2)
    elif (text0 != "undefined" and text1 != "undefined" and text2 == "undefined"):
        #eafob.add_tier(defaulttier)
        eafob.add_annotation(defaulttier, startTime, endTime, text0)
        eafob.add_linguistic_type(ltype, ltcon)
        eafob.add_tier(tier1)
        eafob.add_annotation(tier1, startTime, endTime, text1)
    elif (text0 != "undefined" and text1 == "undefined" and text2 == "undefined"):
        eafob.add_annotation(defaulttier, startTime, endTime, text0)

    #Write the object to a file
    #if(filepath != ""):

        #timeslot_list = list(eafob.timeslots.items())
        #indexes = [2,3]
        #t = []
        #for i in indexes:
            #t.append(timeslot_list[i])


        #print("The eaf object looks like: " + str(t))
        #eafob.to_file(filepath)
        #src = filepath
        #dst =  praat._linkElanPraat_dir + nameoffile + ".xml"
        #copyfile(src, dst)
        #appendto_xml(dst)

        #Call a function to print new ELAN image including annotation
        #resp = drawSound1(sound)
    eafob.to_file(filepath)
    xmlObject = etree.parse(filepath)
    eafstring = etree.tostring(xmlObject, pretty_print = True)
    #x = etree.parse(filename)
    #eafstring = etree.toString
    #eafstring = str(open(filepath,'r').read())
    #print("The eaf content is: "+ eafstring)
    return eafstring
    #return resp

#@app.route('/view-annotation/<sound>/<nameofeaf>')
#def viewAnnotation(sound, nameofeaf):


def getEafArray(subdir=None):
    """ Return list of available eafs as an array """
    if subdir is None:
        subdir = praat._eaf_dir
        #old_eaf = [f for f in os.listdir(praat._eaf_dir) if f.endswith('.eaf')]
        #print "All old eaf: " + str(old_eaf)
        #return old_eaf
    try:
        return [f for f in os.listdir(subdir) if f.endswith('.eaf')]
    except OSError:
        return []
    #return os.listdir(subdir)
    #return list(filter(lambda x : x.startswith(prefix), all_eaf))


def get_eaf_dir(user, sound):
    return os.path.join(praat._eaf_dir, user.current_group_id, utils.generate_id(str(sound)), '')


@app.route('/list-eafs/<sound>')
@login_required
def listEafs(sound):
    """ Get a list of sound files available, as a JSON String """
    print "List eafs for sound " + str(sound)
    subdir = get_eaf_dir(g.user, sound)
    print "List all eafs in " + subdir
    response = {
            "files": getEafArray(subdir)
    }
    return jsonify(response)

@app.route('/read-eaf/<sound>/<eaffilename>')
@login_required
def readEafs(sound, eaffilename):
    eaf_dir = get_eaf_dir(g.user, sound)
    nameoffile = eaffilename
    filepath = os.path.join(eaf_dir, nameoffile)
    xmlObject = etree.parse(filepath)
    eafstring = etree.tostring(xmlObject, pretty_print = True)
    return eafstring

## Temporarily added to display ELAN image separately on clicking view waveform
#@app.route('/draw-elan-sound/<sound>')
def drawSound1(sound):

    image = show_wave_n_spec(sound)

    print(image)
    utils.resizeImage(image)
    # Image should be available now, generated or cached
    resp = app.make_response(open(image).read())
    print(resp)
    #resp.content_type = "image/png"
    return send_file(image, mimetype='image/png')
    #return resp

## Method to display ELAN image
def show_wave_n_spec(speech):
    if "wav" not  in speech:
        speechmp3 = convert_mp3_to_wav(speech)
        spf = wave.open(speechmp3,'r')
        f = spf.getframerate()*2
        imagefile = praat._images_dir + str(speech.replace("mp3", "png"))
    else:
        speechfile = praat._sounds_dir + speech
        spf = wave.open(speechfile,'r')
        f = spf.getframerate()
        imagefile = praat._images_dir + str(speech.replace("wav", "png"))

    sound_info = spf.readframes(-1)
    sound_info = fromstring(sound_info, 'Int16')
    Time = linspace(0, len(sound_info)/f, num=len(sound_info))

    print("frame rate: "+ str(f))
    print("length of sound: "+str(len(sound_info)))
    print("stop: "+str(len(sound_info)/f))

    #subplot(211)
    plot(Time, sound_info, 'k')
    title('Wave form of %s' % speech)
    #plot([0,4], [-5550,-5550], 'b', lw=1)
    #axhline(-5050, xmin=0.25, xmax=0.75, color='k')
    axhspan(-5000,-6000, color='red', alpha=0.5, label='default')
    axhspan(-6000,-7000, color='grey', alpha=0.5, label='tier-1')
    axhspan(-7000,-8000, color='green', alpha=0.5, label='tier-2')
    legend(loc='upper right')

    print(imagefile)
    savefig(imagefile)
    #show()
    spf.close()
    return imagefile

## Convert mp3 to wav.. need to fix this
def convert_mp3_to_wav(input_sound):
    sound = AudioSegment.from_mp3 (praat._sounds_dir + input_sound)
    new_sound = praat._sounds_dir + "transform/" + input_sound.replace("mp3", "wav")
    sound.export(new_sound, format='wav')
    #print(new_sound)
    return new_sound

def appendto_xml(file_path, pretty=True):

    """Write an xml object to file.

    :param str file_path: Filepath to write to, - for stdout.
    :param str file_name: append to this file.
    :param bool pretty: Flag to set pretty printing.
    """

    EPtree = ET.parse(file_path)

    EProot = EPtree.getroot()
    print EProot
    type(EProot)
    list_EProot = EProot.getchildren()
    type(list_EProot)
    list_EProot
    childforpraat = ET.Element("PHONETICS")
    EPelement = EProot.append(childforpraat)
    ET.ElementTree(EProot).write(file_path)

    #EPelement_properties =EPelement.find('Properties')
    #EPelement_properties.attrib['typing'] = 'duck'

    praatdata = ET.SubElement(childforpraat, 'PRAAT_DATA')

    sound = ET.SubElement(praatdata, 'SOUND')
    soundenergy = ET.SubElement(sound, 'SOUND_ENERGY', energy='0.002112626523245126 Pa2 sec')

    pitch = ET.SubElement(praatdata, 'PITCH')
    voicedframes = ET.SubElement(pitch, 'PITCH_VOICED_FRAMES', count='226')
    getpvalattime = ET.SubElement(pitch, 'PITCH_AT_TIME')
    getpvalinframe = ET.SubElement(pitch, 'PITCH_IN_FRAME')

    spectrumdata = ET.SubElement(praatdata, 'SPECTRUM')
    getlowestfreq = ET.SubElement(spectrumdata, 'LOWEST_FREQUENCY', value='0 Hertz')
    gethighestfreq = ET.SubElement(spectrumdata, 'HIGHEST_FREQUENCY', value='8000 Hertz')

    intensity = ET.SubElement(praatdata, 'INTENSITY')
    getminintensity = ET.SubElement(intensity, 'MINIMUM_INTENSITY', value='37.36793761863101 dB')
    getmaxintensity = ET.SubElement(intensity, 'MAXIMUM_INTENSITY', value='68.96113475212057 dB')
    getmeanintensity = ET.SubElement(intensity, 'MEAN_INTENSITY', value='61.20009563626668 dB')

    formant = ET.SubElement(praatdata, 'INTENSITY')
    getnumframes = ET.SubElement(formant, 'NUMBER_OF_FRAMES', count='632')
    getnumformants = ET.SubElement(formant, 'NUMBER_OF_FORMANTS')
    getfvalattime = ET.SubElement(formant, 'FORMANT_AT_TIME')

    harmonicity = ET.SubElement(praatdata, 'HARMONICITY')
    getmin = ET.SubElement(harmonicity, 'MINIMUM_HARMONICITY')
    getmax = ET.SubElement(harmonicity, 'MAXIMUM_HARMONICITY')
    gethvalattime = ET.SubElement(harmonicity, 'HARMONICITY_AT_TIME')


    pointprocess = ET.SubElement(praatdata, 'POINT_PROCESS')
    getnumperiods = ET.SubElement(pointprocess, 'NUMBER_OF_PERIODS')
    getnumpoints = ET.SubElement(pointprocess, 'NUMBER_OF_POINTS', count='436')
    getjitterr = ET.SubElement(pointprocess, 'LOCAL_JITTER')



    django = ET.SubElement(praatdata, 'Django', type='Web Framework')

    #EPtree.write(file_path, pretty_print=True)
    if pretty:
        indent(childforpraat)

    EPtree.write(file_path,  encoding="utf-8", xml_declaration=True)

def indent(el, level=0):
    """Function to pretty print the xml, meaning adding tabs and newlines.

    :param ElementTree.Element el: Current element.
    :param int level: Current level.
    """
    i = '\n' + level * '\t'
    if len(el):
        if not el.text or not el.text.strip():
            el.text = i+'\t'
        if not el.tail or not el.tail.strip():
            el.tail = i
        for elem in el:
            indent(elem, level+1)
        if not el.tail or not el.tail.strip():
            el.tail = i
    else:
        if level and (not el.tail or not el.tail.strip()):
            el.tail = i

#####################################################################################################
