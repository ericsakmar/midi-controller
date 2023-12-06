import math
import time
import board
import busio
import analogio
import digitalio
import adafruit_midi
from adafruit_midi.midi_message import MIDIUnknownEvent
from adafruit_midi.stop import Stop
from adafruit_midi.timing_clock import TimingClock
from adafruit_midi.control_change import ControlChange
#TODO import all midi messages
from adafruit_debouncer import Debouncer

# midi stuff
midi_out_channel = 12
uart = busio.UART(board.TX, board.RX, baudrate=31250, timeout=0.001)
midi = adafruit_midi.MIDI(midi_in=uart, midi_out=uart, out_channel=midi_out_channel)

class Knob:
    def __init__(self, input, midi_control):
        self.pin = analogio.AnalogIn(input)
        self.last = 0
        self.midi_control = midi_control

    def update(self):
        midi_value = self.get_midi_value()

        if self.should_update(midi_value):
            cc = ControlChange(self.midi_control, midi_value, channel=midi_out_channel)
            print(cc)
            midi.send(cc)
            self.last = midi_value

    def get_midi_value(self):
        value = self.pin.value
        midi_value = int((value / 65535) * 127)

        # round up if close to one of the ends
        if midi_value == 126:
            return 127

        if midi_value == 1:
            return 0

        return midi_value

    def should_update(self, midi_value):
        difference = math.fabs(midi_value - self.last)
        return difference > 1

class Switch:
    def __init__(self, input, led_pin, midi_control):
        self.midi_control = midi_control

        self.pin = digitalio.DigitalInOut(input)
        self.pin.direction = digitalio.Direction.INPUT
        self.pin.pull = digitalio.Pull.UP

        self.switch = Debouncer(self.pin)
        self.switch_on = False

        self.led = digitalio.DigitalInOut(led_pin)
        self.led.direction = digitalio.Direction.OUTPUT

    def update(self):
        self.switch.update()

        if self.switch.fell:
            self.switch_on = not self.switch_on
            self.led.value = self.switch_on
            midi_value = 127 if self.switch_on else 0
            cc = ControlChange(self.midi_control, midi_value, channel=midi_out_channel)
            print(cc)
            midi.send(cc)

# pot stuff
knob1 = Knob(board.A0, 100)
knob2 = Knob(board.A1, 101)
knob3 = Knob(board.A2, 102)
knob4 = Knob(board.A3, 103)
knob5 = Knob(board.A4, 104)
knob6 = Knob(board.A5, 105)

# switch stuff
switch1 = Switch(board.D5, board.D13, 106)
switch2 = Switch(board.D6, board.D12, 107)

# Main loop
while True:
    # midi thru
    msg = midi.receive()
    if msg is not None and not isinstance(msg, MIDIUnknownEvent):
        # print("MIDI Message received:", msg)
        midi.send(msg) # add msg.channel?

    knob1.update()
    knob2.update()
    knob3.update()
    knob4.update()
    knob5.update()
    knob6.update()

    switch1.update()
    switch2.update()

    # time.sleep(1)
