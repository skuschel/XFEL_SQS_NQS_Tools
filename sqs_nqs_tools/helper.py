'''
This module provides helper functions and classes to be used in the live programs.


Stephan Kuschel, Matt Ware, Catherine Saladrigas, 2019
'''

import numpy as np



class DataBuffer():

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
        return np.asanyarray(self.data, dtype=dtype)  

    def __call__(self, data):
        '''
        add data to the buffer
        '''
        if self._buffer is None:
            self._initarray(data)
        data = np.asarray(data)
        self._buffer[self.i] = data
        self.i = (self.i + 1) % self.length
        self.n += 1

    @property
    def buffer(self):
        if self._buffer is None:
            raise ValueError('Buffer contains no data')
        return self._buffer

    def __getitem__(self, idx):
        return self.data[idx]

    def __len__(self):
        return self.n if self.n < self.length else self.length

    def __iter__(self):
        return (d for d in self.data)

    @property
    def data(self):
        '''
        return the usable data from the buffer, sorted from old to new
        '''
        endidx = None if self.n > self.i else self.i
        data = self.buffer[0:endidx]
        start = 0 if self.i == self.n else self.i-self.length
        return np.roll(data, -self.i, axis=0)

    @property
    def average(self):
        '''
        returns the average of all buffered data.
        '''
        ret = np.mean(self.data, axis=0)
        return ret
        
    def normby(self, norm=np.sum):
        return [norm(el) for el in self]

    def max(self, norm=np.sum):
        '''
        returns the max in the buffer.
        reduce = np.sum:
            function which reduces each element in the buffer to a single scalar
            used to find the max.
        '''
        normvals = self.normby(norm)
        idx = np.argmax(norm)
        return self[idx]

#databuffer that keeps the data sorted by some value
class SortedBuffer(DataBuffer):
    def __init__(self, length=10):
        self.length = length
        self._buffer = None
        self.i = 0  # next
        self.n = 0  # data processed
        self.values = np.zeros(length)

    def __call__(self, data, value):
        '''
        add data to the buffer if its value is bigger than the smallest
        '''
        if self._buffer is None:
            self._initarray(data)
    
        data = np.asarray(data)

        if self.n < self.length:
            self._buffer[self.n] = data
            self.n += 1
            self.i += 1
        elif value >= np.min(self.values):
            self._buffer[0] = data #always replace the lowest value, we keep it sorted
            self.values[0] = value
            self.n += 1
            self.i = 0
            indx = np.argsort(self.values)
            self._buffer = self._buffer[indx]
            self.values = self.values[indx]

    @property
    def data(self):
        '''
        return the usable data from the buffer, sorted from old to new
        '''
        endidx = None if self.n > self.length else self.n
        return self.buffer[0:endidx]


class RollingAverage(DataBuffer):
    def __array__(self, dtype=None):
        return np.asanyarray(self.average, dtype=dtype)



class Accumulator():
    def __init__(self):
        '''
        An Accumulator for n-dimensional data.
        '''
        self._buffer = None
        self.n = 0

    def __call__(self, data):
        if self._buffer is None:
            self._buffer = np.array(data)  # a real copy. May be read-only otherwise
        else:
            self._buffer += data
        self.n += 1

    def __len__(self):
        return self.n

    @property
    def buffer(self):
        if self._buffer is None:
            raise ValueError('Buffer contains no data')
        return self._buffer

    @property
    def mean(self):
        return self.buffer / self.n










