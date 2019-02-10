


import numpy as np
import json
from itertools import product, count

CONFIG = {
    'activation_pin' : 'c',
    'output_port' : 'a'
}


class Controller:
    def __init__(self):
        with open('controller-template.lua', 'r') as file:
            self.template = file.read()

    def compile(self, **kwargs):
        kwargs.update(CONFIG)
        program = self.template
        for key, value in kwargs.items():
            program = program.replace('%{}%'.format(key.replace('_', '-')), value)
        return program


class Digit(Controller):
    def __init__(self, type, index):
        assert type.lower() in ('h', 'm', 's') and index >= 0
        super().__init__()

        self.pixels = np.load('../data/pixels.npy')
        self.type = type.lower()
        self.index = index

    def compile_pixel(self, row, col):
        activations = self.pixels[row, col, :].flatten()

        if self.type == 'm':
            interval = '60 - time.sec'
        elif self.type == 'h':
            interval = '60 * (60 - time.min) + (60 - time.sec)'
        else:
            interval = '1'

        input = ('math.floor(time.{} / 10) + 1' if self.index == 0 else 'time.{} % 10 + 1').format({'h':'hour', 'm':'min', 's':'sec'}[self.type])

        return super().compile(
            activations=', '.join(['true' if value else 'false' for value in activations]),
            input=input,
            interval=interval
        )

    def compile(self):
        data = []
        for row, col in product(range(0, 5), range(0, 3)):
            data.append({
                'row': row,
                'col': col,
                'script':self.compile_pixel(row, col)
            })
        return data



class Display:
    def __init__(self, type):
        self.digits = [Digit(type, 0), Digit(type, 1)]

    def compile(self):
        data = []
        for index, digit in zip(count(0), self.digits):
            data.append({
                'digit':index,
                'pixels':digit.compile()
            })
        return data


class Clock:
    def __init__(self, format):
        self.format = format.lower()

    def compile(self):
        data = {}
        for c in self.format:
            data[c] = Display(c).compile()
        return data

    def to_json(self, filename):
        with open(filename, 'w') as file:
            json.dump(self.compile(), file)

if __name__ == '__main__':
    Clock('HM').to_json('../data/clock[hh-mm].json')
    Clock('MS').to_json('../data/clock[mm-ss].json')
    Clock('HMS').to_json('../data/clock[hh-mm-ss].json')
