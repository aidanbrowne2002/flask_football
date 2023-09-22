import matplotlib.pyplot as plt
import numpy as np

def save_color_key_image(num1, num2, player1, player2, outcome, names, box_width=0.83):
    # Create a list to hold the numbers and labels
    fig, ax = plt.subplots()

    # Calculate the mean of the data
    means = [np.mean(num1), np.mean(num2)]

    # Customize the plot
    ax.set_title('Threat levels', fontsize=40, color='white')
    ax.set_ylabel('Threat', fontsize=40, color='white')
    ax.tick_params(axis='both', labelsize=40, color='white')

    for label in ax.get_xticklabels() + ax.get_yticklabels():
        label.set_fontsize(40)
        label.set_color('white')

    ax.set_ylim(-2, 2)
    fig.set_size_inches(12, 15)

    fig.patch.set_facecolor('none')

    # Plot median lines as horizontal lines
    for i, mean in enumerate(means):
        ax.hlines(y=mean, xmin=i + 1 - box_width / 2, xmax=i + 1 + box_width / 2,
                  color='green', linestyle='-', linewidth=8,
                  label=f'Mean {names[i]}: {mean:.2f}')

    if outcome == 1:
        fig.savefig(f'static/images/color_key_success/{player1}_{player2}.png', bbox_inches='tight', transparent=True)
    else:
        fig.savefig(f'static/images/color_key_unsuccess/{player1}_{player2}.png', bbox_inches='tight', transparent=True)
    plt.close(fig)
