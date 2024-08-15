import os
import glob
from PIL import Image, ImageDraw, ImageFont

def add_spaces_between_chinese_characters(text):
    new_text = []
    for i, char in enumerate(text):
        new_text.append(char)
        if i + 1 < len(text) and is_chinese(char) and is_chinese(text[i + 1]):
            new_text.append(" ")
    return ''.join(new_text)

def is_chinese(char):
    return '\u4e00' <= char <= '\u9fff'


def render_text_to_led_matrix(text, font_path, font_size=50, output_size=(314, 186), text_color=(0, 0, 0)):
    text = add_spaces_between_chinese_characters(text)
    
    initial_width = font_size * len(text)
    image = Image.new('RGB', (initial_width, output_size[1]), 'white')
    draw = ImageDraw.Draw(image)

    font = ImageFont.truetype(font_path, font_size)

    # Using textbbox to get text bounding box
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    print(text_bbox)
    text_height = text_bbox[3] - text_bbox[1]
    
    position = (2, (output_size[1] - text_height) // 2)
    print(position)
    draw.text(position, text, fill=text_color, font=font)

    # Calculate the number of fragments required
    num_fragments = (text_width + output_size[0] - 1) // output_size[0]

    print("num fragment is ", num_fragments)
    
    fragments = []
    for i in range(num_fragments):
        fragment = image.crop((i * output_size[0], 0, min((i + 1) * output_size[0], text_width), output_size[1]))
        
        # If there is only one fragment, ensure it fits the output size
        if num_fragments == 1:
            fragment_image = Image.new('RGB', output_size, 'white')
            fragment_image.paste(fragment, (0, 0))
            print((output_size[1] - text_height) // 2)
            fragments.append(fragment_image)
        else:
            fragments.append(fragment)
    
    return fragments



def save(fragments, base_path):
    """
    Saves each fragment to the specified path after clearing the directory.

    Parameters:
        fragments (list of Image): The list of image fragments to save.
        base_path (str): The base file path where the fragments will be saved.
    """
    # Ensure the directory exists
    directory = os.path.dirname(base_path)
    if not os.path.exists(directory):
        os.makedirs(directory)
    else:
        # Clear any existing files in the directory
        files = glob.glob(os.path.join(directory, '*'))
        for f in files:
            os.remove(f)
    
    # Save each fragment
    for idx, fragment in enumerate(fragments):
        fragment.save(f"{base_path}_fragment_{idx + 1}.png")

# Example usage
if __name__ == "__main__":
    
    font_path = "/Users/zhaoze/Desktop/2024/upsoft/xingkai.ttf"
    text = "Luka"
    text_color = (0, 0, 0)  # Change this to the desired color, e.g., (255, 0, 0) for red
    base_save_path = "./char/"  # Ensure the directory exists or will be created

    fragments = render_text_to_led_matrix(text, font_path, font_size=50, text_color=text_color)
    save(fragments, base_save_path, True)

    # Optionally, display the fragments
    for fragment in fragments:
        fragment.show()
