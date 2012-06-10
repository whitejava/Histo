class format:
    def check(self, c):
        if type(c) != tuple:
            return False
        if len(c) != 6:
            return False
        for e in c:
            if type(e) != tuple:
                return False
            if len(e) != 2:
                return False
        keys = ['version','commit_time','name','last_modify','range','files']
        for a,b in zip([e[0] for e in c],keys):
            if a != b:
                return False
        if not self._check_version(c[0][1]):
            return False
        if not self._check_commit_time(c[1][1]):
            return False
        if not self._check_name(c[2][1]):
            return False
        if not self._check_last_modify(c[3][1]):
            return False
        if not self._check_range(c[4][1]):
            return False
        if not self._check_files(c[5][1]):
            return False
        return True
    
    def _check_version(self,v):
        if type(v) != int:
            return False
        if v != 0:
            return False
        return True
    
    def _check_commit_time(self,v):
        return self._check_time(v)
    
    def _check_time(self,v):
        if type(v) != tuple:
            return False
        if len(v) <= 0:
            return False
        for e in v:
            if type(e) != int:
                return False
        return True
    
    def _check_last_modify(self,v):
        return self._check_time(v)
    
    def _check_range(self,v):
        if type(v) != tuple:
            return False
        if len(v) != 2:
            return False
        for e in v:
            if type(e) != int:
                return False
            if e < 0:
                return False
        if v[0] > v[1]:
            return False
        return True
    
    def _check_files(self,v):
        if type(v) != tuple:
            return False
        for e in v:
            if type(e) != str:
                return False
        return True
    
    def _check_name(self,v):
        if type(v) != str:
            return False
        return True