import os, sys, urllib2, json, time, threading, atexit
from socket import socket, SOCK_DGRAM, AF_INET

weAreRecording = False
weArePlayingMusic = False
weAreForcingReloadOfSoundCardDrivers = False

def speechToText(audioFile, capture):

        global weArePlayingMusic
        global weAreForcingReloadOfSoundCardDrivers

        if weAreForcingReloadOfSoundCardDrivers == True:
                return

        url = "http://www.google.com/speech-api/v1/recognize?xjerr=1&client=chromium&lang=en-GB"

        try:
                headers= {'Content-Type': 'audio/x-flac; rate=48000', 'User-Agent':'Mozilla/5.0'}
                request = urllib2.Request(url, data=audioFile, headers=headers)
                response = urllib2.urlopen(request)
                res = response.read()
                res = json.loads(res)

                result = None

                if not res['hypotheses']:
                        print("No results")
                else:
                        result = res['hypotheses'][0]['utterance']

                        wordList = result.split(' ')

                        theResultContainsHello = False

                        for word in wordList:
                                print word
                                if word == 'hello':
                                        theResultContainsHello = True

                        if theResultContainsHello == True and weArePlayingMusic == False:
                                print("Is it me you're looking for?")
                                weArePlayingMusic = True
                                os.system("aplay /home/pi/IIMYLF/webV/assets/IsItMe.wav")
                                weArePlayingMusic = False

                recordSpeech()
        except:
                print("Didn't recieve useful results")

        os.remove(capture + ".flac")
        os.remove(capture + ".wav")   

def recordSpeech():

        global weAreForcingReloadOfSoundCardDrivers
        global weAreRecording

        if weArePlayingMusic == False and weAreForcingReloadOfSoundCardDrivers == False and weAreRecording == False:
                print(time.time())
                fileName = "capture" + str(time.time())
                weAreRecording = True
                os.system("arecord -f cd -t wav --file-type wav -d 2 -r 48000 " + fileName  + ".wav")
                weAreRecording = False
                os.system("flac -f " + fileName  + ".wav")
                try:
                        read = open(fileName + ".flac", 'rb').read()
                        t = threading.Thread(target=speechToText, args = (read, fileName,))
                        t.start()
                except:

                        if weAreForcingReloadOfSoundCardDrivers == False:
                                print("File not found for recording\nRemoving stored files")
                                #os.system("rm *.flac; rm *.wav")
                                print("Forcing Reload of ALSA soundcard drivers\n")
                                weAreForcingReloadOfSoundCardDrivers = True
                                os.system("sudo alsa force-reload")
                                weAreForcingReloadOfSoundCardDrivers = False
                                print("Done. Attempting to record speech\n")
                                os.system("rm *.flac; rm *.wav")

def cleanUp():
        print("Exiting. Deleting all .wav and .flac files")
        os.system("rm *.wav; rm *.flac")

def init():
        atexit.register(cleanUp)

        while True:
                recordSpeech()

if __name__ == "__main__":
        init()