from typing import Any, Coroutine, List
import streamlit as st
import cv2
import time
from generate_response import FormFeedback
import json
from streamlit_webrtc import  webrtc_streamer, VideoProcessorBase
import os
from twilio.rest import Client
import imageio

class VideoProcessor(VideoProcessorBase):
    def __init__(self):
        self.duration = 10
        self.start_time = time.time()
        self.recording = False
        self.frames = []
    
    def recv(self, frame):
        return frame
    
    def recv_queued(self, frames: List) -> Coroutine[Any, Any, List]:
        if not self.recording:
            return super().recv_queued(frames)
        if time.time() - self.start_time > self.duration :
            self.recording = False
        
        for frame in frames:
            self.frames.append(frame.to_ndarray(format = "bgr24"))

        return super().recv_queued(frames)
         


def save_video(frames):
    os.write(1, b"Saved video frames \n")
    if not frames:
        return

    # fourcc = cv2.VideoWriter_fourcc(*"avc1")
    # height, width, channel = frames[0].shape 
    # out = cv2.VideoWriter("recorded_video.mov", fourcc, 20.0, (width, height))
    # for frame in frames:
    #     out.write(frame)
    # out.release()
    output_file = "recorded_video.mp4"
        
    # Create a video writer using imageio
    writer = imageio.get_writer(output_file, fps=20)
    
    for frame in frames:
        # Convert BGR to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # Append the RGB frame to the video
        writer.append_data(rgb_frame)

    writer.close()
    on_stop_callback()


def on_stop_callback():
    os.write(1,b"calling rerun \n")
    st.session_state.recording_status = 2
    st.rerun()

def main():
    st.title("FORM EXPERT AI")

    # Button to start/stop recording
    recording_button = st.empty()
    live_video_placeholder = st.empty()
    if "recording_status" not in st.session_state :
        st.session_state.recording_status = 0
        st.session_state.workout_count = 0
    
    
    if st.session_state.recording_status == 0 :
        recording_button = st.button("Start Recording", on_click=toggleRecordingStatus)
        live_video_placeholder = st.empty()
        
    elif st.session_state.recording_status == 1 :
        print("Recording button is modified to --STOP RECORDING----")
        print(f"SESSIONSTATE - {st.session_state.recording_status}")
        recording_button = st.button("Stop Recording", on_click=toggleRecordingStatus)
        
        account_sid = 'AC12fd17343f1554d20e202e30f2f25d33'
        auth_token = '40d4406146f8598cf0b08e0e8a508460'
        client = Client(account_sid, auth_token)

        token = client.tokens.create()
        
        live_video_placeholder.empty()
        live_video_placeholder = webrtc_streamer(key="example", video_processor_factory=VideoProcessor,rtc_configuration={"iceServers": token.ice_servers}, desired_playing_state= True)
        frames = []
        if live_video_placeholder.video_processor :
            live_video_placeholder.video_processor.recording = True
            while live_video_placeholder.video_processor :
                os.write(1,b"Entering the loop \n")
                if live_video_placeholder.video_processor.recording == True :
                    os.write(1,b"Sleeping zzz \n")
                    time.sleep(1)
                    continue
                else :
                    os.write(1,b"Checking else condition \n")
                    frames = live_video_placeholder.video_processor.frames
                    break
        save_video(frames)

    else:
        recording_button = st.button("Start new recording", on_click=toggleRecordingStatus)
        with open('recorded_video.mp4', 'rb') as video:
            live_video_placeholder = st.video(video, format="video/mp4", start_time=0)
        with st.spinner("Getting feedback for your workout..."):
            generator = FormFeedback()
            json_data = generator.get_feedback("recorded_video.mp4")
            print("JSON DATA IS ----------\n")
            print(json_data)
            print("===========================")

            cleaned_text = json_data.replace("```json\n", "").replace("```","").replace("```json\n{","").replace("JSON","").replace("\n","").strip()
            print("Cleaned text IS ----------")
            print(cleaned_text)
            print("===========================")
            try:
                json_data = json.loads(cleaned_text)
                print(json_data)
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON: {e}")
            st.title(f"# {json_data['workout']} Workout")
            st.subheader(f"Form Rating: {json_data['form_rating']}")

            st.header("Mistakes:")
            for mistake in json_data['mistakes']:
                st.write(f"- {mistake}")

            st.header("Improvements:")
            for improvement in json_data['improvements']:
                st.write(f"- {improvement}")

            st.header("Next Steps:")
            for next_step in json_data['next_steps']:
                st.write(f"- {next_step}")


def toggleRecordingStatus():
    if st.session_state.recording_status == 0 :
        st.session_state.recording_status = 1
    elif st.session_state.recording_status == 1:
        st.session_state.recording_status = 2
    else:
        st.session_state.recording_status = 0
    
    

       

if __name__ == "__main__":
    main()
