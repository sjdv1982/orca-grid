import numpy as np
space = np.linspace(-1, 1, 150)
x = space[:, None, None]
y = space[None, :, None]
z = space[None, None, :]
arr = np.maximum(-1, 100-80*(x**2+(y/2)**2+z**2))
result = arr
