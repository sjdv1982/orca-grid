import numpy as np
space = np.linspace(-1, 1, 150)
x = space[:, None, None]
y = space[None, :, None]
z = space[None, None, :]
#arr = np.maximum(-1, 100-80*(x**2+(y/2)**2+z**2),dtype=np.float32)
print(coor.shape, voxelsize)
mins = coor.min(axis=0)
maxes = coor.max(axis=0)
bounds=np.max([-mins, maxes],axis=0)
center = (bounds/voxelsize+0.999).astype(np.int)
dims = center * 2 + 1
arr = np.zeros(shape=dims, dtype=np.float32)
coor_grid = (coor / voxelsize+0.5).astype(int) + center
for c in coor_grid:
    arr[c[0], c[1], c[2]] += 1.0
result = arr
