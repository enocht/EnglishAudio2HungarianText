import azure.cognitiveservices.speech as speechsdk
import time
from collections import Counter
import re
from mutagen.wave import WAVE
import pygame as pygame
from googletrans import Translator
from iso_language_codes import *

speech_key, service_region = "3eb9c244756b430c8f683f37f3b78ae1", "westeurope"
speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
audio_file = input("Enter Absolute Path of Audio File: ")
audio_file_ = speechsdk.audio.AudioConfig(filename=audio_file)
speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_file_)

done = False
result = []

from_language, to_language = 'en-US', 'hu'


def stop_cb(evt):
    """callback that stops continuous recognition upon receiving an event `evt`"""
    speech_recognizer.stop_continuous_recognition()
    global done
    done = True


# Connect callbacks to the events fired by the speech recognizer
speech_recognizer.recognizing.connect(lambda evt: evt)
speech_recognizer.recognized.connect(lambda evt: result.append('{}'.format(evt.result.text)))
speech_recognizer.session_started.connect(
    lambda evt: print('SESSION STARTED: {}\nListening to the audio file...'.format(evt)))
speech_recognizer.session_stopped.connect(lambda evt: print('SESSION STOPPED {}'.format(evt)))
speech_recognizer.canceled.connect(lambda evt: evt)
# stop continuous recognition on either session stopped or canceled events
speech_recognizer.session_stopped.connect(stop_cb)
speech_recognizer.canceled.connect(stop_cb)

# Start continuous speech recognition
speech_recognizer.start_continuous_recognition()
while not done:
    time.sleep(.5)

transcribed_result = ' '.join(result)
translator = Translator()

print("\nTranscribed Audio ({}): ".format(language_name(translator.detect(transcribed_result).lang)))
print(transcribed_result)

# Get Audio Length
# audio = WAVE(audio_file)
# audio_info = audio.info
# length = int(audio_info.length)
# print('\nThis audio file is {} seconds long'.format(length))
# print('\nPlaying Audio...')
# print('Verify Transcription accuracy by listening to the audio while reading the text')
# pygame.mixer.init()
# pygame.mixer.music.load(audio_file)
# pygame.mixer.music.play()
# time.sleep(length)
# print('Audio Finished Playing :)')

print('\nTranslation from {} to Hungarian:'.format(language_name(translator.detect(transcribed_result).lang)))
translated_text = translator.translate(transcribed_result, dest=to_language)

print(translated_text.text)
