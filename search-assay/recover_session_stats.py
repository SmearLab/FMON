'''
EXAMPLE CODE: Collecting and Saving Analog Signals with USB-6009 

Written: Teresa Findley, tfindley@uoregon.edu, 
Last Updated: 9/22/17

Adopted from documentation on the following websites:
---http://nidaqmx-python.readthedocs.io/en/latest/index.html
---https://pypkg.com/pypi/nidaqmx/f/nidaqmx/tests/test_stream_analog_readers_writers.py
'''
##SET UP

#Imports
import numpy as np
import matplotlib.pyplot as plt

mouse_id = '2148'
group_name = '100-0'
session_num = 14


base_dir = "D:/FMON_Project/"
datapath = base_dir + "data/goodmice/Mouse_" + mouse_id + "/" + group_name + "/" + str(session_num) + "/"

trialsummary_file = datapath + 'trialsummary.txt';


ts = np.genfromtxt(trialsummary_file, delimiter = ',')
conc = ts[:,1]
res1 = sum(ts[:,3][conc == 0])
tot1 = len(ts[conc==0])

res2 = sum(ts[:,3][conc == 1])
tot2 = len(ts[conc==1])

res3 = sum(ts[:,3][conc == 2])
tot3 = len(ts[conc == 2])

res4 = sum(ts[:,3][conc == 3])
tot4 = len(ts[conc == 3])

#res5 = sum(ts[:,4][conc == 4])
#tot5 = len(ts[conc == 4])

print str(res1) + "/" + str(tot1)
print str(res2) + "/" + str(tot2)
print str(res3) + "/" + str(tot3)
print str(res4) + "/" + str(tot4)
#print str(res5) + "/" + str(tot5)
