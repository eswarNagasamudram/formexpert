import streamlit as st
from streamlit_webrtc import  webrtc_streamer, VideoProcessorBase
import cv2
import numpy as np
import io
import time
import base64

class VideoTransformer(VideoProcessorBase):
    def __init__(self):
        self.duration = 10
        self.start_time = time.time()
        self.recording = False
        self.frames = []

    def recv(self, frame):
        print("Calling transform--------")
        if not self.recording:
            return frame

        if time.time() - self.start_time > self.duration:
            self.recording = False
            self.save_video()
            st.write("Recording complete!")
            return frame

        self.frames.append(frame)
        return frame

    def save_video(self):
        print("Saving video ------------ ")
        if not self.frames:
            return

        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        height, width, _ = self.frames[0].shape
        out = cv2.VideoWriter("recorded_video.mp4", fourcc, 20.0, (width, height))

        for frame in self.frames:
            out.write(frame)

        out.release()

def main():
    st.title("Form expert")

    duration = 10
    webrtc_ctx = webrtc_streamer(key="example", video_processor_factory=VideoTransformer)

    if webrtc_ctx.video_transformer:
        print("Video transformer has been initialised")
        webrtc_ctx.video_transformer.duration = duration
        webrtc_ctx.video_transformer.start_time = time.time()
        webrtc_ctx.video_transformer.recording = True
        st.write(f"Recording started. Duration: {duration} seconds.")

        if not webrtc_ctx.video_transformer.recording and webrtc_ctx.video_transformer.frames:
            # Provide an option to download the recorded video
            st.markdown(
                f"Download recorded video: [recorded_video.mp4](data:video/mp4;base64,{get_video_bytes()})"
            )

def get_video_bytes():
    with open("recorded_video.mp4", "rb") as file:
        video_bytes = base64.b64encode(file.read()).decode("utf-8")
    return video_bytes

if __name__ == "__main__":
    main()