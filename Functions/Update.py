'''
 * Copyright (C) 2024 Aria.Watch - All Rights Reserved
'''

import urequests,json,ubinascii,config,io,os,uos,shutil,utarfile,machine


def Update(version):
    #Downlaod new firmware from server
    data = {"Device" : config.DEVICE_ID}
    data64 = ubinascii.b2a_base64(bytes(str(json.dumps(data)),'UTF-8'))
    url = "https://data.aria.watch/update"
    r = urequests.post(url, data = data64)
    #Create tmp folder
    os.mkdir("tmp")
    # Save file
    with io.open("tmp/firmware.tar", "w") as file_output:
        file_output.write(r.content)
    #Extract Tar file in folder
    ExtractFirmware()
    #Get folder path
    folder = FirmwareFileLocation()
    # Install Firmware
    InstallNewFirmware(folder)
    #Delete tmp folder
    RemoveFolder("tmp")
    #Update Firmware Version
    with open('data/version.json') as f:
        data = json.load(f)
    data['FVersion'] = version
    with open('data/version.json', 'w') as f:
        json.dump(data, f)
        f.close()
    #Reboot
    machine.reset()
 
    
def ExtractFirmware():
    tar = utarfile.TarFile("tmp/firmware.tar")
    for i in tar:
        if i.type == utarfile.DIRTYPE:
            dirname = "tmp/"+ str(i.name)
            uos.mkdir(dirname.rstrip('/'))
        else:
            sub_file = tar.extractfile(i)
            filename = "tmp/"+ str(i.name)
            with open(filename, "wb") as dest:
                shutil.copyfileobj(sub_file, dest)
                dest.close()
                
#Function to replace the firmware file with the new one                
def InstallNewFirmware(firmwarefolder):
    #Exclusion List     
    exclude = ["config.py", "data", "README.md"]
    content = uos.listdir(firmwarefolder)
    for element in content:
        origine_path = firmwarefolder + "/"+ element
        file = element.split('/')[-1]
        #Check if file is not to be escluded
        if file not in exclude:
            #Check if the elemnt is a folder or a file
            if uos.stat(origine_path)[0] & 0o170000 == 0o040000:
                folder = firmwarefolder + "/" + file
                # Recursione
                InstallNewFirmware(folder)
            else:
                #Copy file nella nuova directory
                fileLocation = firmwarefolder.replace(FirmwareFileLocation(), "")
                dest_file = fileLocation + "/" +  file
                #print("Copia da: " + origine_path + " Verso: "+ dest_file )
                with open(origine_path, 'rb') as origin, open(dest_file, 'wb') as dest:
                    dest.write(origin.read())


# Function to return the extracted firmware location
def FirmwareFileLocation():
    for x in uos.listdir("tmp"):
        if x.startswith("bora_aria_watch"):
            folder = "tmp/" + str(x)
    return(folder)


def RemoveFolder(folder):
    content = uos.listdir(folder)
    for element in content:
        path = folder + "/" +element
        if uos.stat(path)[0] & 0o170000 == 0o040000:
            RemoveFolder(path)
        else:
            uos.remove(path)
    uos.rmdir(folder)
        
    

