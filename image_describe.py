from transformers import AutoModelForCausalLM, AutoTokenizer
from PIL import Image
import time
import sys

start_time = time.time()

model_id = "vikhyatk/moondream2"
revision = "2024-07-23"
model = AutoModelForCausalLM.from_pretrained(
    model_id, trust_remote_code=True, revision=revision
)
tokenizer = AutoTokenizer.from_pretrained(model_id, revision=revision)

image = Image.open(sys.argv[1])
enc_image = model.encode_image(image)
print(
    model.answer_question(
        enc_image,
        "Describe the clothing item you see in the center of the image as succinctly as possible, only describe the clothing and print no more tokens: The clothing item in the center of the image is a",
        tokenizer,
    )
)

end_time = time.time()
print("It took this long to run: {}".format(end_time - start_time))

# import requests
# import torch
# import sys
# from PIL import Image
# from transformers import AutoProcessor, AutoModelForCausalLM

# device = "cuda:0" if torch.cuda.is_available() else "cpu"
# torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32

# model = AutoModelForCausalLM.from_pretrained(
#     "microsoft/Florence-2-base", torch_dtype=torch_dtype, trust_remote_code=True
# ).to(device)
# processor = AutoProcessor.from_pretrained(
#     "microsoft/Florence-2-base", trust_remote_code=True
# )

# prompt = "<CAPTION_TO_PHRASE_GROUNDING>Describe the clothing item you see in the center of the image as succinctly as possible, only describe the clothing and print no more tokens: The clothing item in the center of the image is a"

# image = Image.open(sys.argv[1])

# inputs = processor(text=prompt, images=image, return_tensors="pt").to(
#     device, torch_dtype
# )

# generated_ids = model.generate(
#     input_ids=inputs["input_ids"],
#     pixel_values=inputs["pixel_values"],
#     max_new_tokens=1024,
#     num_beams=3,
# )
# generated_text = processor.batch_decode(generated_ids, skip_special_tokens=False)[0]

# parsed_answer = processor.post_process_generation(
#     generated_text, task="<OD>", image_size=(image.width, image.height)
# )

# print(parsed_answer)
