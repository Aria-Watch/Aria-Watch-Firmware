from Functions.Tools import GetTime
import config

#Function to handle log and error
def LogMaster(Content,Type,Severity):
    
    #Check the log type
    if Type == "Error":
        file = "data/log/error.log"
    elif Type == "Sent":
        file = "data/log/sent.log"
    elif Type == "GPS":
        file = "data/log/gps.log"
    elif Type == "WIFI":
        file = "data/log/wifi.log"
    else:
        return
    
    #Save Log
    with open(file, 'a+b') as f:
        f.write("\n" + "[" + str(GetTime()) + "] -> " + str(Content))
    f.close()
    
    #If Debug print on screen
    if config.DEBUG: print("-> " + Content)
    
    #Check severity and act according 
    if Severity == 1:
        SendErrorToServer()
    return

#ToDo if error perssist send the info to the server,if the error is not in the wifi 
def SendErrorToServer():
    if config.DEBUG: print("-> Send the error to the server")
    return