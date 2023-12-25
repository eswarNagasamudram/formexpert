from typing import Any, Coroutine, List
import streamlit as st
import cv2
import time
from generate_response import FormFeedback
import json
from streamlit_webrtc import  webrtc_streamer, VideoProcessorBase
import os

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
        
        
        for frame in frames:
            self.frames.append(frame.to_ndarray(format = "bgr24"))

        return super().recv_queued(frames)
         


def save_video(frames):
    os.write(1, b"Saved video frames \n")
    if not frames:
        return

    fourcc = cv2.VideoWriter_fourcc(*"H264")
    height, width, channel = frames[0].shape 
    out = cv2.VideoWriter("recorded_video.mp4", fourcc, 20.0, (width, height))
    for frame in frames:
        out.write(frame)
    out.release()
    on_stop_callback()


def on_stop_callback():
    os.write(1, b"Starting to rerun \n")
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
        live_video_placeholder.empty()
        live_video_placeholder = webrtc_streamer(key="example", video_processor_factory=VideoProcessor)
        if live_video_placeholder.video_processor :
            live_video_placeholder.video_processor.recording = True
            # os.write(1, b"Entering here  \n")
            # while live_video_placeholder.video_processor :
            #     if live_video_placeholder.video_processor.recording == True :
            #         os.write(1,b"Sleeping zzzzzz \n")
            #         time.sleep(1)
            #         continue
            #     else :
            #         frames = live_video_placeholder.video_processor.frames
            #         save_video(frames)
            #         break

    else:
        recording_button = st.button("Start new recording", on_click=toggleRecordingStatus)
        with open('recorded_video.mp4', 'rb') as video:
            live_video_placeholder = st.video(video, format="video/mp4", start_time=0)
        with st.spinner("Getting feedback for your workout..."):
            st.write("Generating feedback")
            # generator = FormFeedback()
            # json_data = generator.get_feedback("recorded_video.mp4")
            # print("JSON DATA IS ----------\n")
            # print(json_data)
            # print("===========================")

            # cleaned_text = json_data.replace("```json\n", "").replace("```","").replace("```json\n{","").replace("JSON","").replace("\n","").strip()
            # print("Cleaned text IS ----------")
            # print(cleaned_text)
            # print("===========================")
            # try:
            #     json_data = json.loads(cleaned_text)
            #     print(json_data)
            # except json.JSONDecodeError as e:
            #     print(f"Error decoding JSON: {e}")
            # st.title(f"# {json_data['workout']} Workout")
            # st.subheader(f"Form Rating: {json_data['form_rating']}")

            # st.header("Mistakes:")
            # for mistake in json_data['mistakes']:
            #     st.write(f"- {mistake}")

            # st.header("Improvements:")
            # for improvement in json_data['improvements']:
            #     st.write(f"- {improvement}")

            # st.header("Next Steps:")
            # for next_step in json_data['next_steps']:
            #     st.write(f"- {next_step}")


def toggleRecordingStatus():
    if st.session_state.recording_status == 0 :
        st.session_state.recording_status = 1
    elif st.session_state.recording_status == 1:
        st.session_state.recording_status = 2
    else:
        st.session_state.recording_status = 0
    
    

        # if "recording_status" not in st.session_state or st.session_state.recording_status == 0:
        #     st.session_state.recording_status = 1

        # recording_button.empty()
        # stop_recording = st.button("Stop Recording")
        # # Countdown timer
        # live_video_placeholder = st.empty()

        # for i in range(3, 0, -1):
        #     live_video_placeholder.markdown(f"<h1 style='text-align: center;'>{i}</h1>", unsafe_allow_html=True)
        #     time.sleep(1)


        # live_video_placeholder.empty()
        # live_video = webrtc_streamer(key="example", video_processor_factory=VideoProcessor)
        # if live_video.video_transformer :
            # print("entering this block")
            # if st.session_state.recording_status == 0 or stop_recording:
            #     print("Processing this block")
            #     live_video_placeholder.empty()  # Clear the live video section
            #     live_video_placeholder.video('recorded_video.mp4')

            #     with st.spinner("Getting feedback for your workout..."):
            #         generator = FormFeedback()
            #         json_data = generator.get_feedback("recorded_video.mp4")
            #         print("JSON DATA IS ----------\n")
            #         print(json_data)
            #         print("===========================")

            #         cleaned_text = json_data.replace("```json\n", "").replace("```","").replace("```json\n{","").replace("JSON","").replace("\n","").strip()
            #         print("Cleaned text IS ----------")
            #         print(cleaned_text)
            #         print("===========================")
            #         try:
            #             json_data = json.loads(cleaned_text)
            #             print(json_data)
            #         except json.JSONDecodeError as e:
            #             print(f"Error decoding JSON: {e}")
            #         st.title(f"# {json_data['workout']} Workout")
            #         st.subheader(f"Form Rating: {json_data['form_rating']}")

            #         st.header("Mistakes:")
            #         for mistake in json_data['mistakes']:
            #             st.write(f"- {mistake}")

            #         st.header("Improvements:")
            #         for improvement in json_data['improvements']:
            #             st.write(f"- {improvement}")

            #         st.header("Next Steps:")
            #         for next_step in json_data['next_steps']:
            #             st.write(f"- {next_step}")
                
            #         recording_button.empty()
            #         start_recording = st.button("Start Recording")

if __name__ == "__main__":
    main()
