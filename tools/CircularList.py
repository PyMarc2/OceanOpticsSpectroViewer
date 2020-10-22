"""Module containing the circular list class"""
import numpy as np


class CircularList():
    """FIFO style buffer class
    List of fixed size where appended data overwrites the oldest entries
    Args:
        size (int, optional): Length of the array to reserve. Defaults
            to 0.
    """
    def __init__(self, size: int = 0) -> None:
        self._index = 0
        self._size = size
        self._data = np.array([])
        self.reset(self._size)

    def __getitem__(self, index: int) -> float:
        return self._data[(self._index+index) % self._size]

    def __len__(self):
        return self._size

    def __array__(self):
        return np.append(self._data[self._index:], self._data[:self._index])

    def append(self, data: list) -> None:
        """Replace the oldest entries in the buffer by those in data
        Args:
            data (list): New data of variable length
        """
        try:
            self._data[self._index:self._index+len(data)] = data
        except ValueError:
            self._data[self._index:] = data[:self._size-self._index]
            self._data[:(self._index+len(data)) % self._size] = \
                data[self._size-self._index:]
        finally:
            self._index = (self._index+len(data)) % self._size

    def reset(self, size: int = None) -> None:
        """Reset the buffer
        Resizes the buffer to the specified size if not None, fills
        the array with np.nan and resets the index back to 0.
        Args:
            size (int, optional): Length of the array to reserve.
                Defaults to None.
        """
        self._index = 0
        if size is not None:
            self._size = size
            self._data = np.zeros(self._size)
        self._data.fill(np.nan)


class RingBuffer:
    """ class that implements a not-yet-full buffer """
    def __init__(self, size_max):
        self.max = size_max
        self.data = []

    def __call__(self):
        return self.data

    class __Full:
        """ class that implements a full buffer """
        def append(self, x):
            """ Append an element overwriting the oldest one. """
            self.data[self.cur] = x
            self.cur = (self.cur+1) % self.max

        def get(self):
            """ return list of elements in correct order """
            return self.data[self.cur:]+self.data[:self.cur]

        def __call__(self):
            return self.data

    def append(self,x):
        """append an element at the end of the buffer"""
        self.data.append(x)
        if len(self.data) == self.max:
            self.cur = 0
            # Permanently change self's class from non-full to full
            self.__class__ = self.__Full

    def get(self):
        """ Return a list of elements from the oldest to the newest. """
        return self.data
