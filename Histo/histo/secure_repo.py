class secure_repo:
    def __init__(self, root, key):
        import os
        from .repo import repo
        self._root = root
        self._index_output = self._create_secure_dfile(os.path.join(root, 'index'), 'i{:06d}')
        self._data_output = self._create_secure_dfile(os.path.join(root, 'data'), 'd{:06d}')
        self._repo = repo(self._index_output, self._data_output)
        self._key = key
    
    def commit_file(self, filename, name, summary, time = None):
        self._repo.commit_file(filename, name, summary, time)
    
    def __enter__(self):
        self._index_output.__enter__()
        self._data_output.__enter__()
        return self
    
    def __exit__(self,*k):
        self._index_output.__exit__(*k)
        self._data_output.__exit__(*k)
    
    def _create_secure_dfile(self, folder, idformat):
        import dfile
        from dfile.files.files import files
        from dfile.bundle.crypto.bundle import bundle as crypto_bundle
        from dfile.bundle.local.bundle import bundle as local_bundle
        cipher = self._create_cipher()
        bundle = local_bundle(folder, idformat)
        bundle = crypto_bundle(bundle, cipher)
        return dfile.writer(files(bundle))
    
    def _create_cipher(self):
        from cipher.aes.cipher import cipher
        return cipher(self._key)