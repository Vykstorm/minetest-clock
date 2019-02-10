'''
The clock is composed by four digits. The first ones indicates the hour and
the second ones the minutes (on minetest server time)

We will have a total of 4 digits: hh-mm (with indexes from 0 to 3)

Each digit will have a display of size 5x3 pixels (5 rows and 3 columns)
And each pixel will have an associated lua micro controller (a special
minetest mesecon component which can be programmed using lua code)

Each lua micro-controller will be responsible to set the current state of
its associated pixel in the display

The class Clock defined below has a method called get_lua_code that can be
used to generate the code that must be inserted to a specific micro-controller
so that the clock is working properly

e.g:
Clock().get_lua_code(digit_index=1, row=2, col=0) will return the lua
code for the micro-controller associated to a pixel in the display of the
2nd clock digit with coordinates (2,0) -> at second row and first column

The next ascii text shows a possible output configuration of the clock's pixels
'#' means the pixel is activated and '.' for disabled


        1st      2nd         3rd      4th     -> th-digit
     0  1  2   0  1  2     0  1  2   0  1  2  -> col
0    #  .  .   #  #  #     #  #  #   #  .  #
1    #  .  .   #  .  #     .  .  #   #  .  #
2    #  .  .   #  #  #  :  #  #  #   #  #  #
3    #  .  .   #  .  #     .  .  #   .  .  #
4    #  .  .   #  #  #     #  #  #   .  .  #
|
row



Depending what direction your clock is facing forward, you must change the
clock configuration; Three variables named 'output_port' and 'activation_pin',
'always_active' must be tunned

always_active can be true/false. If set to true, the clock will be always
enabled and the parameter 'activation_pin' will be ignored

activation_pin can be set to indicate a specific pin on the lua micro-controllers
to be used to enable/disable the clock

output_port must be set to the port used by micro-controllers to send their
current pixel states



The next ascii chars show a lua controller for one pixel of the clock
The activation signal will come from the A pin and the pixel state is sent
to the port C

    e/d signal
        |
-----------------
|       A       |
|  B         C  | -> pixel state
|       D       |
-----------------


You can execute the next lines of code to configure your clock:
clock = Clock()
clock.activation_pin = 'a'
clock.output_port = 'c'
clock.always_active = False
'''



import numpy as np
import json
from itertools import product, count
from singleton import singleton
from re import sub
import re


def render_template(filename, **kwargs):
    def parse_value(x):
        if isinstance(x, (list, tuple)):
            return ', '.join([parse_value(item) for item in x])

        if isinstance(x, bool):
            return 'true' if x else 'false'

        if not isinstance(x, str):
            return repr(x)
        return str(x)

    with open(filename, 'r') as file:
        text = file.read()

    for key, value in kwargs.items():
        text = text.replace('%' + key.lower() + '%', parse_value(value))
        text = text.replace('%' + key.upper() + '%', parse_value(value).upper())

    def block_if_else(match):
        predicate_var = match.group(1)
        first_block = match.group(2)
        second_block = match.group(3)
        return first_block if kwargs[predicate_var] else second_block

    text = sub("[ \t]*{%[ ]*if ([^%]+) %}[^\n]*\n([^{]+){%[ ]*else[ ]*%}[^\n]*\n([^{]+){%[ ]*end[ ]*%}[ \t]*",
        block_if_else,
        text,
        flags=re.DOTALL)


    return text

@singleton
class Clock:
    def __init__(self, **kwargs):
        self.pixels = np.load('../data/pixels.npy')
        self._activation_pin = 'c'
        self._output_port = 'a'
        self._always_enabled = False


    # You can configure the clock using the next properties
    @property
    def activation_pin(self):
        return self._activation_pin

    @activation_pin.setter
    def activation_pin(self, pin):
        assert pin.lower() in ('a', 'b', 'c', 'd')
        self._activation_pin = pin.lower()

    @property
    def output_port(self):
        return self._output_port

    @output_port.setter
    def output_port(self, port):
        assert port.lower() in ('a', 'b', 'c', 'd')
        self._output_port = port.lower()

    @property
    def always_enabled(self):
        return self._always_enabled

    @always_enabled.setter
    def always_enabled(self, enabled):
        assert isinstance(enabled, bool)
        self._always_enabled = enabled


    def get_microcontroller_lua_code(self, digit_index, row, col):
        '''
        Returns the lua code for a specific micro-controller
        '''

        # Value of the digit shown on the display
        value = ('math.floor({} / 10) + 1' if (digit_index % 2) == 0 else '{} % 10 + 1').format(
            'time.hour' if digit_index < 2 else  'time.min')

        # Amount of secs to elapse before the next pixel update (in server seconds)
        interval = '60 * (60 - time.min) + (60 - time.sec)' if digit_index < 2 else '60 - time.sec'

        # Each possible pixel state depending on the digit input value
        states = [bool(state) for state in self.pixels[row, col, :].flatten()]

        # Small header on the lua script to provide additional info
        cardinals = ['1st', '2nd', '3th', '4th']
        header = '-- Code for pixel with coordinates ({}, {}) at the {} digit'.format(row, col, cardinals[digit_index])

        # Get the lua code and return it
        return render_template('controller.lua',
            input=value,
            states=states,
            activation_pin=self.activation_pin,
            output_port=self.output_port,
            always_enabled=self.always_enabled,
            interval=interval,
            header=header)

    def get_code(self):
        code = ''
        for digit_index, row, col in product(range(0, 4), range(0, 5), range(0, 3)):
            body = self.get_microcontroller_lua_code(digit_index, row, col)
            code += '~' * 30 + '\n\n' + body + '~' * 30 + '\n\n'
        return code

    def save_code(self, filename):
        with open(filename, 'w') as file:
            file.write(self.get_code())


if __name__ == '__main__':
    clock = Clock()
    clock.always_enabled = False
    clock.activation_pin = 'c'
    clock.output_port = 'a'
    clock.save_code('../data/microcontrollers-code.txt')
