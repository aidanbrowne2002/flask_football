import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np

def save_color_key_image(value1, value2, player1, player2, outcome, names, box_width=0.83):
    mean_value1 = np.mean(value1)
    mean_value2 = np.mean(value2)

    # Check if mean values are within the valid range [-2, 2]
    #if abs(mean_value1) > 2 or abs(mean_value2) > 2:
        #raise ValueError("Mean values must be between -2 and 2")

    if outcome == 1:
        img = mpimg.imread('static/images/passing_success.png')  # Replace 'background_image.png' with your image file
    else:
        img = mpimg.imread('static/images/passing_fail.png')

    # Create a tall and skinny figure
    fig, ax = plt.subplots(figsize=(3, 6))  # Adjust the width and height as needed

    # Display the image
    ax.imshow(img, extent=[-0.5, 0.5, -2, 2])  # Adjust x-axis range here

    # Plot arrows with y positions based on the mean values
    arrow_length = 0.2  # Length of the arrows
    ax.arrow(-1, mean_value1, arrow_length, 0, head_width=0.1, head_length=0.2, fc='orange', ec='orange')  # Left to right
    ax.arrow(1, mean_value2, -arrow_length, 0, head_width=0.1, head_length=0.2, fc='orange', ec='orange')  # Right to left

    # Add mean labels near the arrows
    ax.text(-1, mean_value1+0.15, f'{mean_value1:.2f}', ha='left', va='center', color='w', fontsize=12)
    ax.text(1, mean_value2+0.15, f'{mean_value2:.2f}', ha='right', va='center', color='w', fontsize=12)

    # Remove labels and legend
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_xlabel('')
    ax.set_ylabel('')
    ax.legend().set_visible(False)
    ax.axis('off')

    if outcome == 1:
        fig.savefig(f'static/images/color_key_success/{player1}_{player2}.png', bbox_inches='tight', transparent=True,
                    format='png')
    else:
        fig.savefig(f'static/images/color_key_unsuccess/{player1}_{player2}.png', bbox_inches='tight', transparent=True,
                    format='png')
    plt.close(fig)
