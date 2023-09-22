import matplotlib.pyplot as plt
import numpy as np


def save_color_key_image(num1, num2, player1, player2, outcome, names, box_width=0.83):
    # Create a list to hold the numbers and labels
    fig, ax = plt.subplots()

    # Create boxplots for the datasets with larger markers and labels
    data = [num1, num2]
    positions = [1, 2]  # Define positions for the boxplots
    box = ax.boxplot(data, positions=positions, labels=[names[0], names[1]], patch_artist=True,
                     boxprops=dict(facecolor='lightblue'), widths=0.8, showfliers=False, whis=0,
                     whiskerprops={'linestyle': '', 'linewidth': 0})  # Remove whiskers

    # Calculate the mean of the data
    means = [np.mean(num1), np.mean(num2)]

    # Customize the plot
    ax.set_title('Threat levels', fontsize=40, color = 'white')
    ax.set_ylabel('Threat', fontsize=40, color = 'white')
    ax.tick_params(axis='both', labelsize=40, color = 'white')

    for label in ax.get_xticklabels() + ax.get_yticklabels():
        label.set_fontsize(40)
        label.set_color('white')

    for element in ['boxes', 'whiskers', 'medians', 'caps']:
        plt.setp(box[element], linewidth=8)

    ax.set_ylim(-2, 2)
    fig.set_size_inches(12, 15)
    ax.legend()

    fig.patch.set_facecolor('none')

    # Plot means as horizontal lines spanning the width of each boxplot
    for i, mean in enumerate(means):
        ax.hlines(y=mean, xmin=positions[i] - box_width / 2, xmax=positions[i] + box_width / 2,
                  color='green', linestyle='-', linewidth=8,
                  label=f'Mean {names[i]}: {mean:.2f}')

    if outcome == 1:
        fig.savefig(f'static/images/color_key_success/{player1}_{player2}.png', bbox_inches='tight', transparent=True)
    else:
        fig.savefig(f'static/images/color_key_unsuccess/{player1}_{player2}.png', bbox_inches='tight', transparent=True)
    plt.close(fig)

# Example usage:
# save_color_key_image([1, 2, 3], [4, 5, 6], "Player1", "Player2", 1, ["Dataset1", "Dataset2"], box_width=0.8)  # Adjust box_width as needed
