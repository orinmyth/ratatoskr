import requests #For http requests 
import os #Access to files
import json #Export to JSON
import glob #Look for relevant files
import fitz #PDF to image 
import cv2 #Video handling, also requires ffmpeg is installed
import tempfile #Create Temp Directory for Video Processing


location = input("Target Directory?\n")
location += '\\**'

languageinput = input("Select languages e.g. ara rus fra eng\n")
languages = languageinput.split()

for language in languages: 

    #Prepare URL based on user input
    url = f"http://localhost:8080/extract-text?lang={language}"
    headers = {
    'Content-Type': 'image/png'
    }

    #Print(imgfiles)
    OutputOCR = []

    #Extracts frames from video and calls ImageOCR on each frame
    def VideoOCR(target):
        #Extract frames from video
        print(f"Extracting frames from {os.path.basename(target)}.")
        with tempfile.TemporaryDirectory() as tmpdirname:
            print('Created temporary directory', tmpdirname)
            vidcap = cv2.VideoCapture(target)
            success,image = vidcap.read()
            count = 0
            while success:
                cv2.imwrite(f"{tmpdirname}\\frame{count}.jpg", image) # save frame as JPEG file      
                success,image = vidcap.read()
                print('Reading frame: ', success)
                count += 1
            #Send OCR Request for each frame
            frames = glob.glob(f"{tmpdirname}\\frame*.jpg")
            for frame in frames: 
                ImageOCR(frame)

    #Converts PDF to image (PNG) and calls ImageOCR on tempfile
    def PDFOCR(target):
        #Convert PDF to image
        print(f"Converting {os.path.basename(target)} to image format.")
        doc = fitz.open(target)
        page = doc.loadPage(0) #number of pages
        pix = page.getPixmap()
        with tempfile.NamedTemporaryFile() as tmpfilename:
            pix.writePNG(tmpfilename.name)
            #Send OCR Request for output
            ImageOCR(tmpfilename.name)

    #Sends OCR request to Web API
    def ImageOCR(target):
        print(f"Sending OCR Request for: {os.path.basename(target)}.")
        datafile =  open(target,"rb")
        payload = datafile.read()
        datafile.close()
        response = requests.request("POST", url, headers=headers, data = payload)
        if(response.status_code == 200):
            data = response.json()
            data['filename'] = os.path.basename(localfile)
            OutputOCR.append(data)
        else:
            print(f"Received status code from server: {response.status_code}.")

    #Main         

    #Find supported files from target directory, including all sub-folders
    localfiles = glob.glob(location, recursive=True)
    for localfile in localfiles: 
        if localfile.lower().endswith(('.mp4','.avi','.mpeg')):
            VideoOCR(localfile)
        if localfile.lower().endswith('.pdf'):
            PDFOCR(localfile)
        if localfile.lower().endswith(('.gif', '.jpeg', '.tif', '.png', 'jpg')):
            ImageOCR(localfile)

    if(OutputOCR == []):
        print("No valid files found")

    #Create JSON with OCR output
    with open(f'C:\\Users\\CIS_User\\Documents\\Dev\\vitriol-integration\\vedfolnir\\OCR_Output_{language}.json','w', encoding='utf8') as fout: 
        json.dump(OutputOCR,fout, ensure_ascii=False)
