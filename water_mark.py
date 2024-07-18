import cv2
from datetime import datetime
from collections import Counter
import easyocr
import numpy as np

# It's important to pre-process, but we can worry about that later... 


path = "L1_LoveAgain_ITR-A_16x9_ENG_TXTD_Stereo_PRORES_1080P24_PR.mp4"

cap = cv2.VideoCapture(path)

count = 0

success = 1
start = datetime.now().time()

skip_frames = 10

if not cap.isOpened():
    print("Error while reading video")

ret, frame = cap.read()

reader = easyocr.Reader(['en'])
result = reader.readtext(frame)
# bbox = result[0][0]
bbox = result[0][0]

def get_text_color(frame, bbox):
    # extract the region of itnerest 
    top_left = tuple(map(int, bbox[0]))
    bottom_right = tuple(map(int, bbox[2]))
    roi = frame[top_left[1]:bottom_right[1], top_left[0]:bottom_right[0]]
    
    # Convert the roi to grayscale

    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    cv2.imwrite("gray_watermark.jpg", gray)
    
    _, binary = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    cv2.imwrite("gray_watermark_OTSU.jpg", binary)
    
    # find the contours of the text regions
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Create a mas for the text regions
    mask = np.zeros_like(binary)
    cv2.drawContours(mask, contours, -1, (255), thickness=cv2.FILLED)
    
    # Extract the colors from the original ROI using the mask
    colors = cv2.bitwise_and(roi, roi, mask=mask)
    colors = cv2.cvtColor(colors, cv2.COLOR_BGR2RGB).reshape(-1,3)
    colors = [tuple(p) for p in colors if any(p)]
    if not colors:
        return (0, 0, 0)
    
    # Find the most common color
    most_common_color = Counter(colors).most_common(1)[0][0]
    most_common_color = tuple(map(int, most_common_color))
    mean_color = np.mean(colors, axis=0)
    mean_color = tuple(map(int, mean_color))
    # print(f"most common color is {most_common_color}")
    # print(f"average color is {mean_color}")
    # This part is probably overkill, but oh well ... 
    return_color = tuple(map(int,(np.mean([most_common_color, mean_color], axis=0))))
    # print(f"return_color is {return_color}")
    return return_color, most_common_color
    
    # APPLY A BINARY THRESHOLD TO CREATE A MASK FOR THE TEXT

get_text_color(frame, bbox)
cv2.imwrite(f"first_frame_from video.jpg", frame)