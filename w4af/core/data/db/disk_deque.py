from functools import total_ordering

from w4af.core.data.db.disk_dict import DiskDict

@total_ordering
class DiskDeque(object):
    """
    The base code for this file comes from [0], I've modified it to use a
    DiskDict which stores the "self.data" dictionary to disk in order to save
    memory.

    [0] https://code.activestate.com/recipes/259179/
    """

    def __init__(self, iterable=(), maxsize=-1):
        if not hasattr(self, 'data'):
            self.left = self.right = 0
            self.data = DiskDict(table_prefix='deque')
        self.maxsize = maxsize
        self.extend(iterable)

    def append(self, x):
        self.data[self.right] = x
        self.right += 1
        if self.maxsize != -1 and len(self) > self.maxsize:
            self.popleft()

    def appendleft(self, x):
        self.left -= 1
        self.data[self.left] = x
        if self.maxsize != -1 and len(self) > self.maxsize:
            self.pop()

    def pop(self):
        if self.left == self.right:
            raise IndexError('cannot pop from empty deque')
        self.right -= 1
        elem = self.data[self.right]
        del self.data[self.right]
        return elem

    def popleft(self):
        if self.left == self.right:
            raise IndexError('cannot pop from empty deque')
        elem = self.data[self.left]
        del self.data[self.left]
        self.left += 1
        return elem

    def clear(self):
        self.data.cleanup()
        self.left = self.right = 0

    def extend(self, iterable):
        for elem in iterable:
            self.append(elem)

    def extendleft(self, iterable):
        for elem in iterable:
            self.appendleft(elem)

    def rotate(self, n=1):
        if self:
            n %= len(self)
            for i in range(n):
                self.appendleft(self.pop())

    def __getitem__(self, i):
        if i < 0:
            i += len(self)
        try:
            return self.data[i + self.left]
        except KeyError:
            raise IndexError

    def __setitem__(self, i, value):
        if i < 0:
            i += len(self)
        try:
            self.data[i + self.left] = value
        except KeyError:
            raise IndexError

    def __delitem__(self, i):
        size = len(self)
        if not (-size <= i < size):
            raise IndexError
        data = self.data
        if i < 0:
            i += size
        for j in range(self.left+i, self.right-1):
            data[j] = data[j+1]
        self.pop()

    def __len__(self):
        return self.right - self.left

    def __eq__(self, other):
        if type(self) != type(other):
            return False
        return list(self) == list(other)

    def __ne__(self, other):
        if type(self) != type(other):
            return True
        return list(self) != list(other)

    def __lt__(self, other):
        return list(self) < list(other)

    def __repr__(self, _track=[]):
        if id(self) in _track:
            return '...'
        _track.append(id(self))
        r = 'deque(%r)' % (list(self),)
        _track.remove(id(self))
        return r

    def __getstate__(self):
        return tuple(self)

    def __setstate__(self, s):
        self.__init__(s[0])

    def __hash__(self):
        raise TypeError

    def __copy__(self):
        return self.__class__(self)

    def __deepcopy__(self, memo={}):
        from copy import deepcopy
        result = self.__class__()
        memo[id(self)] = result
        result.__init__(deepcopy(tuple(self), memo))
        return result

