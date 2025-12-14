from rembg import remove
from PIL import Image
import io

def remove_background(input_image_path, output_image_path):
    # Open the image
    with open(input_image_path, 'rb') as input_file:
        input_data = input_file.read()

    # Remove background
    output_data = remove(input_data)

    # Save the output image
    output_image = Image.open(io.BytesIO(output_data))
    output_image.save(output_image_path)

# Example usage
remove_background('image.jpg', 'output.png')


# install 

'''
pip install rembg pillow
pip install onnxruntime
'''