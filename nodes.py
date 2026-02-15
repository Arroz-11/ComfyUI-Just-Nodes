import os
import numpy as np
import torch
from PIL import Image, ImageOps

IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp'}


class ImageFromFolder:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "folder": ("STRING", {"default": ""}),
                "index": ("INT", {"default": 0, "min": 0, "max": 0xFFFFFFFFFFFFFFFF,
                                   "control_after_generate": True}),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "execute"
    CATEGORY = "\U0001f48e Just Nodes"

    def execute(self, folder, index):
        if not os.path.isdir(folder):
            raise FileNotFoundError(f"Folder not found: '{folder}'")

        files = sorted(
            f for f in os.listdir(folder)
            if os.path.splitext(f)[1].lower() in IMAGE_EXTENSIONS
        )

        if not files:
            raise FileNotFoundError(f"No images in: '{folder}'")

        if index >= len(files):
            raise IndexError(f"No more images: index {index} but only {len(files)} images in folder")
        path = os.path.join(folder, files[index])

        img = Image.open(path)
        img = ImageOps.exif_transpose(img)
        img = img.convert("RGB")
        image = np.array(img).astype(np.float32) / 255.0
        image = torch.from_numpy(image)[None,]

        return (image,)


class PromptStack:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"multiline": True}),
            }
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "execute"
    CATEGORY = "\U0001f48e Just Nodes"

    def execute(self, text):
        lines = [line for line in text.split("\n") if line.strip()]
        return ("\n".join(lines),)


class Picker:
    @classmethod
    def INPUT_TYPES(cls):
        inputs = {
            "required": {
                "select": ("INT", {"default": 0, "min": 0, "max": 19}),
                "mode": (["manual", "random"],),
                "line": ("INT", {"default": 0, "min": 0}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xFFFFFFFFFFFFFFFF}),
            },
            "optional": {},
        }
        for i in range(1, 21):
            inputs["optional"][f"text_{i}"] = ("STRING", {"forceInput": True})
        return inputs

    @classmethod
    def VALIDATE_INPUTS(cls, **kwargs):
        return True

    RETURN_TYPES = ("STRING",)
    FUNCTION = "execute"
    CATEGORY = "\U0001f48e Just Nodes"

    def execute(self, select, mode, line, seed, **kwargs):
        connected = []
        for i in range(1, 21):
            key = f"text_{i}"
            if key in kwargs and kwargs[key] is not None:
                connected.append(kwargs[key])

        if not connected:
            return ("",)

        slot = max(0, min(select, len(connected) - 1))
        text = connected[slot]
        lines = [ln for ln in text.split("\n") if ln.strip()]

        if not lines:
            return ("",)

        if mode == "random":
            pick = seed % len(lines)
        else:
            pick = max(0, min(line, len(lines) - 1))

        return (lines[pick],)


def _search_replace_execute(text, count, **kwargs):
    result = text
    for i in range(1, count + 1):
        search = kwargs.get(f"search_{i}", "")
        replace = kwargs.get(f"replace_{i}", "")
        if search:
            result = result.replace(search, replace)
    return (result,)


def _search_replace_inputs(count):
    inputs = {
        "required": {
            "text": ("STRING", {"forceInput": True}),
        },
        "optional": {},
    }
    for i in range(1, count + 1):
        inputs["optional"][f"search_{i}"] = ("STRING", {"default": ""})
        inputs["optional"][f"replace_{i}"] = ("STRING", {"default": ""})
    return inputs


class SearchReplace_x1:
    @classmethod
    def INPUT_TYPES(cls):
        return _search_replace_inputs(1)

    @classmethod
    def VALIDATE_INPUTS(cls, **kwargs):
        return True

    RETURN_TYPES = ("STRING",)
    FUNCTION = "execute"
    CATEGORY = "\U0001f48e Just Nodes"

    def execute(self, text, **kwargs):
        return _search_replace_execute(text, 1, **kwargs)


class SearchReplace_x3:
    @classmethod
    def INPUT_TYPES(cls):
        return _search_replace_inputs(3)

    @classmethod
    def VALIDATE_INPUTS(cls, **kwargs):
        return True

    RETURN_TYPES = ("STRING",)
    FUNCTION = "execute"
    CATEGORY = "\U0001f48e Just Nodes"

    def execute(self, text, **kwargs):
        return _search_replace_execute(text, 3, **kwargs)


class SearchReplace_x6:
    @classmethod
    def INPUT_TYPES(cls):
        return _search_replace_inputs(6)

    @classmethod
    def VALIDATE_INPUTS(cls, **kwargs):
        return True

    RETURN_TYPES = ("STRING",)
    FUNCTION = "execute"
    CATEGORY = "\U0001f48e Just Nodes"

    def execute(self, text, **kwargs):
        return _search_replace_execute(text, 6, **kwargs)


class SearchReplace_x9:
    @classmethod
    def INPUT_TYPES(cls):
        return _search_replace_inputs(9)

    @classmethod
    def VALIDATE_INPUTS(cls, **kwargs):
        return True

    RETURN_TYPES = ("STRING",)
    FUNCTION = "execute"
    CATEGORY = "\U0001f48e Just Nodes"

    def execute(self, text, **kwargs):
        return _search_replace_execute(text, 9, **kwargs)


class LabeledIndex:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "labels": ("STRING", {"multiline": True, "default": "Option A\nOption B\nOption C"}),
                "mode": (["manual", "random"],),
                "value": ("INT", {"default": 0, "min": 0}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xFFFFFFFFFFFFFFFF}),
                "min": ("INT", {"default": 0, "min": 0}),
                "max": ("INT", {"default": 19, "min": 0}),
            }
        }

    RETURN_TYPES = ("INT",)
    FUNCTION = "execute"
    CATEGORY = "\U0001f48e Just Nodes"

    def execute(self, labels, mode, value, seed, min, max):
        if mode == "random":
            if max < min:
                max = min
            return (seed % (max - min + 1) + min,)
        return (value,)
