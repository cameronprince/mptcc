
from machine import Pin, SPI
import sdcard
import uos
import umidiparser

SPI_1_INTERFACE = 0
SPI_1_BAUD = 1000000
PIN_SPI_1_SCK = 2
PIN_SPI_1_MOSI = 3
PIN_SPI_1_MISO = 4
PIN_SPI_1_CS = 1
SD_MOUNT_POINT = "/sd"

spi = SPI(
    SPI_1_INTERFACE,
    baudrate=SPI_1_BAUD,
    polarity=0,
    phase=0,
    sck=Pin(PIN_SPI_1_SCK),
    mosi=Pin(PIN_SPI_1_MOSI),
    miso=Pin(PIN_SPI_1_MISO)
)
sd = sdcard.SDCard(spi, Pin(PIN_SPI_1_CS, Pin.OUT))
uos.mount(sd, SD_MOUNT_POINT)

# file_path = SD_MOUNT_POINT + "/" + 'axel.mid'
file_path = SD_MOUNT_POINT + "/" + 'sweet_caroline_gr_kar.mid'

"""
midi_file = umidiparser.MidiFile(file_path)

for event in midi_file.play():
    print(event)
"""

# for track in umidiparser.MidiFile(file_path, buffer_size=0).tracks:

for index, track in enumerate(umidiparser.MidiFile(file_path, buffer_size=0).tracks):
    print(f"Track {index}")
    for event in track:
        # print('status: ', event.status)


        """if (event.status == umidiparser.CHANNEL_PREFIX):
            print('channel: ', event.channel)

        if (event.status == umidiparser.NOTE_ON or event.status == umidiparser.NOTE_OFF or event.status == umidiparser.POLYTOUCH):
            print('note: ', event.note)

        if (event.status == umidiparser.NOTE_ON or event.status == umidiparser.NOTE_OFF):
            print('velocity: ', event.velocity)

        if (event.status == umidiparser.AFTERTOUCH or event.status == umidiparser.CONTROL_CHANGE or event.status == umidiparser.POLYTOUCH):
            print('value: ', event.value)

        if (event.status == umidiparser.PITCHWHEEL):
            print('pitch: ', event.pitch)

        if (event.status == umidiparser.PROGRAM_CHANGE):
            print('program: ', event.program)

        if (event.status == umidiparser.CONTROL_CHANGE):
            print('control: ', event.control)

        if (event.status == umidiparser.SEQUENCE_NUMBER):
            print('number: ', event.number)

        if (event.status == umidiparser.TEXT or event.status == umidiparser.COPYRIGHT or event.status == umidiparser.LYRICS or event.status == umidiparser.MARKER or event.status == umidiparser.CUE_MARKER):
            print('text: ', event.text)

        if (event.status == umidiparser.TRACK_NAME or event.status == umidiparser.INSTRUMENT_NAME or event.status == umidiparser.PROGRAM_NAME or event.status == umidiparser.DEVICE_NAME):
            print('name: ', event.name)

        if (event.status == umidiparser.MIDI_PORT):
            print('port: ', event.port)

        if (event.status == umidiparser.SET_TEMPO):
            print('tempo: ', event.tempo)
            
        if (event.status == umidiparser.KEY_SIGNATURE):
            print('key: ', event.key)

        if (event.status == umidiparser.TIME_SIGNATURE):
            print('numerator: ', event.numerator)

        if (event.status == umidiparser.TIME_SIGNATURE):
            print('denominator: ', event.denominator)

        if (event.status == umidiparser.TIME_SIGNATURE):
            print('clocks_per_click: ', event.clocks_per_click)

        if (event.status == umidiparser.TIME_SIGNATURE):
            print('notated_32nd_notes_per_beat: ', event.notated_32nd_notes_per_beat)

        if (event.status == umidiparser.SMPTE_OFFSET):
            print('frame_rate: ', event.frame_rate)

        if (event.status == umidiparser.SMPTE_OFFSET):
            print('hours: ', event.hours)

        if (event.status == umidiparser.SMPTE_OFFSET):
            print('minutes: ', event.minutes)

        if (event.status == umidiparser.SMPTE_OFFSET):
            print('seconds: ', event.seconds)

        if (event.status == umidiparser.SMPTE_OFFSET):
            print('frames: ', event.frames)

        if (event.status == umidiparser.SMPTE_OFFSET):
            print('sub_frames: ', event.sub_frames)

        print('data: ', event.data)"""

        # print('is_channel: ', event.is_channel())
        # print('is_meta: ', event.is_meta())

        if not event.is_meta():
            break

        # if not event.is_channel():
        #    break

        if event.status == umidiparser.TRACK_NAME:
            print(event.name)

    print(' ')
