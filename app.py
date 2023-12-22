import streamlit as st
import cv2
import numpy as np
import time
from io import BytesIO
import base64
import vertexai
from vertexai.preview.generative_models import GenerativeModel, Part
from google.oauth2 import service_account
from generate_response import FormFeedback
import json

def main():
    st.title("FORM EXPERT AI")

    # Button to start/stop recording
    recording_button = st.empty()
    start_recording = recording_button.button("Start recording")

    # Video capture object
    cap = cv2.VideoCapture(0)

    if start_recording:
        recording_button.empty()
        stop_recording = recording_button.button("Stop Recording")
        # Set the video codec
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")

        # Get the frame dimensions
        width = int(cap.get(3))
        height = int(cap.get(4))

        # Create a VideoWriter object
        out = cv2.VideoWriter("recorded_video.mp4", fourcc, 20.0, (width, height))

        # Countdown timer
        live_video_placeholder = st.empty()

        for i in range(3, 0, -1):
            live_video_placeholder.markdown(f"<h1 style='text-align: center;'>{i}</h1>", unsafe_allow_html=True)
            time.sleep(1)

        live_video_placeholder.empty()  # Clear the countdown after it finishes


        start_time = time.time()
        while True:
            ret, frame = cap.read()

            # Convert BGR to RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Write the frame to the video file
            out.write(frame)

            # Display the frame
            live_video_placeholder.image(rgb_frame, channels="RGB")

            # Stop recording after 10 seconds
            if (time.time() > start_time + 5):
                cap.release()
                out.release()
                live_video_placeholder.empty()  # Clear the live video section
                live_video_placeholder.video('recorded_video.mp4')

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
                
                    recording_button.empty()
                    start_recording = recording_button.button("Start Recording")
                    break

    # Release the video capture object
    cap.release()

if __name__ == "__main__":
    main()
