import os
import base64
import base64
from io import BytesIO
import json
from PIL import Image

import openai
import google.cloud.texttospeech as tts


from dotenv import load_dotenv, find_dotenv

_ = load_dotenv(find_dotenv())  # read local .env file


def get_completion_text(prompt, model="gpt-3.5-turbo-instruct"):
    openai.api_key = os.environ["OPENAI_API_KEY"]
    
    # messages = [
    #     {
    #         "role": "system",
    #         "content": "You are a friendly assistant. Your answers are JSON only.",
    #     },
    #     {
    #         "role": "assistant",
    #         "content": '{"message": "Understood. I will output my answers in JSON format." }',
    #     },
    #     {"role": "user", "content": prompt},
    # ]

    # response = openai.ChatCompletion.create(
    #     model=model, messages=messages, temperature=0, max_tokens=2048, stream=False
    # )
    response = openai.Completion.create(
        model=model, prompt=prompt, temperature=0.7, max_tokens=3500, stream=False
    )

    # return response.choices[0].message["content"]
    return response.choices[0].text


# get_completion_text("câu chuyện nàng tiên cá")


def get_completion_image(prompt, model=None):
    response = openai.Image.create(
        prompt=prompt, n=1, size="1024x1024", response_format="b64_json"
    )
    im = Image.open(BytesIO(base64.b64decode(response["data"][0]["b64_json"])))

    return im


# get_completion_image("a dog")


def get_completion_tts(
    text: str, voice_name: str = "vi-VN-Neural2-A"
):  # en-AU-Neural2-A vi-VN-Neural2-A
    language_code = "-".join(voice_name.split("-")[:2])
    text_input = tts.SynthesisInput(text=text)
    voice_params = tts.VoiceSelectionParams(
        language_code=language_code, name=voice_name
    )
    audio_config = tts.AudioConfig(audio_encoding=tts.AudioEncoding.LINEAR16)

    client = tts.TextToSpeechClient()
    response = client.synthesize_speech(
        input=text_input,
        voice=voice_params,
        audio_config=audio_config,
    )

    return response.audio_content


def read_audio(path):
    with open(path, "rb") as f:
        audio = f.read()
    return audio


# audio_data = get_completion_tts("đi chết đi con mickey")
# Audio(audio_data)


# def generate(prompt):
#     full_prompt = f"""
#         "story": write a story less than 150 words about '''{prompt}''', use Vietnamese to write it,
#         "prompt": prompt for DALL.E to generate visual of the story in cartoon style, use English to write it.
#         """
#     content = get_completion_text(full_prompt)
#     json_content = json.loads(content)
#     story = json_content["story"]
#     visual_prompt = json_content["prompt"]

#     visual = get_completion_image(visual_prompt)
#     voice = get_completion_tts(story)

#     return visual, voice
