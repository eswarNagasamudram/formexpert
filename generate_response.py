import base64
import vertexai
from vertexai.preview.generative_models import GenerativeModel, Part
from google.oauth2 import service_account
from pydantic import BaseModel
import streamlit as st
import os


class FormFeedback(BaseModel):

  def generate(self, video):
    model = GenerativeModel("gemini-pro-vision")
    response = model.generate_content(
      [video, """You are an AI fitness expert who will help users improve the effectiveness of their workout by pointing out the mistakes and suggesting improvements to their workout. \
              Above is a video of a user performing a workout. Reply in JSON format. Use the below format
              \"workout\" : <workout being performed>,
              \"form_rating\" : <Rating of the workout form from 1-10>,
              \"mistakes\" : <Array of mistakes being committed. If these mistakes are not committed, then the rating should be 10. Make the mistakes as concise as possible>,
              \"improvements\" <Array of improvements so that form can be better>
              \"next_steps\" : <Actionable next steps to be taken to improve the form>"""],
      generation_config={
          "max_output_tokens": 2048,
          "temperature": 0.4,
          "top_p": 1,
          "top_k": 32
      },
    )
    return response.candidates[0].content.parts[0].text

  def get_feedback(self, file_path:str):
    credentials = service_account.Credentials.from_service_account_info(st.secrets["gcs_connection"])
    vertexai.init(project = "kyc-gpt", credentials=credentials)
    video_path = file_path
    with open(video_path,"rb") as video_file :
      video_data = video_file.read()

    video = Part.from_data(data=video_data, mime_type="video/mp4")
    return self.generate(video)