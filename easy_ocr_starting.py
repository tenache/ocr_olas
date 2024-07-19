import cv2
# import pytesseract
from time import time
from water_mark import get_text_color
import numpy as np
from collections import Counter
import easyocr
from determine_watermark_bbox import return_bbox
from look_at_specific_frame import frame_time
from helper_functions import is_water_mark, resize_video_if_needed
import subprocess

# It's important to pre-process, but we can worry about that later... 

WATERMARK_MINIMUM = 0.6
path = "L1_LoveAgain_ITR-A_16x9_ENG_TXTD_Stereo_PRORES_1080P24_PR360.mp4"

new_path = resize_video_if_needed(path, 360, target_bitrate="1M")
cap = cv2.VideoCapture(new_path)

count = 0

success = 1
start = time()

skip_frames = 25

if not cap.isOpened():
    print("Error: could not open video")
    exit()

water_mark_colors = []
water_mark_most_common = []
main_water_mark_color = [135, 137, 140]
water_mark_bboxes_all = []
fps = cap.get(cv2.CAP_PROP_FPS)
water_mark_bboxes = []
while cap.isOpened():

    ret, frame = cap.read()

    if count == 0:
        water_mark_bboxes = return_bbox(frame)
    if count < 10:
        reader = easyocr.Reader(['en'])
        results= reader.readtext(frame)
        print(len(results))
        for result in results:
            bbox = result[0]
            # water_mark_bboxes.append(bbox)
            result_color, most_common_color = get_text_color(frame, bbox)
            water_mark_colors.append(result_color)
            water_mark_most_common.append(most_common_color)
        # water_mark_bboxes_all.append(water_mark_bboxes)
    # else:
    #     break
    if count == 10: 
        # print(water_mark_bboxes_all)
        # break
        water_mark_color = np.mean(water_mark_colors, axis= 0)
        most_common_color = np.mean(water_mark_most_common, axis=0)
        main_water_mark_color = np.mean([water_mark_color, most_common_color], axis=0)
        print(f"most common water_mark_color is {most_common_color}")
        print(f"main_water_mark_color is {water_mark_color}")
        
        # This is super over-kill and maybe even wrong ... 
        print(f"main water_mark_color is {main_water_mark_color}")
    
    if not ret:
        break
    if count % skip_frames == 0 and count > 9: 
        reader = easyocr.Reader(['en'])
        result = reader.readtext(frame)
        all_text = ""
        for (bbox, text, prob) in result:
                is_text = False
                is_watermark_index = is_water_mark(frame, bbox, water_mark_bboxes, main_water_mark_color, most_common_color, text, buffer_pixels=100, buffer_color = 130)
                print(f"is_watermark_index is {is_watermark_index}")
                if is_watermark_index > WATERMARK_MINIMUM:
                    continue
                elif text != "" and text != " ":
                    print(f"Text: {text}, Probability: {prob}")
                    all_text += text + "\n"
                    is_text = True
        if is_text: 
            print(f"in frame number {count}")
            minutes, seconds, remaining_frames = frame_time(count, fps)
            print(f"This was read at {minutes} minutes, {seconds} seconds, and {remaining_frames} frames")
            with open("titles.txt", "a") as file:
                file.write(f"time: {minutes} minutes, {seconds} seconds and {remaining_frames} frames:\n")
                file.write(f"frame number: {count}" + "\n")
                file.write(f"text:" + "\n")
                file.write(all_text + "\n\n")
                file.write("---------------------------------------------\n")
            cv2.imwrite(f"title_{minutes}_{seconds}.jpg", frame)

        # if cv2.waitKey(1) & 0xFF == ord('q'):
        #     break
    count += 1

cap.release()
# cv2.destroyAllWindows()
total_time = round((time()- start), 2)
print(f"process took {total_time//60} minutes and {round(total_time%60, 2)} seconds to complete")
