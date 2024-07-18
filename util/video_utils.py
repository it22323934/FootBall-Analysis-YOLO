import cv2

# Read the video from the video and return the list of frames of the video
def read_video(video_path):
    cap=cv2.VideoCapture(video_path)
    frames=[]
    while True:
        ret,frame=cap.read()
        if not ret:
            break
        frames.append(frame)
    return frames

# Save the video from the list of frames
def save_video(output_video_frames, output_video_path):
    fource=cv2.VideoWriter_fourcc(*'XVID')
    out=cv2.VideoWriter(output_video_path,fource,24,(output_video_frames[0].shape[1],output_video_frames[0].shape[0]))
    for frame in output_video_frames:
        out.write(frame)
    out.release()