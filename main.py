import re
import sys

import azure.cognitiveservices.speech as speechsdk
import time
# from mutagen.wave import WAVE
# import pygame as pygame
from asr_evaluation.asr_evaluation import get_error_count, get_match_count, remove_tail_id, remove_head_id, confusions, \
    track_confusions, print_instances_p, print_errors_p, print_instances
from googletrans import Translator
from iso_language_codes import *
from asr_evaluation import __main__
from edit_distance import SequenceMatcher
from collections import defaultdict


def process_line_pair(ref_line, hyp_line, case_insensitive=False, remove_empty_refs=False):
    """Given a pair of strings corresponding to a reference and hypothesis,
    compute the edit distance, print if desired, and keep track of results
    in global variables.
    Return true if the pair was counted, false if the pair was not counted due
    to an empty reference string."""
    # I don't believe these all need to be global.  In any case, they shouldn't be.
    error_count = 0
    match_count = 0
    ref_token_count = 0
    sent_error_count = 0

    # Split into tokens by whitespace
    ref = ref_line.split()
    hyp = hyp_line.split()
    id_ = None

    # If the files have IDs, then split the ID off from the text
    if files_head_ids:
        id_ = ref[0]
        ref, hyp = remove_head_id(ref, hyp)
    elif files_tail_ids:
        id_ = ref[-1]
        ref, hyp = remove_tail_id(ref, hyp)

    if case_insensitive:
        ref = list(map(str.lower, ref))
        hyp = list(map(str.lower, hyp))
    if remove_empty_refs and len(ref) == 0:
        return False

    # Create an object to get the edit distance, and then retrieve the
    # relevant counts that we need.
    sm = SequenceMatcher(a=ref, b=hyp)
    errors = get_error_count(sm)
    matches = get_match_count(sm)
    ref_length = len(ref)

    # Increment the total counts we're tracking
    error_count += errors
    match_count += matches
    ref_token_count += ref_length

    if errors != 0:
        sent_error_count += 1

    # If we're keeping track of which words get mixed up with which others, call track_confusions
    if confusions:
        track_confusions(sm, ref, hyp)

    # If we're printing instances, do it here (in roughly the align.c format)
    if print_instances_p or (print_errors_p and errors != 0):
        print_instances(ref, hyp, sm, id_=id_)

    # Keep track of the individual error rates, and reference lengths, so we
    # can compute average WERs by sentence length
    lengths.append(ref_length)
    error_rate = errors * 1.0 / len(ref) if len(ref) > 0 else float("inf")
    error_rates.append(error_rate)
    wer_bins[len(ref)].append(error_rate)
    return error_rate


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
speech_recognizer.recognized.connect(lambda evt: result.append(evt.result.text))
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


with open(input("\nEnter Absolute Path of Reference File For Comparison: "), 'r') as file:
    correct_txt = file.read().rstrip()


lengths = []
error_rates = []
wer_bins = defaultdict(list)
files_head_ids = False
files_tail_ids = False

# Get Word Error Rate
print("\nThe Word Error Rate is", process_line_pair(transcribed_result.lower(), correct_txt.lower()))

# Translate Text to Hungarian
print('\nTranslation from {} to Hungarian:'.format(language_name(translator.detect(transcribed_result).lang)))
translated_text = translator.translate(transcribed_result, dest=to_language)

print(translated_text.text)

# Remove all non-alpha numeric characters after every word

# t_r = transcribed_result.split()
# t_r_2 = []
# for i in t_r:
#     res = re.sub(r'^\W+|\W+$', '', i)
#     t_r_2.append(res.lower())
# transcribed_result_2 = ' '.join(t_r_2)
# print(transcribed_result_2)
