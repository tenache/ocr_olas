from water_mark import get_text_color
import subprocess
import re
import os

def is_water_mark(frame, 
                  bbox, 
                  water_mark_bboxes,
                  main_water_mark_color,
                  most_common_color,
                  text,
                  buffer_pixels = 100,
                  buffer_color = 130,
                  ):
    """
    function to determine with some degree of probability if an identified text is actually part of a watermark
    """

    color, most_commmon = get_text_color(frame, bbox)


    # The idea in this next section is to determine buffer_color by trial and error. 
    # We want a number that is big enough to allow for the expected differences in output, but low enough to allow
    # for other stuff that might be there. 
    # We then say, how close were we to this buffer color? 80%? thats what common_diff/buffer_color does.
    #  
    main_color_diff = abs(sum(color - main_water_mark_color))
    if main_color_diff < buffer_color:
        color_within_range = main_color_diff/buffer_color
    else:
        color_within_range = False
    common_diff = abs(sum(most_commmon - most_common_color))
    if common_diff < buffer_color:
        common_within_range = common_diff/buffer_color
    else:
        common_within_range = False
    
    leftmost = bbox[0][0]
    rightmost = bbox[1][0]
    uppermost = bbox[0][1]
    bottommost = bbox[1][1]
    box_within_range = False

    # determine if the we are analyzing is inside the buffer zone
    # for watermark_bbox in water_mark_bboxes:
    #     if leftmost >= watermark_bbox[0][0] + buffer_pixels and rightmost <= watermark_bbox[1][0] - buffer_pixels:
    #         if uppermost <= watermark_bbox[0][1] - buffer_pixels and bottommost >= watermark_bbox[1][1] + buffer_pixels:
    #             box_within_range = True
    #     if not box_within_range:
    #         break

    # The same thing here: we are establishing some lee-way between the bounding box determined to be the water-mark, and the 
    # one that has been detected. If under a certain limit, we are trying to determine how close we got to that limit 
    # with box_within_range

    for watermark_bbox in water_mark_bboxes:
        left_dist = abs(leftmost - watermark_bbox[0][0])
        right_dist = abs(rightmost - watermark_bbox[1][0])
        upper_dist = abs(uppermost - watermark_bbox[0][1])
        bottom_dist = abs(bottommost - watermark_bbox[1][1])
        # todo: problem here is that i am comparing the actual bounding box to the one that i drew. 
        # So I need to identify the actual approximate bounding boxes that easyocr obtains
        if left_dist < buffer_pixels and right_dist < buffer_pixels and upper_dist < buffer_pixels and bottom_dist < buffer_pixels:
            box_within_range = (left_dist + right_dist + upper_dist + bottom_dist)/buffer_pixels*4
        if not box_within_range:
            break
    if color_within_range and common_within_range and box_within_range:
        watermark_index = (color_within_range + common_within_range + box_within_range)/3
    else:
        watermark_index = False

    return watermark_index

def get_video_resolution(video_path):
    command = [
        'ffmpeg',
        '-i', video_path
    ]
    result = subprocess.run(command, stderr=subprocess.PIPE, text=True)
    pattern = re.compile(r'Stream.*Video.* (\d+)x(\d+)')
    for line in result.stderr.split('\n'):
        match = pattern.search(line)
        if match:
            width, height = match.groups()
            return int(width), int(height)
    return None, None

def resize_video_if_needed(video_path, max_resolution = 720, target_bitrate='1M'):
    video_path_base = os.path.splitext(video_path)[0]
    output_path = video_path_base + str(max_resolution) + ".mp4"
    width, height = get_video_resolution(video_path)
    if width is None or height is None:
        print("Unable to determine video resolution.")
        return

    print(f"Original resolution: {width}x{height}")
    if width > 1280 or height > max_resolution:
        print(f"Resolution is higher than {max_resolution}p. Resizing...")
        if width > height:
            scale = 'scale=1280:-1'
        else:
            scale = f'scale=-1:{max_resolution}'
        command = [
            'ffmpeg',
            '-i', video_path,
            '-vf', scale,
            '-b:v', target_bitrate,
            '-bufsize', target_bitrate,
            output_path
        ]
        subprocess.run(command)
        print(f"Video resized to {max_resolution}p and saved as {output_path} with a bitrate of {target_bitrate}.")
        return output_path
    else:
        print(f"Resolution is {max_resolution}p or lower. No resizing needed.")
        return video_path
