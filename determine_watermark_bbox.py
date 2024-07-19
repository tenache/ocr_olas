import cv2

# Global variables
ix, iy = -1, -1
drawing = False
bounding_boxes = []
image = None
img_copy = None

# Function to draw bounding box
def draw_bounding_box(event, x, y, flags, param):
    global ix, iy, drawing, img_copy, image

    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        ix, iy = x, y

    elif event == cv2.EVENT_MOUSEMOVE:
        if drawing:
            img_copy = image.copy()
            cv2.rectangle(img_copy, (ix, iy), (x, y), (0, 255, 0), 2)
            cv2.imshow('image', img_copy)

    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        cv2.rectangle(image, (ix, iy), (x, y), (0, 255, 0), 2)
        cv2.imshow('image', image)
        bounding_boxes.append(((ix, iy), (x, y)))

# Function to return bounding boxes
def return_bbox(image_name):
    global image, img_copy, bounding_boxes

    if isinstance(image, str):
        image = cv2.imread(image_name)
        if image is None:
            print(f"error loading image: {image}")
            return []
    else:
        image = image_name

    bounding_boxes = []

    # Clone the image for drawing
    img_copy = image.copy()

    # Create a window and bind the function to the window
    cv2.namedWindow('image')
    cv2.setMouseCallback('image', draw_bounding_box)

    # Display the image and wait for a keypress
    cv2.imshow('image', image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    return bounding_boxes

if __name__ == "__main__":
    bboxes = return_bbox('first_frame_from_video.jpg')
    print(f"Watermark bboxes are {bboxes}")
