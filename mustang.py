import time
import busio
import digitalio
import board
import RPi.GPIO as GPIO
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn
from amidiw import MIDIInterface
from amidiw import CC_ON

# set midi cc codes
CC_BUTTON_LEFT = 80
CC_BUTTON_RIGHT = 81
CC_EXPRESSION = 11

# set up pins for push buttons
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(12, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(18, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

# create the spi bus
spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)

# create the cs (chip select)
cs = digitalio.DigitalInOut(board.D22)

# create the mcp object
mcp = MCP.MCP3008(spi, cs)

# create an analog input channel on pin 0
chan0 = AnalogIn(mcp, MCP.P0)

# create midi interface
midi = MIDIInterface()

last_read = 0
tolerance = 250
left_pressed = False
right_pressed = False


def remap_range(value, left_min, left_max, right_min, right_max):
    left_span = left_max - left_min
    right_span = right_max - right_min
    value_scaled = int(value - left_min) / int(left_span)
    return int(right_min + (value_scaled * right_span))


while True:

    if GPIO.input(12) == GPIO.HIGH:
        if not left_pressed:
            left_pressed = True
            midi.send_cc_message(CC_BUTTON_LEFT, CC_ON)
    else:
        left_pressed = False
        
    if GPIO.input(18) == GPIO.HIGH:
        if not right_pressed:
            right_pressed = True
            midi.send_cc_message(CC_BUTTON_RIGHT, CC_ON)
    else:
        right_pressed = False
    
    trim_pot_changed = False

    # read the analog pin
    trim_pot = chan0.value

    # how much has it changed since the last read
    pot_adjust = abs(trim_pot - last_read)

    if pot_adjust > tolerance:
        trim_pot_changed = True

    if trim_pot_changed:
        # convert 16bit adc0 (0-65535) trim pot read into 0-127 midi cc value
        pedal_value = remap_range(trim_pot, 0, 65535, 0, 127)
        midi.send_cc_message(CC_EXPRESSION, pedal_value)
        last_read = trim_pot

    time.sleep(0.0001)
