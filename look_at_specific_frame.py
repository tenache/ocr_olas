import cv2


video_path = "L1_LoveAgain_ITR-A_16x9_ENG_TXTD_Stereo_PRORES_1080P24_PR.mp4"
cap = cv2.VideoCapture(video_path)
print(cap.get(cv2.CAP_PROP_FRAME_COUNT))

frame_num = 3200

total_seconds = (frame_num/cap.get(cv2.CAP_PROP_FPS))
minutes_for_frame = total_seconds//60
seconds_for_frame = (total_seconds % 60)
def frame_time(frame_num, fps):
    total_seconds = frame_num/fps
    minutes_for_frame = total_seconds//60
    seconds_for_frame = round(total_seconds % 60,2) 
    remaining_frames = round((seconds_for_frame - int(seconds_for_frame)) * fps)
    return minutes_for_frame, seconds_for_frame, remaining_frames

print(f"time for the frame number {frame_num} is {minutes_for_frame} minutes and {seconds_for_frame} seconds")
cap.set(cv2.CAP_PROP_FRAME_COUNT, frame_num)
ret, frame = cap.read()
cv2.imwrite(f"{video_path}_frame{frame_num}.jpg", frame)