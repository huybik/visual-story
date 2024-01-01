import gradio as gr
from utils import *
import os
from PIL import Image


class MyGenerator(object):
    def __init__(self):
        """Initialize model state"""
        self.index = 0  # story index

    def read_prompt(self, prompt):
        folder = None
        if prompt == "Cậu bé quàng khăn đỏ":
            folder = "caube/"
        elif prompt == "Hoàng hậu ngủ trong rừng":
            folder = "hoanghau/"
        elif prompt == "Bạch tuyết và ba chú lùn":
            folder = "bachtuyet/"

        # Load sample folders
        if folder:
            # with open('content.json', 'r', encoding='utf-8') as f:
            #    json_content = json.load(f)
            self.visual = [
                Image.open(folder + "image0.jpeg"),
                Image.open(folder + "image1.jpeg"),
                Image.open(folder + "image2.jpeg"),
            ]
            # self.voice = [read_audio('voice1.mp3'), read_audio('voice2.mp3'), read_audio('voice3.mp3')]
            self.voice = [
                folder + "voice0.mp3",
                folder + "voice1.mp3",
                folder + "voice2.mp3",
            ]

        # Generate the story if we have api key
        elif os.environ["OPENAI_API_KEY"]:
            full_prompt = f"""
            Only return in JSON format, do the task below:
            Write a children story around 500 words about '''{prompt}''' in Vietnamese that breaks down to 3 parts,
            "intro": the intro of the story,
            "middle": the middle of the story,
            "ending": the ending of the story,
            then write detail prompt for image generator DALL.E to generate cartoon visualize for the story in English,
            "intro_prompt": prompt for intro
            "middle_prompt": prompt for middle
            "ending_prompt": prompt for ending
        """
            self.content = get_completion_text(full_prompt)
            json_content = json.loads(self.content)

            self.stories = [
                json_content["intro"],
                json_content["middle"],
                json_content["ending"],
            ]
            self.visual_prompts = [
                json_content["intro_prompt"],
                json_content["middle_prompt"],
                json_content["ending_prompt"],
            ]

            self.visual = []
            self.voice = []
            i = 0
            for story, visual_prompt in zip(self.stories, self.visual_prompts):
                # get image
                img = get_completion_image(visual_prompt)
                img.save("temp/image" + str(i) + ".jpeg")
                self.visual.append(img)

                # get voice over
                single_voice = get_completion_tts(story)
                filename = "temp/voice" + str(i) + ".mp3"
                with open(filename, "wb") as out:
                    out.write(single_voice)
                self.voice.append(filename)
                i += 1

                # self.voice.append(get_completion_tts(story))
                # self.visual.append(get_completion_image(visual_prompt))

        else:
            return None, None

        # reset index for new prompt
        self.index = 0

        current_visual, current_voice = self.story_telling()
        return current_visual, current_voice

    # Load the visual and voice path
    def story_telling(self):
        if self.index > 2:
            return None, None

        current_visual = self.visual[self.index]
        current_voice = self.voice[self.index]

        # increase index
        self.index += 1
        return current_visual, current_voice


gr.close_all()
with gr.Blocks(css="header {visibility: hidden}") as demo:
    generator = MyGenerator()
    with gr.Row():
        with gr.Column():
            prompt = gr.Textbox(
                label="Story you want to hear!",
                lines=1,
                value="Hoàng hậu ngủ trong rừng",
            )

            btn_submit = gr.Button("Submit")
            examples = gr.Examples(
                examples=[
                    "Hoàng hậu ngủ trong rừng",
                    "Cậu bé quàng khăn đỏ",
                    "Bạch tuyết và ba chú lùn",
                ],
                inputs=[prompt],
            )

            visual = gr.Image(image_mode="auto", shape=(512, 512))
            voice = gr.Audio(type="filepath", autoplay=True)

            btn_next = gr.Button("Next")

            # active buttons
            btn_submit.click(
                fn=generator.read_prompt, inputs=[prompt], outputs=[visual, voice]
            )
            btn_next.click(fn=generator.story_telling, outputs=[visual, voice])

        with gr.Column():
            pass
    demo.launch(share=False, debug=False)
