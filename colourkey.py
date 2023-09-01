import matplotlib.pyplot as plt
import matplotlib
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import FancyArrowPatch

# Define cmap_data in this script



def save_color_key_image(num1, num2, player1, player2, outcome):
    cmap_data = {
        'red': [(0.0, 1.0, 1.0),
                (0.5, 0.8, 0.8),  # Light grey has an RGB value of (0.8, 0.8, 0.8)
                (1.0, 0.0, 0.0)],

        'green': [(0.0, 0.0, 0.0),
                  (0.5, 0.8, 0.8),  # Light grey
                  (1.0, 0.5, 0.5)],

        'blue': [(0.0, 0.0, 0.0),
                 (0.5, 0.8, 0.8),  # Light grey
                 (1.0, 0.0, 0.0)]
    }
    cm = LinearSegmentedColormap('custom_cmap', cmap_data)  # Use cmap_data defined in this script

    fig, ax = plt.subplots(figsize=(6, 4))  # Increased width to accommodate arrows and labels
    cax, _ = matplotlib.colorbar.make_axes(ax)

    # Adjust the position of the colorbar to leave space for the arrow and labels
    cax.set_position([0.2, 0.2, 0.03, 0.6])

    cbar = matplotlib.colorbar.ColorbarBase(cax, cmap=cm, norm=matplotlib.colors.Normalize(vmin=-10, vmax=10))
    cbar.set_ticks([-10, 10])

    # Set the tick labels to white
    cbar.ax.tick_params(axis='y', colors='white')

    cbar.set_ticklabels(['-10 (High Negative Threat)', '10 (High Positive Threat)'])

    # Calculate arrow positions based on num1 and num2
    arrow1_y = (num1 + 10) / 20.0  # Map num1 to a position between 0 and 1
    arrow2_y = (num2 + 10) / 20.0  # Map num2 to a position between 0 and 1

    # Add arrow1 on the left pointing right with white color
    arrow1 = FancyArrowPatch((-0.2, arrow1_y), (0.1, arrow1_y), arrowstyle='-|>', color='white', mutation_scale=20)
    ax.add_patch(arrow1)

    # Add arrow2 on the right pointing left with white color
    arrow2 = FancyArrowPatch((0.3, arrow2_y), (0.2, arrow2_y), arrowstyle='-|>', color='white', mutation_scale=20)
    ax.add_patch(arrow2)

    # Add labels with values next to the arrows in white color
    ax.text(0, arrow1_y + 0.05, str(round(num1,2)), va='center', ha='left', fontsize=12, color='white')
    ax.text(0.3, arrow2_y + 0.05, str(round(num2,2)), va='center', ha='right', fontsize=12, color='white')

    ax.axis('off')
    if outcome == 1:
        fig.savefig(f'static/images/color_key_success/{player1}_{player2}.png', bbox_inches='tight', transparent=True)
    else:
        fig.savefig(f'static/images/color_key_unsuccess/{player1}_{player2}.png', bbox_inches='tight', transparent=True)
    plt.close(fig)

