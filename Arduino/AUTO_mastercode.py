'''
FMON MASTERCODE - Freely Moving Odor Navigation Mastercode

Written: Teresa Findley, tfindley@uoregon.edu
Last Updated: 9/23/17

--Records Tracking Data via Input from Bonsai
--Records Signal Data through NI USB-6009
'''

#     [SET UP]     #
trialtime = 2 #in seconds
##IMPORTS
##libraries
import numpy as np, cv2, os
import time, math, random, datetime
import OSC, threading, Queue
import nidaqmx, ctypes
import matplotlib.pyplot as plt
from nidaqmx.constants import AcquisitionType, Edge
from nidaqmx.stream_readers import AnalogMultiChannelReader
##local modules
from fmon_preferences_bonsai import *
import fmon_datamgt, fmon_tracking, fmon_serial

##INITIATE VARIABLES
session_num = 1; trial_num = 1; state = 1; prep_odor = True; iti_delay = iti_correct; #trial information

correct0=0; correct1=0; correct2=0; correct3=0; total0=0; total1 = 0; total2=0; total3=0; #online statistics
correct0L=0; correct1L=0; correct2L=0; correct3L=0; total0L=0; total1L=0; total2L=0; total3L=0;
correct0R=0; correct1R=0; correct2R=0; correct3R=0; total0R=0; total1R=0; total2R=0; total3R=0;

total_trials = 0;  total_left = 0; total_right = 0; left_correct = 0; right_correct = 0 #online statistics
total_correct = 0; fraction_correct = 0; fraction_left = 0; fraction_right = 0;
last_occupancy = 0; section_occupancy = 0; counter = 0; msg = 0 #online tracking
odor_calibration = np.genfromtxt(base_dir + 'data/olfactometercalibration.txt', delimiter = ',') #odor calibration array

datapath,session_num = fmon_datamgt.CHK_directory(mouse_id,group_name,session_num) #update/create datapath
trialsummary_file = datapath + 'trialsummary.txt'; ch0_file = datapath + 'PIDsignal.dat';

signaldata = np.zeros((6,buffersize),dtype=np.float64) #NI data collection reading variables
reader = AnalogMultiChannelReader(ni_data.in_stream) 

##START UP PROCEDURES
section,section_center=fmon_tracking.calc_partitions() #online tracking: gridline deliniation
triallist,odorconditionlist = fmon_datamgt.randomize_trials(random_groupsize,total_groupsize) #randomize trials
fmon_serial.close_all_valves() #turn off all hardware

#Session Summary

#Create/Open Data Files
ch0_handle = open(ch0_file,'ab');

#NI Set Up
ni_data.ai_channels.add_ai_voltage_chan(channels) #add channels to server
ni_data.timing.cfg_samp_clk_timing(samplingrate, '',Edge.RISING,AcquisitionType.CONTINUOUS,uInt64(buffersize)) #instruct how to sample
def ni_handler(): #define background function to handle incoming NI data
    while True:
        reader.read_many_sample(signaldata,number_of_samples_per_channel= buffersize, timeout=10.0)
        signaldata[0,:].tofile(ch0_handle); 
nisignal = threading.Thread(target = ni_handler) #set handler function in background
nisignal.daemon = True

##INITIATE SESSION
print "PID " + str(mouse_id) + ", Session " + str(session_num) #report session initiation
print "System Ready. Initiating Data Collection..."
session_start = time.time() #session timer
ni_data.start(); nisignal.start(); #start data collection 
localtime = datetime.datetime.now(); #stamp for video locator & session timestamp

print "Session Started."


#     [MAIN CODE]     #

while True: 
#   [State *](occurs in all states)
   
    if time.time() - session_start >= session_length:
        fmon_serial.close_all_valves()
        reasonforend = "Auto Session End"
        break

    if show_active_stats == True: #online trial statistics
        frame = cv2.imread('C:/Users/Smear Lab/Dropbox/data/statsbackground.jpeg')
        cv2.imshow('Session Statistics',frame) 

    ##Manual Session Termination
    if cv2.waitKey(1) & 0xFF == ord('q'): 
        fmon_serial.close_all_valves()
        reasonforend = "Manual Exit"
        break


#   [State 1] TRIAL INITIATION   
    if state == 1: 
        
        #Odor Preparation    
        if prep_odor == True:
            active_valve = triallist[trial_num-1] #side of odor delivery
            concentration_setting = odorconditionlist[trial_num-1] #concentration difference of odor delivery 
            #Update Trial Values & MFC settings
            low_valve, correctpoke,nameoftrialtype,correctindex,incorrectindex = fmon_datamgt.trial_values(active_valve)
            HairR,LairR,HairL,LairL,Hn2R,Ln2R,Hn2L,Ln2L,activevial,lowvial = fmon_serial.MFC_settings(concentration_setting,odor_calibration,active_valve)
            print "Upcoming Trial: " + nameoftrialtype + ", " + str(concentration_setting) #report upcoming trial
            #turn on MFCs and Vials
            if group_name != 'non-spatial':
                if active_valve == 1:
                    tnsy.write("MFC " + str(active_valve) + " " + str(MFC_air) + " " + str(HairR) + "\r")
                    tnsy.write("MFC " + str(active_valve) + " " + str(MFC_n2) + " " + str(Hn2R) + "\r")
                    tnsy.write("MFC " + str(low_valve) + " " + str(MFC_air) + " " + str(LairL) + "\r")
                    tnsy.write("MFC " + str(low_valve) + " " + str(MFC_n2) + " " + str(Ln2L) + "\r")
                if active_valve == 2: 
                    tnsy.write("MFC " + str(active_valve) + " " + str(MFC_air) + " " + str(HairL) + "\r")
                    tnsy.write("MFC " + str(active_valve) + " " + str(MFC_n2) + " " + str(Hn2L) + "\r")
                    tnsy.write("MFC " + str(low_valve) + " " + str(MFC_air) + " " + str(LairR) + "\r")
                    tnsy.write("MFC " + str(low_valve) + " " + str(MFC_n2) + " " + str(Ln2R) + "\r")
                tnsy.write("vialOn " + str(active_valve) + " " + str(activevial) + "\r")
                tnsy.write("vialOn " + str(low_valve) + " " + str(lowvial) + "\r")
            if group_name == 'non-spatial':
                if non_spatial_condition == 'odor_concentration': 
                    if active_valve == 1:
                        tnsy.write("MFC " + str(active_valve) + " " + str(MFC_air) + " " + str(HairR) + "\r")
                        tnsy.write("MFC " + str(active_valve) + " " + str(MFC_n2) + " " + str(Hn2R) + "\r")
                        tnsy.write("MFC " + str(low_valve) + " " + str(MFC_air) + " " + str(HairL) + "\r")
                        tnsy.write("MFC " + str(low_valve) + " " + str(MFC_n2) + " " + str(Hn2L) + "\r")
                    if active_valve == 2: 
                        tnsy.write("MFC " + str(active_valve) + " " + str(MFC_air) + " " + str(LairL) + "\r")
                        tnsy.write("MFC " + str(active_valve) + " " + str(MFC_n2) + " " + str(Ln2L) + "\r")
                        tnsy.write("MFC " + str(low_valve) + " " + str(MFC_air) + " " + str(LairR) + "\r")
                        tnsy.write("MFC " + str(low_valve) + " " + str(MFC_n2) + " " + str(Ln2R) + "\r")
                    tnsy.write("vialOn " + str(active_valve) + " " + str(odor_vial) + "\r")
                    tnsy.write("vialOn " + str(low_valve) + " " + str(odor_vial) + "\r")
                if non_spatial_condition == 'odor_identity': 
                    tnsy.write("MFC " + str(active_valve) + " " + str(MFC_air) + " " + str(HairR) + "\r")
                    tnsy.write("MFC " + str(active_valve) + " " + str(MFC_n2) + " " + str(Hn2R) + "\r")
                    tnsy.write("MFC " + str(low_valve) + " " + str(MFC_air) + " " + str(HairL) + "\r")
                    tnsy.write("MFC " + str(low_valve) + " " + str(MFC_n2) + " " + str(Hn2L) + "\r")
                    if active_valve == 1:
                        tnsy.write("vialOn " + str(active_valve) + " " + str(odor_vial) + "\r")
                        tnsy.write("vialOn " + str(low_valve) + " " + str(odor_vial) + "\r")
                    if active_valve == 2:
                        tnsy.write("vialOn " + str(active_valve) + " " + str(alt_odor_vial) + "\r")
                        tnsy.write("vialOn " + str(low_valve) + " " + str(alt_odor_vial) + "\r")                        

            iti_timeout_start = math.floor(time.time()) #start vial timer
            prep_odor = False #odor has been decided
        
        #Trial Initiation
        if (math.floor(time.time()) >= math.floor(iti_timeout_start + iti_delay)): #vial mixing timer
            tstart = time.time() - session_start; #timestamp trial start (in ms)
            tnsy.write("valve " + str(low_valve) + " 1 on\r") #turn on FVs
            tnsy.write("valve " + str(active_valve) + " 1 on\r")
            state = 2 #update trial variables
            print("Trial " + str(trial_num) + " Activated: " + nameoftrialtype) #report trial start


#   [State 2] TRIAL DECISION
    if state == 2:
        time_elapsed = (time.time() - session_start) - tstart
        if time_elapsed > trialtime:
            response = 1; answer = "Correct"
            print("Response registered: " + answer) #report response
            tnsy.write("valve " + str(active_valve) + " 1 off\r") #turn off final valves
            tnsy.write("valve " + str(low_valve) + " 1 off\r") 
            state = 3; counter = 0;  #update trial statistics

#   [State 3] REWARD DELIVERY
    if state == 3:    
        #Correct Responses
 
        if active_valve == 1: #Increment Active Statistics
            if concentration_setting == 0:
                total0 = total0 + 1; total0R = total0R + 1; correct0 = correct0 + 1; correct0R = correct0R + 1
            if concentration_setting == 1: 
                total1 = total1 + 1; total1R = total1R + 1; correct1 = correct1 + 1; correct1R = correct1R + 1
            if concentration_setting == 2: 
                total2 = total2 + 1; total2R = total2R + 1; correct2 = correct2 + 1; correct2R = correct2R + 1
            if concentration_setting == 3: 
                total3 = total3 + 1; total3R = total3R + 1; correct3 = correct3 + 1; correct3R = correct3R + 1
        if active_valve == 2:
            if concentration_setting == 0:
                total0 = total0 + 1; total0L = total0L + 1; correct0 = correct0 + 1; correct0L = correct0L + 1
            if concentration_setting == 1: 
                total1 = total1 + 1; total1L = total1L + 1; correct1 = correct1 + 1; correct1L = correct1L + 1
            if concentration_setting == 2: 
                total2 = total2 + 1; total2L = total2L + 1; correct2 = correct2 + 1; correct2L = correct2L + 1
            if concentration_setting == 3: 
                total3 = total3 + 1; total3L = total3L + 1; correct3 = correct3 + 1; correct3L = correct3L + 1
        print("Reward Delivered.") #report reward delivery
        tend = time.time() - session_start #timestamp trial end & record trial summary info
        fmon_datamgt.write_trialsummary(trialsummary_file,trial_num,concentration_setting, active_valve,response,tstart,tend)
        state = 1; prep_odor = True; iti_delay = iti_correct;trial_num = trial_num + 1;  #update trial variables 
 

#     [SHUT DOWN]     #


tnsy.write("vialOff " + str(right_valve) + " " + str(lowvial) + "\r")
tnsy.write("vialOff " + str(left_valve) + " " + str(lowvial) + "\r")

#Close All Data Files
ch0_handle.close();
##EXIT PROGRAM
fmon_serial.close_all_valves(); cv2.destroyAllWindows(); ard.close(); tnsy.close()
print "Session Ended." #report end of session
print "Data Collection Ended" #report end of data collection
