import unittest

class test(unittest.TestCase):
    def test_raise_error(self):
        with self._expect_error('test error'):
            raise Exception('test error')
    
    def test_no_error(self):
        with self._expect_error('expect exception'):
            with self._expect_error('no error'):
                pass

    def test_no_message_exception(self):
        with self._expect_error('unexpected message: '):
            with self._expect_error('empty error'):
                raise Exception()
    
    def test_double_with(self):
        e = self._expect_error('test error')
        with e:
            with e:
                raise Exception('test error')
            raise Exception('test error')
    
    def test_unexpected_exception(self):
        with self._expect_error('unexpected message: unexpected'):
            with self._expect_error('message'):
                raise Exception('unexpected')
    
    def _expect_error(self, message):
        from .expect_error import expect_error
        return expect_error(message)