import numpy as np
from mrcfile.mrcfile import MrcFile, MrcInterpreter

from io import BytesIO
class MyBytesIO(BytesIO):
    def close(self):
        self.myvalue = self.getvalue()
        super().close()


class MemoryMrcFile(MrcFile):

    def __init__(self, bytes_io, mode='r', permissive=False,
                 header_only=False, **kwargs):
        MrcInterpreter.__init__(self, permissive=permissive, **kwargs)
        if not isinstance(bytes_io, BytesIO):
            raise TypeError(bytes_io)
                
        self._mode = mode
        self._read_only = (self._mode == 'r')
        
        self._iostream = bytes_io
        
        try:
            if 'w' in mode:
                self._create_default_attributes()
            else:
                self._read(header_only)
        except Exception:
            self._iostream.close()
            raise    

arr = arr.unsilk.astype(np.float32)
mrc_buffer = MyBytesIO()
mrc_file = MemoryMrcFile(mrc_buffer, mode="w+")
data = arr
mrc_file.set_data(data)
mrc_file.voxel_size = voxelsize
mrc_file.header.ispg = 0
del mrc_file
result = mrc_buffer.myvalue
