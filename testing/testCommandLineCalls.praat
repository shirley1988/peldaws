form Test command line calls
    sentence First_text I love you
    real Beep_duration 0.4
    sentence Second_text Me too
endform

writeInfoLine: "She: """, first_text$, """"
appendInfoLine: "He: """, second_text$, """"

synth1 = Create SpeechSynthesizer: "English", "f1"
Play text: first_text$
Create Sound as pure tone: "beep", 1, 0.0, beep_duration,
... 44100, 440, 0.2, 0.01, 0.01
Play
Remove
synth2 = Create SpeechSynthesizer: "English", "m1"
Play text: second_text$



Old annotationTimeSelection function:
@app.route('/annotation/time-selection/<sound>/<tier>/<childTier>/<ltype>/<start>/<end>/<textP>/<textC>')

0.0.0.0:5000/annotation/time-selection/Part2.mp3/TimeSubdivision-lt/9/14/tetst/undefined/undefined

0.0.0.0:5000/annotation/time-selection/Part2.mp3/TimeSubdivision-lt/9/14/tetst/test2/undefined

0.0.0.0:5000/annotation/time-selection/Part2.mp3/TimeSubdivision-lt/9/14/tetst/test2/test3

def annotationTimeSelection(sound, tier, childTier, ltype, start, end, textP, textC):

    #add annotation to default tier
    if (tier == "default"):
        eafob.add_annotation(tier, startTime, endTime, textP)
    #add annotation to single tier
    elif (tier != "default" and childTier == "default"):
        eafob.add_tier(tier)
        eafob.add_annotation(tier, startTime, endTime, textP)
    #add annotation to child tier
    elif (childTier != "default" and ltype == "TimeSubdivision-lt"):
        eafob.add_tier(tier)
        eafob.add_annotation(tier, startTime, endTime, textP)
        eafob.add_linguistic_type(ltype, ltcon)
        eafob.add_tier(childTier, ltype, tier)
        eafob.add_annotation(childTier,  startTime, endTime, textC)
