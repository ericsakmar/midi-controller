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
midi_knob_cc = 100
midi_switch_cc = 101
uart = busio.UART(board.TX, board.RX, baudrate=31250, timeout=0.001)
midi = adafruit_midi.MIDI(midi_in=uart, midi_out=uart, out_channel=midi_out_channel)

# pot stuff
p0 = analogio.AnalogIn(board.A0)
p0_last = 0

# switch stuff
pin = digitalio.DigitalInOut(board.D5)
pin.direction = digitalio.Direction.INPUT
pin.pull = digitalio.Pull.UP
switch = Debouncer(pin)
switch_on = False

# led stuff
led = digitalio.DigitalInOut(board.D13)
led.direction = digitalio.Direction.OUTPUT

# Main loop
while True:
    # midi thru
    msg = midi.receive()
    if msg is not None and not isinstance(msg, MIDIUnknownEvent):
        # print("MIDI Message received:", msg)
        midi.send(msg) # add msg.channel?

    # knobs
    sensor_value = p0.value
    difference = math.fabs(sensor_value - p0_last)
    if math.fabs(difference) > 258:
        midi_value = int((sensor_value / 65535) * 127)
        print("SENDING", midi_value)
        cc = ControlChange(midi_knob_cc, midi_value, channel=midi_out_channel)
        midi.send(cc)
        p0_last = sensor_value

    # switches
    switch.update()
    if switch.fell:
        switch_on = not switch_on
        led.value = switch_on
        midi_value = 127 if switch_on else 0
        cc = ControlChange(midi_switch_cc, midi_value, channel=midi_out_channel)
        print(cc)
        midi.send(cc)

    # time.sleep(1)