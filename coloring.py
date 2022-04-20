from re import X
import matplotlib.cm
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from pyrsistent import l

cmap = matplotlib.cm.get_cmap('turbo')
list_colors_edges = [cmap(comm_color) for comm_color in np.linspace(0,1,4)]
print(list_colors_edges)
norm = matplotlib.colors.Normalize(vmin=-2, vmax=2)
for i in np.linspace(0,1,100):
    rgba = cmap(i)
    print(rgba)
    x = np.linspace(0, 10, 1000)
    plt.plot(x, np.sin(x+i), color=rgba)


plt.show()