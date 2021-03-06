import sys
import unittest
from glob import glob

import numpy as np


class NotAvailable(SystemExit):
    def __init__(self, msg, code=0):
        SystemExit.__init__(self, (msg,code,))
        self.msg = msg
        self.code = code

# -------------------------------------------------------------------

# Custom test case/suite for embedding unittests in the test scripts

if sys.version_info < (2, 4, 0, 'final', 0):
    class CustomTestCase(unittest.TestCase):
        assertTrue = unittest.TestCase.failUnless
        assertFalse = unittest.TestCase.failIf
else:
    from unittest import TestCase as CustomTestCase

from ase.parallel import paropen

class CustomTextTestRunner(unittest.TextTestRunner):
    def __init__(self, logname, descriptions=1, verbosity=1):
        self.f = paropen(logname, 'w')
        unittest.TextTestRunner.__init__(self, self.f, descriptions, verbosity)

    def run(self, test):
        stderr_old = sys.stderr
        try:
            sys.stderr = self.f
            testresult = unittest.TextTestRunner.run(self, test)
        finally:
            sys.stderr = stderr_old
        return testresult

# -------------------------------------------------------------------

class ScriptTestCase(unittest.TestCase):
    def __init__(self, methodname='testfile', filename=None, display=True):
        unittest.TestCase.__init__(self, methodname)
        self.filename = filename
        self.display = display
        
    def testfile(self):
        try:
            execfile(self.filename, {'display': self.display})
        except KeyboardInterrupt:
            raise RuntimeError('Keyboard interrupt')
        except NotAvailable, err:
            # Only non-zero error codes are failures
            if err.code:
                raise

    def id(self):
        return self.filename

    def __str__(self):
        return '%s (ScriptTestCase)' % self.filename.split('/')[-1]

    def __repr__(self):
        return "ScriptTestCase(filename='%s')" % self.filename


def test(verbosity=1, dir=None, display=True, stream=sys.stdout):
    ts = unittest.TestSuite()
    if dir is None:
        dir = __path__[0]
    tests = glob(dir + '/*.py')
    tests.sort()
    for test in tests:
        if test.endswith('__init__.py'):
            continue
        if test.endswith('COCu111.py'):
            lasttest = test
            continue
        ts.addTest(ScriptTestCase(filename=test, display=display))
    ts.addTest(ScriptTestCase(filename=lasttest, display=display))

    from ase.utils import devnull
    sys.stdout = devnull
    
    ttr = unittest.TextTestRunner(verbosity=verbosity, stream=stream)
    results = ttr.run(ts)

    sys.stdout = sys.__stdout__

    return results


class World:
    """Class for testing parallelization with MPI"""
    def __init__(self, size):
        self.size = size
        self.data = {}
        
    def get_rank(self, rank):
        return CPU(self, rank)

class CPU:
    def __init__(self, world, rank):
        self.world = world
        self.rank = rank
        self.size = world.size

    def send(self, x, rank):
        while (self.rank, rank) in self.world.data:
            pass
        self.world.data[(self.rank, rank)] = x

    def receive(self, x, rank):
        while (rank, self.rank) not in self.world.data:
            pass
        x[:] = self.world.data.pop((rank, self.rank))
    
    def sum(self, x):
        if not isinstance(x, np.ndarray):
            x = np.array([x])
            self.sum(x)
            return x[0]

        if self.rank == 0:
            y = np.empty_like(x)
            for rank in range(1, self.size):
                self.receive(y, rank)
                x += y
        else:
            self.send(x, 0)

        self.broadcast(x, 0)

    def broadcast(self, x, root):
        if self.rank == root:
            for rank in range(self.size):
                if rank != root:
                    self.send(x, rank)
        else:
            self.receive(x, root)
