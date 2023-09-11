import matplotlib.pyplot as plt
import numpy as np

# Define your two colors in RGB format
color1 = (1, 0, 0)  # Red
color2 = (0, 0, 1)  # Blue

# Create a custom colormap with your two colors
cmap = plt.cm.colors.LinearSegmentedColormap.from_list('custom_colormap', [color1, color2], N=256)

# Your value between 0 and 1 (where 0 corresponds to color1 and 1 corresponds to color2)
value = 0.8

# Create a colorbar for reference
plt.imshow([[value]], cmap=cmap, aspect='auto', extent=[0, 1, 0, 1])
plt.colorbar(label='Value')

# Create a gradient image
gradient = np.linspace(0, 1, 256).reshape(1, -1)
plt.imshow(gradient, cmap=cmap, aspect='auto', extent=[0, 1, 2, 3])

# Add an arrow annotation to point to the value on the gradient
arrow_props = dict(facecolor='black', arrowstyle='->')
plt.annotate(f'Value: {value:.2f}', xy=(value, 2.5), xytext=(0.7, 2.7),
             arrowprops=arrow_props, fontsize=12, color='black')

# Display the plot
plt.axis('off')
plt.show()
