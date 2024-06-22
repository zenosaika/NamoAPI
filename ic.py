import torch
from PIL import Image
from io import BytesIO
import requests

from transformers import AutoProcessor, AutoModelForVision2Seq
from transformers.image_utils import load_image

DEVICE = "cuda:0"

processor = AutoProcessor.from_pretrained("/app/idefics2-8b")
model = AutoModelForVision2Seq.from_pretrained("/app/idefics2-8b").to(DEVICE)


def get_caption(img_url):
    response = requests.get(img_url, stream=True)

    image = Image.open(BytesIO(response.content))
    image = image.convert('RGB')

    question = "Considering the spatial distribution of NDVI values in this image, (green square is the highest NDVI). please identify any patterns or trends that suggest variations in plant growth stages or health across the landscape?"

    messages = [
        {
            "role": "user",
            "content": [
                {"type": "image"},
                {"type": "text", "text": question},
            ]
        },

    ]

    prompt = processor.apply_chat_template(messages, add_generation_prompt=True)
    inputs = processor(text=prompt, images=[image], return_tensors="pt")
    inputs = {k: v.to(DEVICE) for k, v in inputs.items()}

    generated_ids = model.generate(**inputs, max_new_tokens=500)
    generated_texts = processor.batch_decode(generated_ids, skip_special_tokens=True)

    return generated_texts[len(question):]