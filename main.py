from langchain.llms.vertexai import VertexAI
from langchain.chat_models import ChatVertexAI
from langchain.schema.messages import HumanMessage
from langchain.prompts import PromptTemplate
from AppConfig import AppConfig
import os
from io import BytesIO
import base64
from moviepy.editor import VideoFileClip
from PIL import Image
import numpy as np

def set_vertex_ai_key(app_config : AppConfig):
    check_and_set_env_variable("GOOGLE_APPLICATION_CREDENTIALS", app_config.GOOGLE_APPLICATION_CREDENTIALS)


def check_and_set_env_variable(variable_name, default_value):
    # Check if the environment variable is already set
    existing_value = os.environ.get(variable_name)

    if existing_value is not None:
        print(f"The environment variable '{variable_name}' is already set to '{existing_value}'.")
    else:
        # Set the environment variable with a default value
        os.environ[variable_name] = default_value
        print(f"The environment variable '{variable_name}' has been set to '{default_value}'.")


def load_config():
    app_config = AppConfig()
    return app_config

def create_text_message(text:str):
    text_message = {"type": "text","text" : text }
    return text_message

def create_image_message_from_image(image_path:str):
    with open(image_path, "rb") as image_file:
        image_bytes = image_file.read()
    image_message = {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{base64.b64encode(image_bytes).decode('utf-8')}"},
                    }
    return image_message

def create_image_message_from_image_bytes(image_bytes):
    image_message = {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{base64.b64encode(image_bytes).decode('utf-8')}"},
                    }
    return image_message

def convert_video_to_images(video_path, frame_interval=1):
    # Load the video clip
    clip = VideoFileClip(video_path)
    
    # Get video properties
    frame_count = int(clip.fps * clip.duration)

    print(f"Converting {video_path} to images...")
    print(f"Total frames: {frame_count}, FPS: {clip.fps}")

    images = []
    # Save frames at specified intervals
    for current_frame in range(0, frame_count, frame_interval):
        frame = clip.get_frame(current_frame / clip.fps)
        frame = (frame*255).astype(np.uint8)
        image = Image.fromarray(frame)
        with BytesIO() as buffer:
            image.save(buffer, format="JPEG")
            image_bytes = buffer.getvalue()
            images += [image_bytes]
    return images
def main():
    config = load_config()
    set_vertex_ai_key(config)

    llm = ChatVertexAI(model_name="gemini-pro-vision", max_output_tokens=2048)
    video_file_path = "bench_dip_correct.mp4"
    # images = convert_video_to_images(video_file_path)
    # image_messages = list(map(lambda img_bytes: create_image_message_from_image_bytes(img_bytes),images))
    

    text_message = create_text_message(f'You are an AI fitness expert who will help users improve the effectiveness of their workout by pointing out the mistakes and suggesting improvements to their workout. Above is a video of a user performing bench dips. Reply in JSON format. Use the below format \
                                        "form_rating" : <Rating of the workout form from 1-10> \
                                        "mistakes" : <Array of mistakes being committed. If these mistakes are not committed, then the rating should be 10. Make the mistakes as concise as possible> \
                                        "improvements" : <Array of improvements so that form can be better>')
    
    with open(video_file_path, "rb") as video_file:
        video_data = video_file.read()
    video_message = {"type" : "image_url", 
                     "image_url" :{"url": f"data:video/mp4;base64,{base64.b64encode(video_data).decode('utf-8')}"} }
    message = HumanMessage(content=([text_message, video_message]))
    response = llm([message])
    print(response)

if __name__ == "__main__":
    main()