'''
This module provides helper functions and classes to be used in the live programs.


Stephan Kuschel, Matt Ware, Catherine Saladrigas, 2019
'''

import numpy as np



class RollingAverage():

    def __init__(self, length=10):
        self.length = length
        self._buffer = None
        self.i = 0  # next
        self.n = 0  # data processed

    def _initarray(self, data):
        '''
        Initializes matrix of data for rolling average operation
        input:
            data for generation of rolling average
        '''
        s = np.asarray(data).shape
        self._buffer = np.zeros(tuple((self.length, *s)))

    def __array__(self, dtype=None):
        return np.asanyarray(self.average, dtype=dtype)  

    def __call__(self, data):
        '''
        add data to the rolling average
        '''
        if self._buffer is None:
            self._initarray(data)
        data = np.asarray(data)
        self._buffer[self.i] = data
        self.i = (self.i + 1) % self.length
        self.n += 1

    def __getitem__(self, idx):
        return _buffer[idx]

    def __len__(self):
        return self.i if self.i < self.length else self.length

    @property
    def data(self):
        '''
        return the usable data from the buffer
        '''
        endidx = -1 if self.n > self.i else self.i
        data = self._buffer[0:endidx]
        start = 0 if self.i == self.n else self.i-self.length
        return np.roll(data, -self.i)

    @property
    def average(self):
        '''
        returns the average of all buffered data.
        '''
        ret = np.mean(self.data, axis=0)
        return ret
        

    @property
    def max(self):
        '''
        returns the max in the buffer
        '''
        assert False
        ret = np.mean(self.data, axis=0)
        return ret




















