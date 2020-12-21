import time
import busio
import digitalio
import board
import RPi.GPIO as GPIO
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn
from amidiw import MIDIInterface
from amidiw import CC_ON

# set midi cc code
CC_EXPRESSION = 11

# create the spi bus
spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)

# create the cs (chip select)
cs = digitalio.DigitalInOut(board.D22)

# create the mcp object
mcp = MCP.MCP3008(spi, cs)

# create an analog input channel on pin 0
chan0 = AnalogIn(mcp, MCP.P0)
chan7 = AnalogIn(mcp, MCP.P7)

# create midi interface
midi = MIDIInterface()

left_last_read = 0
right_last_read = 0
tolerance = 250


def remap_range(value, left_min, left_max, right_min, right_max):
    left_span = left_max - left_min
    right_span = right_max - right_min
    value_scaled = int(value - left_min) / int(left_span)
    return int(right_min + (value_scaled * right_span))


while True:

    # read the analog pin
    left_knob = chan0.value
    right_knob = chan7.value

    # how much have they changed since the last read
    left_adjust = abs(left_knob - left_last_read)
    right_adjust = abs(right_knob - right_last_read)

    if left_adjust > tolerance:
        # convert 16bit adc0 (0-65535) left knob read into 0-127 midi cc value
        pedal_value = remap_range(left_knob, 0, 65535, 0, 127)

        #knobs are upside down so reverse the value
        pedal_value = abs(pedal_value - 127)

        midi.send_cc_message(CC_EXPRESSION, 0, pedal_value)
        left_last_read = left_knob

    if right_adjust > tolerance:
        # convert 16bit adc0 (0-65535) right knob read into 0-127 midi cc value
        pedal_value = remap_range(right_knob, 0, 65535, 0, 127)

        #knobs are upside down so reverse the value
        pedal_value = abs(pedal_value - 127)
        
        midi.send_cc_message(CC_EXPRESSION, 7, pedal_value)
        right_last_read = right_knob

    time.sleep(0.0001)
