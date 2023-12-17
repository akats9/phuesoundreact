from phue import Bridge
import pyaudio
import time
from math import *
import audioop
import os
import sys

def restart_program():
    python = sys.executable
    os.execl(python, python, *sys.argv)

b = Bridge("192.168.1.50")
b.connect()
b.get_api()

light = 'Hue ambiance lamp 3'

b.set_light(light,'on',True)

p = pyaudio.PyAudio()
WIDTH = 2
RATE = int(p.get_default_input_device_info()['defaultSampleRate'])
DEVICE = p.get_default_input_device_info()['index']
rms = 1
print(p.get_default_input_device_info())

def callback(in_data, frame_count, time_info, status):
    global rms
    rms = audioop.rms(in_data,WIDTH) / 32767
    return in_data, pyaudio.paContinue

stream = p.open(format = p.get_format_from_width(WIDTH),
                input_device_index=DEVICE,
                channels=1,
                rate=RATE,
                input=True,
                output=False,
                stream_callback=callback)

stream.start_stream()

try:
    while stream.is_active():
        db = 20 * log10(rms)
        dbl = round(max(1, min(254, (db+70)*((db+70)/10))))
        dbt = round(max(2000,min(6500,(db+70)*((db+70)*10))))
        b.set_light(light, 'bri', dbl)
        b.set_light(light, 'ct',dbt)
        print(f"Bri: {dbl} Ct: {dbt}")
        time.sleep(0.1)
except ConnectionResetError:
    restart_program()

stream.stop_stream()
stream.close()
p.terminate()

