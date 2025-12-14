import cv2

# Load the image
# image = cv2.imread('image.jpg')
image = cv2.imread('mariya.png')

# Convert to grayscale
gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# Invert the grayscale image
inverted_image = 255 - gray_image

# Apply Gaussian blur
blurred = cv2.GaussianBlur(inverted_image, (25, 25), sigmaX=0, sigmaY=0)

# Invert the blurred image
inverted_blurred = 255 - blurred

# Create the pencil sketch
pencil_sketch = cv2.divide(gray_image, inverted_blurred, scale=256.0)

# Save the result
cv2.imwrite('pencil_sketch.jpg', pencil_sketch)

# (Optional) Display the image
cv2.imshow("Pencil Sketch", pencil_sketch)
cv2.waitKey(0)
cv2.destroyAllWindows()

# pip install opencv-python

