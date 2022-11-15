# -*- coding: utf-8 -*-
"""
Created on Mon Mar 14 10:42:27 2022

@author: moomi
"""

# -*- coding: utf-8 -*-
"""
Created on Sun Mar 13 12:52:02 2022

@author: moomi
"""
from nltk.tokenize.treebank import TreebankWordDetokenizer
from nltk.tokenize import sent_tokenize
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import moviepy
from moviepy.editor import *
import cv2
import numpy as np
import os
import pypandoc
import nltk
nltk.download('punkt')
import datetime
import string
import time
import re
import shutil
import itertools
import copy
import math
import re
from time import strftime
from time import gmtime
import json
from collections import Counter
from operator import itemgetter
WORD = re.compile(r"\w+")
regex = re.compile('$')
keyword_match=[]
frames = []
artifact_name=[]
keywords=[]
index_list=[]
word_line_section=[]
matches = []
medical_list=[]
keyword_list=[]
# Deletes output of previous executions.
def delete_output(dir):
    for filename in os.listdir(dir):
        file_path = os.path.join(dir, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))
            
def create_transcript_directory(transcript):
    transcript_directory = os.path.join('frames_output', transcript[:-16])
    try:
        os.mkdir(transcript_directory)
    except OSError:
        print("Creation of the directory %s failed" % transcript_directory)
    else:
        print("Successfully created the directory %s " % transcript_directory)

# tokenize sentences.
def sentence_tokenize_txt(file):
    read_text = open(file, "r", encoding="utf8").read()
    sentences = nltk.sent_tokenize(read_text)
    return sentences        
 # converts docx into a .txt file and returns the location of the new .txt file.
def format_sentences(sentences):
    sentence_list = []
    count = 0

    for sentence in sentences:
        if (count > 0):
            sentence = sentence.lower()
            sentence = sentence.replace('dr:', '')
            sentence = sentence.replace('pt:', '')
            sentence = sentence.replace('cmp:', '')
            sentence = sentence.replace('cmp1:', '')
            sentence = sentence.replace('cmp2:', '')
            sentence = sentence.replace('cmp3:', '')
            sentence = sentence.replace("'", '')
            sentence_list.append(sentence)
            # print(sentence)

        count = count + 1

    return sentence_list


# Gets rid of unwanted words.
def word_tokenize_txt(sentence):
    words = nltk.word_tokenize(sentence)
    return words


def convert_to_txt(transcript):
    transcript_input_name = os.path.join('transcript_input', transcript)
    transcript_name, _ = os.path.splitext(transcript)
    transcript_output = os.path.join('transcript_output', transcript_name)
    transcript_output_name = str(transcript_output) + ".txt"
    print("Converting: " + transcript_input_name +
          " into " + transcript_output_name)
    converted = pypandoc.convert_file(
        transcript_input_name, "plain", outputfile=transcript_output_name)
    assert converted == ""
    print("conversion is done ....")
    print("---------------------------------------")
    print(converted)
    return transcript_output_name


# checks if word is timestamp.
def check_timestamp(word):
    if word not in string.punctuation:

        if len(word) == 8:
            if word[0].isdigit():
                if word[1].isdigit():
                    if word[2] == ":":
                        if word[3].isdigit():
                            if word[4].isdigit():
                                if word[5] == ":":
                                    if word[6].isdigit():
                                        if word[7].isdigit():
                                            return True

    if len(word) == 7:
        if word[0].isdigit():
            if word[1] == ":":
                if word[2].isdigit():
                    if word[3].isdigit():
                        if word[4] == ":":
                            if word[5].isdigit():
                                if word[6].isdigit():
                                    return True

    if len(word) == 5:
        if word[0].isdigit():
            if word[1].isdigit():
                if word[2] == ":":
                    if word[3].isdigit():
                        if word[4].isdigit():
                            return True

    return False


def convert_to_seconds(w):
    if len(w) == 7 or len(w) == 8:
        timeobject = datetime.datetime.strptime(w, '%H:%M:%S').time()
        #print("this is timeobject",timeobject)
        hour = timeobject.hour
        minute = timeobject.minute
        second = timeobject.second
        total_seconds = (hour * 3600) + (minute * 60) + second
        #print("this is total seconds",total_seconds )
        return total_seconds

    else:
        timeobject = datetime.datetime.strptime(w, '%M:%S').time()
        minute = timeobject.minute
        second = timeobject.second
        total_seconds = (minute * 60) + second
        #print(total_seconds )
        return total_seconds



# creates individual lists from transcripts containing known timestamps
def find_timetamps(sentences, transcript):

    timestamps = []
    start_time = "0:00:00"
    transcript_sections = []
    tmp = []
    tmp_timestamp = "0:00:00"
    tmp.append(start_time)
    for sentence in sentences:
        words = word_tokenize_txt(sentence)
        #print(words)
        for w in words:
            #print(w)
            if (check_timestamp(w) == True):

                if (convert_to_seconds(w) < convert_to_seconds(tmp_timestamp)):

                    t1 = convert_to_seconds(w)
                    #print("This is t1 ",t1)
                    t2 = convert_to_seconds(tmp_timestamp)
                    #print("This is t2", t2)
                    t3 = t1 + t2
                    #print("This is t2",t3)
                    new_timestamp = strftime("%H:%M:%S", gmtime(t3))
                    tmp.append(new_timestamp)
                    tmp_copy = copy.deepcopy(tmp)
                    transcript_sections.append(tmp_copy)
                    tmp = []
                    tmp.append(new_timestamp)

                else:
                    tmp.append(w)
                   # print("incase timestamp is greater",tmp)
                    tmp_copy = copy.deepcopy(tmp)
                   # print("this is tmpcopy",tmp_copy)
                    transcript_sections.append(tmp_copy)
                    #print("this is transcriptsections",transcript_sections)
                    tmp = []
                    tmp.append(w)
                    #print("a new tmp",tmp)
                    tmp_timestamp = w
                    #print("a new tmp_timesstamp",tmp_timestamp)

            else:
                if w not in string.punctuation:
                    tmp.append(w)
                    #print(tmp)

    video_name = transcript[:-16]
    video_name = video_name.replace("_", " ")
    video_name = video_name.replace("_", " ")
    video_name = video_name + "_Deidentified.mp4"
    video_path = os.path.join('videos', video_name)
    video = cv2.VideoCapture(video_path)
    fps = video.get(cv2.CAP_PROP_FPS)  # gets fps of the Video.
    tns = video.get(cv2.CAP_PROP_FRAME_COUNT)  # get total number of frames

    if (float(fps) != 0.0):
        duration = float(tns)/float(fps)

    else:
        duration = video.get(cv2.CAP_PROP_POS_MSEC)

    end_time = strftime("%H:%M:%S", gmtime(duration))

    tmp.append(end_time)
    transcript_sections.append(tmp)
    return transcript_sections
def calculate_time_frame(time, framerate):
    hour = time // 3600
    minute = (time % 3600) // 60
    second = time % 60
    specific_frame = (hour*3600+minute*60+second)*framerate
    return int(specific_frame)

def word_said_per_second(list):
    duration = convert_to_seconds(list[-1]) - convert_to_seconds(list[0])
    wsps = 0
    list = list[1:-1]

    if (duration > 0):
        wsps = duration/len(list)

    return wsps

def regx_matching(transcript_sections):
    match=False 
    for sections in transcript_sections:
         line=' '.join([str(item) for item in sections])
         aus_stheoscope = re.search( r'\b(all\sin\sthis\sthing)\b|\b(big)(?=\sbreath\sin)(\s\w+){2}\b|\b(big)(?=\sbreath\sin,\sand\sout)(\s\w+){4}\b|\b((deep)(?=\sbreaths\s))(\s\w+){1}\b|\b((deep)(?=\sbreath\sin))(\s\w+){2}\b|\b((breath)(?=\sin))(\s\w+){1}\b|\b(In,\sand\sout)\b|\b(listen(?=\sto\syour\s(chest|heart|back|lungs)))(\s\w+){3}|\b(listen(?=\s(here|to)))(\s\w+){1}\b|\b(listen(?=\sat\sthe\sback))(\s\w+){3}\b|\b(your(?=\schest))(\s\w+){1}\b|\b(lift(?=\sit))(\s\w+){1}\b|\b(lift(?=\sup\syour\sshirt))(\s\w+){3}\b|\bjust(?=\sgonna\slisten\sto\syour\sheart)(\s\w+){5}\b|\b(here\swe\sgo)\b|\b(heart(?=\smurmur))(\s\w+){2}\b|\b(have(?=\sa\slisten))(\s\w+){3}\b|\b(have(?=\sa\slisten\sto\sthe\sback))(\s\w+){5}\b|\bgonna(?=\slisten\sto\syour\sheart)(\s\w+){4}\b|\b(examine(?=\syou))(\s\w+){1}\b|\b(check(?=\syou\sover))(\s\w+){2}\b',line, re.M|re.I)
         if  aus_stheoscope:
             print ("aus_stheoscope is found : ", aus_stheoscope.group())  
             keywords.append("aus_stheoscope")
             keywords.append(aus_stheoscope.group())
         biochemical_testing =re.search( r'\b(chloestral)(?=\stest)(\s\w+){1}\b|\binject\b|\bCBT\b|\b(prostate)(?=\sspecific\santigen)(\s\w+){2}\b|\b(hameoglobin)(?=\sA1C\sform)(\s\w+){2}\b|\b(kidney|liver|fasting|smear|haemoglobin|blood)(?=\stest)(\s\w+){1}\b|\b(fasting)(?=\sblood\stest)(\s\w+){2}\b|\b(cardiovascular)(?=\srisk\sfactor\blood)(\s\w+){2}\b|\b(breast)(?=\sscreening\stest)(\s\w+){2}\b|\b(depo)(?=\sinjection)(\s\w+){1}\b|\b(this)(?=\sis\syour\sblood\stest)(\s\w+){4}\b|\b(B12)(?=\sform)(\s\w+){1}\b|\b(asthma)(?=\scheck)(\s\w+){1}\b|\bbloods\b|\b(swab)(?=\sform\syour\sear)(\s\w+){3}\b|\b(cholestral)(?=\sthat\sis\sraised)(\s\w+){3}\b|\b(blood)(?=\ssugar)(\s\w+){1}\b|\bswab\b|\bthryoid\shormone\stest\b',line, re.M|re.I)
         if biochemical_testing:
             print ("biochemical_testing is found : ",biochemical_testing.group())
             keywords.append("biochemical_testing")
             keywords.append(biochemical_testing.group())
         bed =re.search( r' \b(lie)(?=\sdown\son\sthe\sbed\sfor\sme)(\s\w+){6}\b|\bbed\b|\b(laying)(?=\sdown)(\s\w+){1}\b|\b(across)(?=\sto\sthat\sbade)(\s\w+){3}\b|\b(come)(?=\sacross\sto\sthat\sbed\sfor\sme)(\s\w+){6}\b|\b(lie)(?=\sdown\sfor\sme)(\s\w+){3}\b',line, re.M|re.I)
         if bed:
             print ("bed is found : ",bed.group())
             keywords.append("bed")
             keywords.append(bed.group())
         blood_Pressure =re.search( r'\b(can)(?=\si\sjust\scheck\syour\sblood\spressure)(\s\w+){6}\b|\b(let)(.s)(?=\sdo\sthis)(\s\w+){2}\b|\b(blood)(?=\spressure)(\s\w+){1}\b|\b(just)(?=\sdo\syour\sblood\spressure)(\s\w+){4}\b|\b(gonna)(?=\sdo\syour\sblood\spressure\sand\syour\sheart\srate)(\s\w+){8}\b|\bpulse\b|\b(place)(?=\sit\son\syour\sarm)(\s\w+){4}\b|\b(blood)(?=\spressure\scheck)(\s\w+){2}\b|\b(just)(?=\sdo\syour\sblood\spressure)(\s\w+){4}\b|\b(gonna)(?=\sdo\syour\sblood\spressure\sand\syour\sheart\srate)(\s\w+){8}\b|\bpulse\b|\b(place)(?=\sit\son\syour\sarm)(\s\w+){4}\b|\b(blood)(?=\spressure\scheck)(\s\w+){2}\b|\b(check)(?=\syour\spulse)(\s\w+){2}\b|\b(just)(?=\srelax)(\s\w+){1}\b|\b(if)(?=\syou\sjust\spull\sthis\sup)(\s\w+){5}\b|\b(heart)(?=\srate)(\s\w+){1}\b|\b(let)(?=\sme\sdo\syour\sblood\spressure\sfirst)(\s\w+){6}\b|\b(check)(?=\syour\sblood\spressure\sagain)(\s\w+){4}\b|\b(straighten)(?=\syour\sarm)(\s\w+){2}\b|\b(within)(?=\sthe\sthresholds)(\s\w+){2}\b|\b(can)(?=\si\sjust\scheck\syour\sblood\spressure)(\s\w+){6}\b|\b(check)(?=\syour\sblood\spressure)(\s\w+){3}\b|\b(blood)(?=\spressure\smonitor)(\s\w+){2}\b|\b(let)(?=\sme\sdo\syour\sblood\spressure)(\s\w+){5}\b|\b(you)(?=\sto\sdo\smy\sblood\spressure)(\s\w+){5}\b',line, re.M|re.I)
         if blood_Pressure:
             print ("blood_Pressure is found : ",blood_Pressure.group())
             keywords.append("blood_Pressure")
             keywords.append(blood_Pressure.group())
         computer =re.search( r'\b(have)(?=\syou\sgot\sa\slandline)(\s\w+){4}\b|\blandline\b|\bcomputer\b|\b(send)(?=\sa\smessage)(\s\w+){3}\b|\b(have)(?=\sfor\syou\son\sfile)(\s\w+){4}\b|\b(make)(?=\sa\snote)(\s\w+){2}\b|\b(arrange)(?=\sfor\syou)(\s\w+){2}\b|\b(let)(?=\sme\sjust\smake\sa\snote)(\s\w+){5}\b|\b(show)(?=\syour\sresults\shere)(\s\w+){3}\b|\b(send)(?=\s(me|us)\sa\smessage)(\s\w+){3}\b|\bfile\b',line, re.M|re.I)
         if computer:
             print ("computer is found : ",computer.group())
             keywords.append("computer")
             keywords.append(computer.group())
         CTP_SCAN =re.search( r'\b(have)(?=\sa\sCT\sscan)(\s\w+){3}\b|\b(CT)(?=\sscan)(\s\w+){1}\b',line, re.M|re.I) 
         if CTP_SCAN:
             print ("CTP_SCAN is found : ",CTP_SCAN.group())
             keywords.append("CTP_SCAN")
             keywords.append(CTP_SCAN.group())
         ECG =re.search( r'\b(ECG|ECG\stest|form\sto\shave\san\sECG)\b ',line, re.M|re.I)
         if ECG:
             print ("ECG is found : ",ECG.group())
             keywords.append("ECG")
             keywords.append(ECG.group())
         Glucometer =re.search( r'\b(been)(?=\schecking\syour\sblood\ssugar)(\s\w+){4}\b|\b(can)(?=\sI\shave\sa\sfinger)(\s\w+){4}\b|\b(reading)(?=\sup\sto\s11\sis\snormal)(\s\w+){5}\b|\b(checked)(?=\syour\ssugars)(\s\w+){2}\b',line, re.M|re.I)
         if Glucometer :
             print ("Glucometer is found : ",Glucometer.group())
             keywords.append("Glucometer")
             keywords.append(Glucometer.group())
         ENT =re.search( r'\b(back)(?=\sof\s(her|your)\sthroart)(\s\w+){3}\b|\bENT\b|\b(let)(?=\sme\sjust\scheck\sthe\sglands)(\s\w+){5}\b|\b(look)(?=\sat\sback\sof\s(her|your)\sthroart)(\s\w+){5}\b|\b(can)(?=\sI\slook\sin\syour\sgood\sear\sfirst)(\s\w+){7}\b|\b(looked)(?=\sfor\sawhile)(\s\w+){2}\b|\b(feel)(?=\sthe\sglands\sin\syour\sneck)(\s\w+){5}\b|\b(can)(?=\syou\sjust\sopen\syour\smouth\sfor\sme)(\s\w+){7}\b|\bAH\b|\b(look)(?=\sin\s(the|your)\sears)(\s\w+){3}\b|\b(pop)(?=\syour\stongue\sout)(\s\w+){3}\b|\bstick\b|\b(breath)(?=\sthrough\smouth)(\s\w+){2}\b|\b(open)(?=\syour\smouth)(\s\w+){2}\b|\b(have)(?=\sa\slook\sin\s(your|her)\sears)(\s\w+){5}\b',line, re.M|re.I)
         if ENT:
             print ("ENT is found : ", ENT.group())
             keywords.append("ENT")
             keywords.append(ENT.group())
         Form_Pen_Papers=re.search( r'\b(that)(.s)(?=\s(for\syou|the\sform))(\s\w+){2}\b|\b(I)(.ll)(?=\sput\sit\son\syour\srepeat\sprescription)(\s\w+){6}\b|\b(according)(?=\sto\sthis)(\s\w+){2}\b|\b(add)(?=\sin\sreferral)(\s\w+){2}\b|\b(all)(?=\sin\sthis)(\s\w+){2}\b|\b(blood)(?=\s(form|tests))(\s\w+){1}\b|\b(book)(?=\s(an\sappointment|your\sfollow\sup\sappointment))(\s\w+){4}\b|\bcertificates\b|\b(come)(?=\sback)(\s\w+){1}\b|\b(consultant)(?=\sgave\sme\sa\sprescription)(\s\w+){4}\b|\b(do)(?=\syou\sneed\sto\shave\sany)(\s\w+){5}\b|\b(fill)(?=\sthat\sform\sin)(\s\w+){3}\b|\bform\b|\b(general)(?=\sprescription)(\s\w+){1}\b|\b(get)(?=\s(a\sletter|some\sblood\stests\sdone|you\sa\sa\sreferral))(\s\w+){4}\b|\b(general)(?=\sprescription)(\s\w+){1}\b|\b(give)(?=\s(it\sto\syou\snow|this\sa\sgo|this\sto\sthe\sfront\sdesk|you\sa\sreferral\sletter))(\s\w+){5}\b|\b(gonna)(?=\s(give\syou|give\syou\sa\sblood\sform))(\s\w+){5}\b|\b(green)(?=\sform)(\s\w+){1}\b|\b(have)(?=\sa\slook\sthere)(\s\w+){3}\b|\b(hope)(?=\sit\sgoes\sthrough\sfor\syou)(\s\w+){5}\b|\b(I)(?=\sgot\san\sappointment)(\s\w+){3}\b|\b(leave)(?=\sthis\swith\syou)(\s\w+){3}\b|\b(let)(?=\sme\sput\sit\sthis\sway)(\s\w+){5}\b|\bletter\b|\b(look)(?=\sat\sthe\sresults)(\s\w+){3}\b|\b(need)(?=\sa\sprescription\sfor\scontraception)(\s\w+){4}\b|\b(on)(?=\sa\srepeat\sprescription)(\s\w+){3}\b|\b(on)(?=\sto\sget\syour)(\s\w+){3}\b|\b(organise)(?=\sthe\sreferral)(\s\w+){2}\b|\b(pop)(?=\sthat\sout\sto\sthe\sdispensary)(\s\w+){5}\b|\b(prescription|prescriptions)\b\b(put)(?=\sit\son\syour\srepeat\sprescription)(\s\w+){5}\b|\b(put)(?=\sthis\saway)(\s\w+){2}\b|\b(refer)(?=\syou)(\s\w+){1}\b|\b(referral|review)\b|\b(repeat)(?=\s(pescription|prescription))(\s\w+){2}\b|\b(see)(?=\swhat\sthis\sis\sdoing)(\s\w+){4}\b|\b(self-)(?=\s(referral\snumber))(\s\w+){2}\b|\b(send)(?=\sme\stablet)(\s\w+){2}\b|\b(shall)(?=\si\ssend\sthe)(\s\w+){3}\b|\b(sick)(?=\snote)(\s\w+){1}\b|\b(sign)(?=\sit\shere)(\s\w+){2}\b|\b(some)(?=\sinstructions)(\s\w+){1}\b|\bstretches\b|\b(swap)(?=\sthis\swith\sthis)(\s\w+){3}\b|\b(take)(?=\s(care|that))(\s\w+){1}\b|\b(thank)(?=\syou\sfor\sthat)(\s\w+){3}\b|\b(thats)(?=\sthe)(\s\w+){1}\b|\b(the)(?=\sreferral)(\s\w+){1}\b|\b(there)(?=\s(are\sthe|we\sgo|you\sgo))(\s\w+){2}\b|\b(thank)(?=\syou\sfor\sthat)(\s\w+){3}\b|\b(this)(?=\sis\sthe\santibiotic\seardrop)(\s\w+){4}\b|\b(those)(?=\sare\sthe\sexercises)(\s\w+){3}\b|\b(three)(?=\stimes\sa\sday)(\s\w+){3}\b|\b(see)(?=\syou)(\s\w+){1}\b|\b(to)(?=\s(put\sthat\sin|the\sdispensary))(\s\w+){3}\b\b(try)(?=\s(popping\sthis\son|that\smorning\sand\snight))(\s\w+){4}\b|\b(try)(?=\sthat)(\s\w+){1}\b|\b(two)(?=\stablets\sa\sday)(\s\w+){3}\b|\bwritten\b|\b(written)(?=\s(on\syour|you))(\s\w+){2}\b|\b(written)(?=\syou\ssome\sinstructions)(\s\w+){3}\b',line, re.M|re.I)
         if Form_Pen_Papers:
             print ("Form_Pen_Papers is found : ",Form_Pen_Papers.group())
             keywords.append("Form_Pen_Papers")
             keywords.append(Form_Pen_Papers.group())
         Magnify_Glass=re.search( r'\b(it)(?=\sjust\slooks)(\s\w+){2}\b',line, re.M|re.I)
         if Magnify_Glass:
             print (" Magnify_Glass is found : ",Magnify_Glass.group())
             keywords.append("Magnify_Glass")
             keywords.append(Magnify_Glass.group())
         MRI_Scan=re.search( r'\b(after)(?=\sthe\sMRI\sscan)(\s\w+){3}\b|\b(reading)(?=\sMRI\sscan)(\s\w+){2}\b|\b(MRI)(?=\sscan)(\s\w+){1}\b',line, re.M|re.I)
         if MRI_Scan:
             print ("MRI_Scan is found : ",MRI_Scan.group())
             keywords.append("MRI_Scan")
             keywords.append(MRI_Scan.group())
         Patients_Medication=re.search( r'\b(your)(?=\s(antibiotics|painkillers))(\s\w+){1}\b|\b(that)(.s)(?=\s(antibiotics|painkillers))(\s\w+){1}\b|\b(Let)(.s)(?=\ssee\syour\sblood\spressure)(\s\w+){4}\b|\b(brought)(?=\s(back|me|me\sthingy))(\s\w+){2}\b|\b(changed)(?=\sthat)(\s\w+){1}\b|\b(got)(?=\s(my\smedication\shere|printed\sout))(\s\w+){3}\b|\b(have)(?=\syou\sgot\sa\scopy)(\s\w+){4}\b|\b(I)(?=\swas\sput\son)(\s\w+){3}\b|\blist\b|\b(make)(?=\sthe\scomplete\srecord)(\s\w+){3}\b|\b(mobile)(?=\shere)(\s\w+){1}\b|\b(print|printed)(?=\sout)(\s\w+){1}\b|\b(put)(?=\sthat\son\syour\srecord)(\s\w+){4}\b|\b(put)(?=\sthat\son\syour\srecord)(\s\w+){4}\b|\b(started)(?=\s(me\son|me\son\sthis))(\s\w+){3}\b|\btablet\b|\b(taking)(?=\sthem\stablets)(\s\w+){2}\b|\b(theres)(?=\s(a\slist|the\slist))(\s\w+){2}\b|\b(they)(?=\schanged\sthat)(\s\w+){2}\b|\b(this)(?=\sis\sthe\smedication)(\s\w+){3}\b|\b(took)(?=\sthe\sdata)(\s\w+){2}\b|\b(was)(?=\sput\son)(\s\w+){2}\b|\b(complete)(?=\srecord)(\s\w+){1}\b|\b(take)(?=\sthese\stablets\son\san\sempty\sstomach)(\s\w+){6}\b|\b(glucose)(?=\slevel\sincreased)(\s\w+){2}\b|\brecord\b|\b(brought)(?=\smy)(\s\w+){1}\b|\b(problem)(?=\swith\smedication)(\s\w+){2}\b|\b(blood)(?=\stest\sexcellent)(\s\w+){2}\b|\b(smear)(?=\sresult\sreport)(\s\w+){2}\b|\bmammogram\b|\b(asthma)(?=\spump)(\s\w+){1}\b|\b(spacer)(?=\sand\sinhaler)(\s\w+){2}\b|\b(which)(?=\sone\shave\syou\sgot)(\s\w+){4}\b',line, re.M|re.I)
         if Patients_Medication:
             print ("Patients_Medication is found : ",Patients_Medication.group())
             keywords.append("Patients_Medication")
             keywords.append(Patients_Medication.group())
         Peak_Flow=re.search( r'\b(done)(?=\syour\speak\sflow)(\s\w+){3}\b|\b(big)(?=\sbreath)(\s\w+){1}\b|\b(blowing)(?=\stest)(\s\w+){1}\b|\b(Pop)(?=\sit\sinto\syour\smouth)(\s\w+){4}\b|\b(peak)(?=\sflow)(\s\w+){1}\b|\b(big)(?=\sbreath\sin)(\s\w+){2}\b',line, re.M|re.I)
         if Peak_Flow:
             print ("Peak_Flow is found : ",Peak_Flow.group())
             keywords.append("Peak_Flow")
             keywords.append(Peak_Flow.group())
         Physical_Examination =re.search( r'\bthat(.s)\swhere\syou\sfeel\spain\b|\bthat(.s)\swhere\b|\bthere(.s)\sa\sbit\sof\sswelling\sthere\b|\bso\syou(.re)\stender\b|\b(let)(.s)(?=\shave\sa\slook\sat\syour\swrists)(\s\w+){6}\b|\b(let)(.s)(?=\shave\sa\slook)(\s\w+){3}\b|\b(let)(?=\shave\sa\slook)(\s\w+){3}\b|\bbit(.s)\sthere\b|\bi(.m)\sgonna\sask\syou\sto\sdo\ssome\smovements\b|\b(how)(?=\smuch\scan\syou\sbend\sthis\sknee)(\s\w+){6}\b|\b(right)(?=\sthere)(\s\w+){1}\b|\b(show)(?=\sme\sexactly\swhere\sit\sis)(\s\w+){5}\b|\b(able)(?=\sto(\sbend|\stry\sand\sbend))(\s\w+){5}\b|\b(about)(?=\shere)(\s\w+){1}\b|\b(across)(?=\sthe\sbed)(\s\w+){2}\b|\b(all)(?=\stensing\sup\shere)(\s\w+){3}\b|\barea\b|\b(around)(?=\s(here|there))(\s\w+){1}\b|\b(behind)(?=\s(curtain|scurtian))(\s\w+){1}\b|\b(bend)(?=\s(this|your)\sknee)(\s\w+){2}\b|\b(blown)(?=\sup\sthere)(\s\w+){2}\b|\b(bottom)(?=\sof\syour\sfeet)(\s\w+){3}\b|\b(can)(?=\ssee)(\s\w+){1}\b|\b(can)(?=\s(you\sfeel|I\scheck))(\s\w+){2}\b|\b(can\sI)(?=\sget\syou\sstanding\sup\sfor\sme)(\s\w+){6}\b|\b(can\sI)(?=\sgrip\syour\shand)(\s\w+){3}\b|\b(can\sI)(?=\sjust\sexamine\syour\stummy)(\s\w+){4}\b|\b(can\syou)(?=\sbring\sthis\sleg\sup)(\s\w+){4}\b|\b(can\syou)(?=\sfeel\sthat)(\s\w+){2}\b|\b(can\syou)(?=\ssqueeze\smy\shand)(\s\w+){2}\b|\b(check)(?=\sthe\sother\sfoot)(\s\w+){3}\b|\b(check)(?=\syour)(\s\w+){1}\b|\b(crossed)(?=\sover)(\s\w+){1}\b|\bcurtian\b|\b(does)(?=\sthat\shurt)(\s\w+){2}\b|\b(down)(?=\sthis\sside)(\s\w+){2}\b|\bexamination\b|\b(examine)(?=\sme\sjust\sthere)(\s\w+){3}\b|\b(examine)(?=\syour)(\s\w+){1}\b|\b(examine)(?=\syour\s(back|brest))(\s\w+){2}\b|\bexamining\b|\b(feel)(?=\sthat)(\s\w+){2}\b|\b(fine)(?=\sthere)(\s\w+){1}\b|\b(from)(?=\shere\sdown)(\s\w+){2}\b|\b(going)(?=\sto\sput\smy\sthumb\swhere\sit\sis)(\s\w+){7}\b|\b(have)(?=\sa\slook)(\s\w+){2}\b|\b(have)(?=\sa\slook\sat\syou)(\s\w+){4}\b|\b(have)(?=\sa\slook\sin\syour\sears)(\s\w+){5}\b|\b(have)(?=\sa\slook\sthen)(\s\w+){3}\b|\b(have)(?=\syour\sleg)(\s\w+){2}\b|\bhere\b|\b(how)(?=\sfar\sforward)(\s\w+){2}\b|\b(how)(?=\slong\shas\sit\sbeen\sthere)(\s\w+){5}\b|\b(I)(?=\scan\sfeel\sthat)(\s\w+){3}\b|\b(I)(?=\scan\sfeel)(\s\w+){2}\b|\b(I)(?=\sjust\swant\sto\slook\sat\sthis\sone)(\s\w+){7}\b|\b(if)(?=\si\sexamine)(\s\w+){2}\b|\b(if)(?=\si\sget\syou\sto\sbend\syour\sknee)(\s\w+){7}\b|\b(is)(?=\sthat\spainful)(\s\w+){2}\b|\b(just)(?=\shave\sto\scheck\ssome)(\s\w+){4}\b|\b(just)(?=\s(here|there))(\s\w+){1}\b|\b(lay)(?=\sdown)(\s\w+){1}\b|\b(let)(?=\sme\shave\sa\slook)(\s\w+){4}\b|\b(let)(?=\sme\slook)(\s\w+){2}\b|\b(let)(?=\sme\sput\smy\sfinger\son\sit)(\s\w+){6}\b|\b(lets)(?=\shave\sa\slook\sat\syour)(\s\w+){5}\b|\b(like)(?=\sa\ssuspension\sbridge)(\s\w+){3}\b|\b(little)(?=\slook)(\s\w+){1}\b|\b(lie)(?=\sdown)(\s\w+){1}\b|\b(look)(?=\sat)(\s\w+){1}\b|\b(look)(?=\sat\syour)(\s\w+){1}\b|\b(look)(?=\slike\sanything)(\s\w+){2}\b|\b(look)(?=\sthis\sway)(\s\w+){2}\b|\b(not)(?=\s(tender|there))(\s\w+){1}\b|\b(okay)(?=\scould\syou\sdo\sthis\sfor\sme)(\s\w+){6}\b|\b(on)(?=\sthe\sbed)(\s\w+){2}\b|\b(pain|past)(?=\sthere)(\s\w+){1}\b|\b(point)(?=\sin\smy)(\s\w+){2}\b|\b(pop)(?=\syou)(\s\w+){1}\b|\b(pop)(?=\syou\sbehind\sthe\s(curtain|curtian))(\s\w+){4}\b|\b(pop)(?=\syour)(\s\w+){1}\b|\b(pop)(?=\syour\schin\sto\syour\schest\sfor\sme\sand\sthen\sup\sto\sthe\ssky)(\s\w+){13}\b|\b(pop)(?=\syour\s(jacket|shirt)\soff)(\s\w+){3}\b|\bpressing\b|\b(pull)(?=\s(that|the)\s(curtain|curtian))(\s\w+){2}\b|\brelax\b|\b(right)(?=\sthere)(\s\w+){1}\b|\bsensation\b|\b(show)(?=\syou\swhere)(\s\w+){2}\b|\b(shut)(?=\sthat\soff)(\s\w+){2}\b|\b(sit)(?=\sup\sthere)(\s\w+){2}\b|\b(stand)(?=\sup)(\s\w+){1}\b|\b(stand)(?=\sup\sfor\sme)(\s\w+){3}\b|\bstraighten\b|\b(stretch)(?=\syour)(\s\w+){1}\b|\b(take)(?=\sthe\spressure\soff\syour\ship)(\s\w+){5}\b|\btender\b|\b(tender)(?=\sthere)(\s\w+){1}\b|\b(test)(?=\sfor\sthe\spower)(\s\w+){3}\b|\b(the)(?=\sbit\sthere)(\s\w+){2}\b|\b(This)(?=\s(bit|one|area))(\s\w+){1}\b|\b(your)(?=\sother\sknee)(\s\w+){2}\b|\b(this)(?=\stendon\shere)(\s\w+){2}\b|\b(under|up)(?=\shere)(\s\w+){1}\b|\b(very)(?=\stender)(\s\w+){1}\b|\bwhereabouts\b|\b(which)(?=\sbits\sare\sbothering\syou)(\s\w+){4}\b|\b(which)(?=\sone\sis\sthe\sworse\sone)(\s\w+){5}\b|\b(would)(?=\sit\sbe\sokay\sif\si\sexamined\syou)(\s\w+){7}\b|\b(your)(?=\s(brest|pulse))(\s\w+){1}\b',line, re.M|re.I)
         if Physical_Examination:
             print ("Physical_Examination is found : ",Physical_Examination.group())
             keywords.append("Physical_Examination")
             keywords.append(Physical_Examination.group())
         Questionaire =re.search( r'\b(that)(.s)(?=\syours)(\s\w+){1}\b|\b(that)(.s)(?=\s(for\syou))(\s\w+){2}\b|\b(I)(?=\sneed\sto\sdo\sthis)(\s\w+){4}\b|\b(need)(?=\sto\sdo\sthis)(\s\w+){3}\b|\bthank\syou\b',line, re.M|re.I)
         if Questionaire:
             print ("Questionaire is found : ",Questionaire.group())
             keywords.append("Questionaire")
             keywords.append(Questionaire.group())
         Samples_Pot =re.search( r'\b(sputum)(?=\ssample)(\s\w+){1}\b|\b(sample)(?=\sof\swee)(\s\w+){2}\b|\b(give)(?=\syou\ssome\spots)(\s\w+){3}\b|\b(get)(?=\sthe\sbottle\sfor\syou)(\s\w+){4}\b|\b(leave)(?=\sat\sfront\sdesk)(\s\w+){3}\b|\b(if)(?=\syou\scan\sdo\sthat)(\s\w+){4}\b|\b(bottle)(?=\sfor\syou)(\s\w+){3}\b',line, re.M|re.I)
         if Samples_Pot:
             print ("Samples_Pot is found : ",Samples_Pot.group())
             keywords.append("Samples_Pot")
             keywords.append(Samples_Pot.group())
         Spirometer =re.search( r'\b(blow)(?=\suntil)(\s\w+){1}\b|\b(take)(?=\sa\sbig\sbreath)(\s\w+){3}\b',line, re.M|re.I)
         if Spirometer :
             print (" Spirometer  is found : ",Spirometer .group())
             keywords.append("Spirometer")
             keywords.append(Spirometer.group())
         Spo2 =re.search( r'\b(your)(?=\sfinger)(\s\w+){1}\b|\b(got)(?=\sto\slook\sat\syour\spulse\srate)(\s\w+){6}\b|\bspO2\b|\bsaturation\b|\b(oxygen)(?=\ssaturation)(\s\w+){1}\b|\b(pop)(?=\s(this|that|it)\son\syour\sfinger)(\s\w+){4}\b|\b(pop)(?=\s(this|that)\son)(\s\w+){2}\b|\b(Can)(?=\si\spop\sthis\son\syour\sfinger)(\s\w+){6}\b',line, re.M|re.I)
         if Spo2:
             print ("Spo2 is found : ",Spo2.group())
             keywords.append("Spo2")
             keywords.append(Spo2.group())
         Support_Brace =re.search( r'\b(support)(?=\sbrace)(\s\w+){1}\b|\b(wrist)(?=\ssupport)(\s\w+){1}\b|\bsupport\b|\b(wear)(?=\sa\sknee\ssupport)(\s\w+){3}\b ',line, re.M|re.I)
         if Support_Brace:
             print ("Support_Brace is found : ",Support_Brace.group())
             keywords.append("Support_Brace")
             keywords.append(Support_Brace.group())
         Temperature =re.search( r'\btemperature\b|\b(your)(?=\stemperature)(\s\w+){1}\b|\b(examine)(?=\syour\stemperature)(\s\w+){2}\b|\b(let)(?=\sme\scheck\syour\stemperature)(\s\w+){4}\b|\bthermometer\b|\b(check)(?=\syour\stemperature)(\s\w+){2}\b ',line, re.M|re.I)
         if Temperature :
             print (" Temperature is found : ",Temperature.group())
             keywords.append("Temperature")
             keywords.append(Temperature.group())
         Weight =re.search( r'\b(have)(?=\syou\sdone\sthis\sbefore)(\s\w+){4}\b|\b(jump)(?=\son)(\s\w+){1}\b|\b(jump\son)(?=\smy\sscales\sfor\sme)(\s\w+){4}\b|\b(take)(?=\smy\sshoes\soff)(\s\w+){3}\b|\b(hop)(?=\s(on\sthe\sscales\sfor\sme|on\sthe\sscales))(\s\w+){5}\b|\b(step)(?=\son)(\s\w+){1}\b|\b(want)(?=\sto\srecord\syour\sweight)(\s\w+){4}\b|\b(check)(?=\syour\sweight)(\s\w+){2}\b|\b(pop)(?=\syou\son\sthe\sscales)(\s\w+){4}\b|\b(gone)(?=\sup)(\s\w+){1}\b|\b(pop)(?=\syou\son)(\s\w+){2}\b|\bkilos\b|\bscale\b|\b(step)(?=\son\sthis\sscale)(\s\w+){3}\b|\b(can)(?=\si\sjust\scheck\syour\sweight)(\s\w+){5}\b|\b(BMI)(?=\schart)(\s\w+){1}\b|\bweight\b|\b(hop)(?=\son)(\s\w+){1}\b|\b(take)(?=\sa\sbig\sbreath\sin)(\s\w+){4}\b|\bscales\b|\b(weight)(?=\sis\sslightly\sover)(\s\w+){3}\b|\b(body)(?=\smass\sindex)(\s\w+){2}\b|\b(you)(?=\sare\sless)(\s\w+){2}\b',line, re.M|re.I)  
         if Weight:
             print ("Weight is found : ",Weight.group())
             keywords.append("Weight")
             keywords.append(Weight.group())
    else:
      print ("No match!!")
    match=True
    return match

def join_key_medical_list(artifact_name,keywords):
      for  arti in artifact_name:
             medical_list.append(arti)
      for keyword in keywords:
             medical_list.append(keyword)
      return medical_list
               
def list_elements_check(transcript_sections,keyword_match):
     for keys in keyword_match:
             for sections in transcript_sections:
                if transcript_sections[sections] == keyword_match[keys]:
                    matche = matches.append(keyword_match[keys])
     return matche
          
def get_index(transcript_sections):
    for keys in keywords:
        keyword=keys
    for sections in transcript_sections:
         line=' '.join([str(item) for item in sections])
         words_line = word_tokenize_txt(line)
    #for words in words_line:
         # w=words
         for index, keyword in enumerate(words_line):
             index_list.append(index)
    return index_list
def get_wps(transcript_sections):
     check=False
     for sections in transcript_sections:
            #print("this is section",sections)
            line=' '.join([str(item) for item in sections])
            words_line = word_tokenize_txt(line)
            wsps = word_said_per_second(words_line)
            check=True
            if check==True:
               print("Done for wsps")
     else:
          print("setion no more for wsps")
          return wsps   
def get_word_line(transcript_sections):
        check=False
        for sections in transcript_sections:
            #print("this is section",sections)
            line=' '.join([str(item) for item in sections])
            words_line = word_tokenize_txt(line)
            word_line_section.append(words_line)
            check=True
            if check==True:
               print("Done")
        else:
            print("setion no more")
            return word_line_section
def convert_keywords_towords(keywords):
     for keyword in keywords:
         key_token = word_tokenize_txt(keyword)
         keyword_match.append(key_token)
     return keyword_match
def check_consecutive(section, keywords, index):

    match = True

    for i in range(len(keywords)):
        #print("this is length medical keyword",len(keywords))
        if index + i < len(section):
            #print("this is length of section ",len(section))
            if (section[index+i] != keywords[i] and keywords[i] != "$"):
                #print("this is section of consective ",section[index+i])
               # print("this is keyword of consective ",keywords[i])
                match = False

    return match


def get_transcripts():
    for transcript in os.listdir('transcript_input'):
        print("-------------------------------")
        print("Grabbing Transcript: " + transcript[:-16])
        create_transcript_directory(transcript)
        #print(transcript)
        text = convert_to_txt(transcript) 
        sentences = sentence_tokenize_txt(text)
        sentences = format_sentences(sentences)   
        #print(sentences)
        transcript_sections = find_timetamps(sentences, transcript)
        match=regx_matching(transcript_sections)
        list_keywords=convert_keywords_towords(keywords)
        line_sections=get_word_line(transcript_sections)
        medical=join_key_medical_list(artifact_name,keywords)
        print( medical)
        check=False
        
    for section in transcript_sections:
            st = section[0]
            #print("this is st", st)
            et = section[-1]
            #print("this is et", et)

            if len(section) == 3 or len(section) == 2:

                split1 = convert_to_seconds(st)
                split2 = convert_to_seconds(et)
                split3 = split1 + split2
                split4 = split3/2

                previousMedicalArtefact = "nill"
                splitKeywords = "[]"
                print("Found a split " + str(split4))
                splitKey = [transcript[:-16], splitKeywords,
                            split4, previousMedicalArtefact]
                print(splitKey)
                frames.append(splitKey)
            for key_list in list_keywords:
                ind = list_keywords.index(key_list)
                if ind % 2:
                   check = all(w in section for w in  key_list) 
                else:
                   frame_file_name=key_list
                   print("Hi its frame name", frame_file_name)  
               
                if check==True:
                           print("Hello, you are successful")
                           for index, w in enumerate(section):
                               consective_match=check_consecutive(section, key_list, index)
                               if (consective_match == True):
                                   print("You are on track")
                                   wsps = word_said_per_second(section)
                                   start_time = convert_to_seconds(st)
                                   frame_location_time = start_time + (index*wsps)
                                   key = [transcript[:-16],
                                          key_list, frame_location_time, frame_file_name]
                                   frames.append(key)
                           
                       
def get_frame():

    frames.sort(key=lambda x: x[2])

    for i in frames:
        practical_name = i[0]
        practical_keywords = i[1]
        practical_time = i[2]
        practical_name = practical_name.replace("_", " ")
        practical_name = practical_name.replace("_", " ")
        video_name = practical_name + "_Deidentified.mp4"
        video_path = os.path.join('videos', video_name)
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)  
        length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        time_location = strftime("%H:%M:%S", gmtime(practical_time))
        print("Consultation: " + str(practical_name) + " | Medical Artefact: " +
              str(practical_keywords) + "| Time Location: " + str(time_location))
        frame_number = calculate_time_frame(practical_time, fps)
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
        _, frame = cap.read()
        print(video_path)
        practical_time = strftime("%H.%M.%S", gmtime(practical_time))

        medical_artefact_name = str(i[3])

        name = str(practical_name) + "_" + \
            medical_artefact_name + "_(" + str(practical_time) + ")" + \
            str(practical_keywords)
        frame_path = os.path.join("frames_output", i[0])
        print(frame_path)
        frame_name = str(name) + ".jpg"
        print(video_name)
        if (frame_number <= length):
            cv2.imwrite(os.path.join(frame_path, frame_name), frame)
        cv2.destroyAllWindows()


def rename_transcripts():
    # Pract_No._GP#_R##_Transcript:
    transcriptModelName = "Pract_No?_GP#_R!_Transcript"
    for transcript in os.listdir('transcript_input'):
        transcriptName = str(transcript).lower()
        gpNumber = int(transcriptName.find("gp")) + 2
        gpNumberNext = gpNumber + 1

        if(transcriptName[gpNumber+1] == "_"):
            gpNumber = transcriptName[gpNumber]
        else:
            gpNumber = transcriptName[gpNumber:gpNumberNext+1]


if __name__ == "__main__":
    delete_output('transcript_output')
    delete_output('frames_output')
    #check_duplicates()
    get_transcripts()
    get_frame()