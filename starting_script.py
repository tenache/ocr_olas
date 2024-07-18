import cv2
import pytesseract
from datetime import datetime

# It's important to pre-process, but we can worry about that later... 


path = "L1_LoveAgain_ITR-A_16x9_ENG_TXTD_Stereo_PRORES_1080P24_PR.mp4"

vidObj = cv2.VideoCapture(path)

count = 0

success = 1
start = datetime.now().time()

while success: 
    # videoObj calls read
    # function extract frames
    success, image = vidObj.read()
    custom_config = r'--oem 3 --psm 6'
    text = pytesseract.image_to_string(image, config = custom_config)
    print(text)
    
    count += 1

print(f"The process took {datetime.now().time() - start}")

