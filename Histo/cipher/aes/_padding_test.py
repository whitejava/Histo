    def test_padding(self):
        self._input = hex.decode('00'*11)
        
        c = cipher(self.key)
        p = c._padding(tobytes('00'*11))
        self.assertEquals(p, tobytes('00'*11 + '05'*5))
        self.assertEquals(c._padding(tobytes('00'*16)), tobytes('00'*16+'10'*16))
    
    def test_unpadding(self):
        c = cipher(self.key)
        t = c._unpadding(tobytes('00'*11 + '05'*5))
        self.assertEquals(t, tobytes('00'*11))
        
    def test_bad_padding(self):
        c = cipher(self.key)
        with self.assertRaises(bad_padding_error):
            c._unpadding(tobytes('00'*16))
            
    def test_empty_bad_padding(self):
        c = cipher(self.key)
        with self.assertRaises(bad_padding_error):
            c._unpadding(b'')