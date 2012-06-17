import unittest
from io import BytesIO
from .loader import loader
from .writer import writer
from ._test_common import common

class test(unittest.TestCase):
    def test_load(self):
        s = [common().sample, common().sample2]
        io = BytesIO()
        with writer(io) as f:
            for e in s:
                f.write(e)
        actual = loader(BytesIO(io.getvalue())).load()
        self.assertEquals(s, actual)