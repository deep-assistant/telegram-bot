import re

from services.utils import find_in_list, find_in_list_by_field

image_models = [
    {"value": "sdxl", "label": "sdxl"},
    {"value": "anything-v5", "label": "anything-v5"},
    {"value": "dark-sushi-25d", "label": "dark-sushi-25d"},
    {"value": "dark-sushi-mix", "label": "dark-sushi-mix"},
    {"value": "cityedgestylemix", "label": "cityedgestylemix"},
    {"value": "cetusmix", "label": "cetusmix"},
    {"value": "ghostmix", "label": "ghostmix"},
    {"value": "dosmix", "label": "dosmix"},
    {"value": "ddosmix", "label": "ddosmix"},
    {"value": "cinnamon", "label": "cinnamon"},
    {"value": "three-delicacy-wonton", "label": "three-delicacy-wonton"},
    {"value": "m9rbgas9t4w", "label": "m9rbgas9t4w"},
    {"value": "majicmixrealistic", "label": "majicmixrealistic"},
    {"value": "majicmixsombre", "label": "majicmixsombre"},
    {"value": "majicmixfantasy", "label": "majicmixfantasy"},
    {"value": "cyberrealistic", "label": "cyberrealistic"},
    {"value": "chilloutmix", "label": "chilloutmix"}
]

samplers = [
    {
        "value": "Euler",
        "label": "Euler",
    },
    {
        "value": "Euler a",
        "label": "EulerA",
    },
    {
        "value": "Heun",
        "label": "Heun",
    },
    {
        "value": "DPM++ 2MKarras",
        "label": "DPM++2MKarras",
    },
    {
        "value": "DPM++ SDE Karras",
        "label": "DPM++SDEKarras",
    },
    {
        "value": "DDIM",
        "label": "DDIM",
    },
]

cgf_values = list(range(0, 22, 2))
steps_values = [21, 31, 41, 51]
size_values = ["512x512", "512x768", "768x512", "768x768", "1024x1024"]
samplers_values = [sampler["label"] for sampler in samplers]
image_models_values = [image_model["label"] for image_model in image_models]


def get_image_model_by_value(label: str):
    return find_in_list_by_field(image_models, "value", label)


def get_image_model_by_label(label: str):
    return find_in_list_by_field(image_models, "label", label)


def get_samplers_by_value(label: str):
    return find_in_list_by_field(image_models, "value", label)


def get_samplers_by_label(label: str):
    return find_in_list_by_field(samplers, "label", label)


def format_image_from_request(text: str):
    pattern1 = r'\{\s*"prompt"\s*:\s*".*?",\s*"size"\s*:\s*".*?"\s*\}'
    answer_text_re1 = re.sub(pattern1, '', text, flags=re.DOTALL)
    pattern2 = r'\{\s*"prompt"\s*:\s*".*?,\s*"size"\s*:\s*".*?",\s*"n"\s*:\s*\d+\s*\}'
    answer_text_re2 = re.sub(pattern2, '', answer_text_re1, flags=re.DOTALL)
    pattern3 = r'!\[image\]\(https://files\.oaiusercontent\.com/file-.*?\)'
    answer_text_re3 = re.sub(pattern3, '', answer_text_re2)

    image = get_image_form_response(answer_text_re2)

    return {
        "image": image,
        "text": answer_text_re3
    }


def get_image_form_response(text):
    pattern = r'!\[image\]\((https://files\.oaiusercontent\.com/file-.*?)\)'

    match = re.search(pattern, text)

    if match:
        image_url = match.group(1)
        return image_url
    else:
        return None
