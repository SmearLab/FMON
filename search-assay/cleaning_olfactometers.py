import serial, time, sys

vials = [6,7,8]; #which vials do you want to clean? 
cleaning_time = 5 #how long do you want to clean? in seconds  
evaporation_time = 7200 #how long do you want to dry? in seconds, 2 hours

tnsyport = '\\\\.\\COM3';
tnsy = serial.Serial(tnsyport,115200,timeout=1)

time.sleep(3) 

print "System Ready. Initiating cleaning..."

status = 0; vial = 0; cleaner = 'iso'
while True:
    if status == 0: 
        print "Cleaning Vial #" + str(vials[vial])
        tnsy.write("vialOn 1 " + str(vials[vial]) + "\r")
        tnsy.write("vialOn 2 " + str(vials[vial]) + "\r")
        status = 1; starttime = time.time()
    if status == 1:
        if time.time() - starttime >= cleaning_time:
            tnsy.write("vialOff 1 " + str(vials[vial]) + "\r")
            tnsy.write("vialOff 2 " + str(vials[vial]) + "\r")
            vial = vial + 1; status = 0
        if vial == len(vials):
            print "Cleaning Dummy Vial" 
            starttime = time.time(); status = 2
    if status == 2:
        if time.time() - starttime >= cleaning_time:
            break

print "Isopropanol step complete. Please replace with DI water for step #2."
while True:
    request = str(input("Enter 1 when you have replaced the fluid. Enter 0 to manually exit."))
    if request == '1': break
    if request == '0': sys.exit('Manual exit requested')
    
print "System Ready. Initiating cleaning..."

status = 0; vial = 0
while True:
    if status == 0: 
        print "Cleaning Vial #" + str(vials[vial])
        tnsy.write("vialOn 1 " + str(vials[vial]) + "\r")
        tnsy.write("vialOn 2 " + str(vials[vial]) + "\r")
        status = 1; starttime = time.time()
    if status == 1:
        if time.time() - starttime >= cleaning_time:
            tnsy.write("vialOff 1 " + str(vials[vial]) + "\r")
            tnsy.write("vialOff 2 " + str(vials[vial]) + "\r")
            vial = vial + 1; status = 0
        if vial == len(vials):
            print "Cleaning Dummy Vial" 
            starttime = time.time(); status = 2
    if status == 2:
        if time.time() - starttime >= cleaning_time:
            break
    
print "Cleaning Complete. Initiating drying..."
vial = 0; status = 0
while True: 
    if status == 0: 
        print "Drying Vial #" + str(vials[vial])
        tnsy.write("vialOn 1 " + str(vials[vial]) + "\r")
        tnsy.write("vialOn 2 " + str(vials[vial]) + "\r")
        status = 1; starttime = time.time()
    if status == 1:
        if time.time() - starttime >= evaporation_time:
            tnsy.write("vialOff 1 " + str(vials[vial]) + "\r")
            tnsy.write("vialOff 2 " + str(vials[vial]) + "\r")
            vial = vial + 1; status = 0
        if vial == len(vials):
            print "Drying Dummy Vial"
            starttime = time.time(); status = 2
    if status == 2:
        if time.time() - starttime >= evaporation_time:
            break

tnsy.close()

print "Manifolds cleaned and dried."
print "System shutdown. Please test manifold solenoids for leaks before using."
