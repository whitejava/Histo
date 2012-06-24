from pctest import test_case

class test(test_case):
    def setUp(self):
        self.script_file = __file__
        self.test_folder = '_archive'
    
    def test_normal(self):
        self._filename = 'normal.rar'
        self.do()
        self.expect(('test', ('rar', None, (('a', (('1', None), ('3', None), ('2', None))),))))
    
    def test_bad(self):
        self._filename = 'bad.rar'
        self.do()
        self.expect(('test', ('rar', 'extract error 10', ())))
    
    def test_encrypt(self):
        self._filename = 'encrypt.rar'
        self.do()
        self.expect(('test', ('rar', 'extract error 1', (('a', ()),))))
    
    def test_embed(self):
        self._filename = 'embed.rar'
        self.do()
        self.expect(('test', ('rar', None, (('embed1.rar', ('rar', None, (('normal.rar', ('rar', None, (('a', (('b', None), ('d', None), ('c', None))),))), ('normal2.rar', ('rar', None, (('a', (('b', None), ('d', None), ('c', None))),)))))), ('embed2.rar', ('rar', None, (('normal.rar', ('rar', None, (('a', (('b', None), ('d', None), ('c', None))),))), ('normal2.rar', ('rar', None, (('a', (('b', None), ('d', None), ('c', None))),)))))), ('embed3.rar', ('rar', None, (('normal.rar', ('rar', None, (('a', (('b', None), ('d', None), ('c', None))),))), ('normal2.rar', ('rar', None, (('a', (('b', None), ('d', None), ('c', None))),))))))))))
    
    def do2(self):
        from summary import generate_summary
        return generate_summary('test', self.get_test_file(self._filename))
    
    