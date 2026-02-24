import os
import re
from pathlib import Path
import numpy as np
import torch
from PIL import Image, ImageOps
import folder_paths
import comfy.sd
import comfy.utils

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
                "select": ("INT", {"default": 0, "min": 0, "max": 19,
                                   "control_after_generate": "fixed"}),
                "mode": (["manual", "random"],),
                "line": ("INT", {"default": 0, "min": 0,
                                 "control_after_generate": "fixed"}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xFFFFFFFFFFFFFFFF,
                                 "control_after_generate": "randomize"}),
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


def _picker_inputs(count):
    inputs = {
        "required": {
            "select": ("INT", {"default": 0, "min": 0, "max": count - 1,
                               "control_after_generate": "fixed"}),
            "mode": (["manual", "random"],),
            "line": ("INT", {"default": 0, "min": 0,
                             "control_after_generate": "fixed"}),
            "seed": ("INT", {"default": 0, "min": 0, "max": 0xFFFFFFFFFFFFFFFF,
                             "control_after_generate": "randomize"}),
        },
        "optional": {},
    }
    for i in range(1, count + 1):
        inputs["optional"][f"text_{i}"] = ("STRING", {"forceInput": True})
    return inputs


def _picker_execute(select, mode, line, seed, count, **kwargs):
    connected = []
    for i in range(1, count + 1):
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


class Picker_x1:
    @classmethod
    def INPUT_TYPES(cls):
        return _picker_inputs(1)

    @classmethod
    def VALIDATE_INPUTS(cls, **kwargs):
        return True

    RETURN_TYPES = ("STRING",)
    FUNCTION = "execute"
    CATEGORY = "\U0001f48e Just Nodes"

    def execute(self, select, mode, line, seed, **kwargs):
        return _picker_execute(select, mode, line, seed, 1, **kwargs)


class Picker_x3:
    @classmethod
    def INPUT_TYPES(cls):
        return _picker_inputs(3)

    @classmethod
    def VALIDATE_INPUTS(cls, **kwargs):
        return True

    RETURN_TYPES = ("STRING",)
    FUNCTION = "execute"
    CATEGORY = "\U0001f48e Just Nodes"

    def execute(self, select, mode, line, seed, **kwargs):
        return _picker_execute(select, mode, line, seed, 3, **kwargs)


class Picker_x6:
    @classmethod
    def INPUT_TYPES(cls):
        return _picker_inputs(6)

    @classmethod
    def VALIDATE_INPUTS(cls, **kwargs):
        return True

    RETURN_TYPES = ("STRING",)
    FUNCTION = "execute"
    CATEGORY = "\U0001f48e Just Nodes"

    def execute(self, select, mode, line, seed, **kwargs):
        return _picker_execute(select, mode, line, seed, 6, **kwargs)


class Picker_x9:
    @classmethod
    def INPUT_TYPES(cls):
        return _picker_inputs(9)

    @classmethod
    def VALIDATE_INPUTS(cls, **kwargs):
        return True

    RETURN_TYPES = ("STRING",)
    FUNCTION = "execute"
    CATEGORY = "\U0001f48e Just Nodes"

    def execute(self, select, mode, line, seed, **kwargs):
        return _picker_execute(select, mode, line, seed, 9, **kwargs)


class Picker_x12:
    @classmethod
    def INPUT_TYPES(cls):
        return _picker_inputs(12)

    @classmethod
    def VALIDATE_INPUTS(cls, **kwargs):
        return True

    RETURN_TYPES = ("STRING",)
    FUNCTION = "execute"
    CATEGORY = "\U0001f48e Just Nodes"

    def execute(self, select, mode, line, seed, **kwargs):
        return _picker_execute(select, mode, line, seed, 12, **kwargs)


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


class SearchReplace_x12:
    @classmethod
    def INPUT_TYPES(cls):
        return _search_replace_inputs(12)

    @classmethod
    def VALIDATE_INPUTS(cls, **kwargs):
        return True

    RETURN_TYPES = ("STRING",)
    FUNCTION = "execute"
    CATEGORY = "\U0001f48e Just Nodes"

    def execute(self, text, **kwargs):
        return _search_replace_execute(text, 12, **kwargs)


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


class ModelChecker:
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {}}

    RETURN_TYPES = ()
    FUNCTION = "execute"
    CATEGORY = "\U0001f48e Just Nodes"

    def execute(self):
        return {}


class LoraTagModelOnly:
    TAG_PATTERN = r"\<[0-9a-zA-Z\:\_\-\.\s\/\(\)\\\\]+\>"

    def __init__(self):
        self.loaded_loras = {}

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "model": ("MODEL",),
                "text": ("STRING", {"multiline": True}),
            },
        }

    RETURN_TYPES = ("MODEL",)
    RETURN_NAMES = ("MODEL",)
    FUNCTION = "execute"
    CATEGORY = "\U0001f48e Just Nodes"

    def execute(self, model, text):
        founds = re.findall(self.TAG_PATTERN, text)
        if not founds:
            return (model,)

        model_lora = model
        lora_files = folder_paths.get_filename_list("loras")
        used_paths = set()

        for f in founds:
            tag = f[1:-1]
            pak = tag.split(":")
            if pak[0] != "lora":
                continue
            if len(pak) < 2 or not pak[1]:
                continue

            name = pak[1]
            strength = 0.0
            try:
                if len(pak) > 2 and pak[2]:
                    strength = float(pak[2])
            except ValueError:
                continue

            lora_name = None
            for lora_file in lora_files:
                if Path(lora_file).name.startswith(name) or lora_file.startswith(name):
                    lora_name = lora_file
                    break

            if lora_name is None:
                print(f"[LoraTagModelOnly] not found: <lora:{name}:{strength}>")
                continue

            lora_path = folder_paths.get_full_path("loras", lora_name)
            if lora_path is None:
                continue

            used_paths.add(lora_path)
            print(f"[LoraTagModelOnly] applying: <lora:{name}:{strength}> -> {lora_name}")

            if lora_path in self.loaded_loras:
                lora = self.loaded_loras[lora_path]
            else:
                lora = comfy.utils.load_torch_file(lora_path, safe_load=True)
                self.loaded_loras[lora_path] = lora

            model_lora, _ = comfy.sd.load_lora_for_models(
                model_lora, None, lora, strength, 0
            )

        for k in [k for k in self.loaded_loras if k not in used_paths]:
            del self.loaded_loras[k]

        return (model_lora,)


class BatchStepper:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "total_runs": ("INT", {"default": 10, "min": 1, "max": 0xFFFFFFFFFFFFFFFF}),
                "step": ("INT", {"default": 0, "min": 0, "max": 0xFFFFFFFFFFFFFFFF}),
                "step_limit": ("INT", {"default": 5, "min": 1, "max": 0xFFFFFFFFFFFFFFFF}),
                "mode": ("BOOLEAN", {"default": True, "label_on": "Run", "label_off": "Stop"}),
            },
        }

    RETURN_TYPES = ("INT",)
    RETURN_NAMES = ("select",)
    FUNCTION = "execute"
    CATEGORY = "\U0001f48e Just Nodes"
    OUTPUT_NODE = True

    def execute(self, total_runs, step, step_limit, mode):
        return (step,)
