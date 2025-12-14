import cv2
import matplotlib.pyplot as plt

# Load and process the image (as before)
image = cv2.imread('image.jpg')
gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
inverted_image = 255 - gray_image
blurred = cv2.GaussianBlur(inverted_image, (21, 21), 0)
inverted_blurred = 255 - blurred
pencil_sketch = cv2.divide(gray_image, inverted_blurred, scale=256.0)

# Display with matplotlib
plt.imshow(pencil_sketch, cmap='gray')
plt.title("Pencil Sketch")
plt.axis('off')
plt.show()

# pip install matplotlib
