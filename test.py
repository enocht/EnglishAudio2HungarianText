import time
from mutagen.wave import WAVE
import pygame as pygame

audio_file = input("Enter Absolute Path of Audio: ")
# audio_file = '/Users/mac/PycharmProjects/speech2text/my_audio.wav'

audio = WAVE(audio_file)
audio_info = audio.info
length = int(audio_info.length)
print(length, 'seconds')
print('\nPlaying Audio...')
pygame.mixer.init()
pygame.mixer.music.load(audio_file)
pygame.mixer.music.play()

time.sleep(length)
print('Audio Finished Playing :)')



# t_r = transcribed_result.split()
# t_r_2 = []
# for i in t_r:
#     res = re.sub(r'^\W+|\W+$', '', i)
#     t_r_2.append(res.lower())
# transcribed_result_2 = ' '.join(t_r_2)
# print('\n{}'.format(sorted(Counter(t_r_2).items())))


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
