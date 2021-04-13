'''
FMON MODULE
Preferences (Constants in Freely Moving Olfactory Navigation Task)

Written By: Sarah Stednitz (sstednit@uoregon.edu) & Teresa Findley (tfindley@uoregon.edu)
Last Updated: 01.04.18, Teresa Findley
'''

#     [USER INPUT]     #

COM_coordinates = "(416,612)" #location of recording device in pixels
group_name = "interleaved" #what experiment are you running? (OPTIONS: trainer1, trainer2, 100-0, 80-20, 60-40, interleaved, abs-conc, non-spatial) 
recording_num = '4' #sessions not automated...which session are you running? 
trialtime = 2 #set length of each automated trial -- in seconds


odortype = 'pinene' #odor identity (pinene, octanol, amyl acetate, etc.)
odor_vial = 7 #where is your odor? (KEY: 6 - blank, 7 - blank, 8 - pinene)
odor_vial2 = 8 #0.1% pinene vial
blank_vial = 6

#Only for non-spatial experiments
non_spatial_condition = 'odor_identity' #OPTIONS: odor_concentration or odor_identity

#     [SET UP]     #

##IMPORTS
##libraries
import numpy as np, serial, ctypes,nidaqmx
int32 = ctypes.c_long; uInt64 = ctypes.c_ulonglong; float64 = ctypes.c_double #64 bit float
#     [OPTIONS]     #

##TRIAL
random_groupsize = 20 #group of trials that contain an even # of events, divisible by 20
total_groupsize = 120 #total number of possible trials, must be divisible by random_groupsize
show_active_stats = True;
#Data Paths
base_dir = "Z:/FMON_Project/analysis/PID_session_data/" + recording_num + '/' #root of data path (below, data compilation file location)
compdatafile = "Z:/Users/Smear Lab/workspace/FMON/DataCompilation/data_compilation_"+group_name+".txt"
#Timing
count_requirement = 4 #how many frames in one quadrant registers response? 
iti_correct = 4; iti_incorrect = 10 #inter-trial intervals
timeout_delay = 5*60 #how long does the timeout between trials?
#Online Tracking
y_min = 0; y_max = 720; x_min = 0; x_max = 1210;
x_sections = 3; y_sections = 2 #how many partitions? 
#Valve Designations
left_valve = 2; right_valve = 1; rightport = 1; leftport = 2; nosepokeport = 4; MFC_air = 1; MFC_n2 = 2;

##NI USB-6009 DATA COLLECTION
samplingrate = 800; buffersize = 25; channel_num = 6 #number of channels
#Name Channels (this is how the files will be saved in the datapath)
ch0 = 'PIDsignal'; ch1 = 'NP'; ch2 = 'LFV'; ch3 = 'RFV';

##ARDUINO & TEENSY COMMUNICATION
port='\\\\.\\COM6'; tnsyport = '\\\\.\\COM3';

#     [CONSTANTS]     #

##TRIAL
if group_name == 'trainer1' or group_name == 'trainer2':
    sessionlength = 30 #in minutes
if group_name == '100-0' or group_name == '80-20' or group_name == '60-40':
    sessionlength = 40 #in minutes
if group_name == 'interleaved' or group_name == 'abs-conc' or group_name == 'non-spatial' or group_name == 'nostril-occlusion':
    sessionlength = 8 #in minutes
session_length = sessionlength * 60
#Online Tracking
num_sections = x_sections*y_sections; section  = [np.nan]*num_sections; section_center = [np.nan]*num_sections; 

##NI USB-6009 DATA COLLECTION
channels = 'Dev1/ai0:' + str(channel_num-1); ni_data = nidaqmx.Task()

##ARDUINO & TEENSY COMMUNICATION
ard = serial.Serial(port,115200,timeout=1); tnsy = serial.Serial(tnsyport,115200,timeout=1)
