'''
This module provides helper functions and classes to be used in the live programs.


Stephan Kuschel, 2019
'''

import numpy as np



class RollingAverage():

    def __init__(self, length=10):
        self.length = length
        self.data = None
        self.i = 0  # next
        self.n = 0  # data processed

    def _initarray(self, data):
        s = np.asarray(data).shape
        self.data = np.zeros(tuple((self.length, *s)))

    def __array__(self, dtype=None):
        return np.asanyarray(self.average, dtype=dtype)  

    def __call__(self, data):
        '''
        add data to the rolling average
        '''
        if self.data is None:
            self._initarray(data)
        data = np.asarray(data)
        self.data[self.i] = data
        self.i = (self.i + 1) % self.length
        self.n += 1

    @property
    def average(self):
        '''
        returns the actural average
        '''
        endidx = -1 if self.n > self.i else self.i
        data = self.data[0:endidx]
        ret = np.mean(data, axis=0)
        return ret
        























