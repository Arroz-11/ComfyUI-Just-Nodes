import os
import re
import json
import random
from pathlib import Path
import numpy as np
import torch
from PIL import Image, ImageOps
import folder_paths
import comfy.sd
import comfy.utils

PRESETS_DIR = os.path.join(os.path.dirname(__file__), "presets")

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


def _picker_inputs(count):
    inputs = {
        "required": {
            "select": ("INT", {"default": 0, "min": 0, "max": count - 1}),
            "mode": (["manual", "random"],),
            "line": ("INT", {"default": 0, "min": 0}),
            "seed": ("INT", {"default": 0, "min": 0, "max": 0xFFFFFFFFFFFFFFFF}),
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


def _load_preset_names():
    """Load preset names from presets.json for the dropdown."""
    presets_file = os.path.join(PRESETS_DIR, "presets.json")
    if not os.path.isfile(presets_file):
        return ["NO PRESETS FOUND"]
    try:
        with open(presets_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        return list(data.keys()) if data else ["EMPTY"]
    except Exception:
        return ["ERROR LOADING PRESETS"]


class PresetManager:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "preset": (_load_preset_names(),),
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xFFFFFFFFFFFFFFFF}),
                "prompt_template": ("STRING", {
                    "multiline": True,
                    "default": "A beautiful {COLOR} {TYPE} flower, {SIZE} size, in a garden."
                }),
            },
            "optional": {
                "preset_index": ("INT", {"default": -1, "min": -1, "max": 999}),
            },
        }

    RETURN_TYPES = ("STRING", "STRING",)
    RETURN_NAMES = ("prompt", "extra_text",)
    FUNCTION = "execute"
    CATEGORY = "\U0001f48e Just Nodes"

    @classmethod
    def IS_CHANGED(cls, **kwargs):
        return float("nan")

    def execute(self, preset, seed, prompt_template, preset_index=-1):
        # Load presets and lists
        presets_file = os.path.join(PRESETS_DIR, "presets.json")
        lists_file = os.path.join(PRESETS_DIR, "lists.json")

        with open(presets_file, "r", encoding="utf-8") as f:
            presets = json.load(f)

        with open(lists_file, "r", encoding="utf-8") as f:
            lists = json.load(f)

        # If preset_index is >= 0, use it instead of the dropdown
        if preset_index >= 0:
            preset_names = list(presets.keys())
            if preset_index < len(preset_names):
                preset = preset_names[preset_index]
            else:
                return (f"ERROR: preset_index {preset_index} out of range (max {len(preset_names) - 1})", "")

        if preset not in presets:
            return ("ERROR: Preset not found", "")

        preset_config = presets[preset]
        rng = random.Random(seed)
        values = {}
        extra_text = ""

        for var_name, var_config in preset_config.items():
            if var_name == "_extra_text":
                extra_text = var_config if isinstance(var_config, str) else str(var_config)
                continue

            mode = var_config.get("mode", "random")

            if mode == "manual":
                values[var_name] = var_config.get("value", "")
            else:
                # Random: pick from the list
                if var_name in lists and lists[var_name]:
                    values[var_name] = rng.choice(lists[var_name])
                else:
                    values[var_name] = ""

        # Replace {VARIABLES} in the template
        result = prompt_template
        for var_name, var_value in values.items():
            result = result.replace(f"{{{var_name}}}", var_value)

        # Replace {VARIABLES} in extra_text too
        for var_name, var_value in values.items():
            extra_text = extra_text.replace(f"{{{var_name}}}", var_value)

        return (result, extra_text,)


class SaveImageWithText:
    def __init__(self):
        self.counter = 0

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "path": ("STRING", {"default": "output"}),
                "filename_prefix": ("STRING", {"default": "JN"}),
                "filename_delimiter": ("STRING", {"default": "_"}),
                "filename_padding": ("INT", {"default": 4, "min": 1, "max": 9}),
                "extension": (["png", "jpg", "webp"],),
                "quality": ("INT", {"default": 100, "min": 1, "max": 100}),
                "embed_workflow": ("BOOLEAN", {"default": False}),
                "show_preview": ("BOOLEAN", {"default": True}),
            },
            "optional": {
                "text": ("STRING", {"forceInput": True}),
            },
            "hidden": {
                "prompt": "PROMPT",
                "extra_pnginfo": "EXTRA_PNGINFO",
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("filepath",)
    FUNCTION = "execute"
    OUTPUT_NODE = True
    CATEGORY = "\U0001f48e Just Nodes"

    def execute(self, image, path, filename_prefix, filename_delimiter,
                filename_padding, extension, quality, embed_workflow,
                show_preview, text=None, prompt=None, extra_pnginfo=None):
        from PIL.PngImagePlugin import PngInfo
        from datetime import datetime

        # Resolve path
        if not os.path.isabs(path):
            path = os.path.join(folder_paths.get_output_directory(), path)
        os.makedirs(path, exist_ok=True)

        # Find next counter
        existing = [f for f in os.listdir(path) if f.startswith(filename_prefix)]
        counter = len(existing)

        results = []
        filepaths = []

        for i in range(image.shape[0]):
            img = image[i]
            img_np = (img.cpu().numpy() * 255).astype(np.uint8)
            pil_img = Image.fromarray(img_np)

            num = str(counter + i).zfill(filename_padding)
            filename = f"{filename_prefix}{filename_delimiter}{num}.{extension}"
            filepath = os.path.join(path, filename)

            save_kwargs = {}

            if extension == "png":
                metadata = PngInfo()
                if text:
                    metadata.add_text("just_text", text)
                if embed_workflow:
                    if prompt is not None:
                        metadata.add_text("prompt", json.dumps(prompt))
                    if extra_pnginfo is not None:
                        for k, v in extra_pnginfo.items():
                            metadata.add_text(k, json.dumps(v))
                save_kwargs["pnginfo"] = metadata

            elif extension == "jpg":
                save_kwargs["quality"] = quality
                pil_img = pil_img.convert("RGB")

            elif extension == "webp":
                save_kwargs["quality"] = quality
                save_kwargs["lossless"] = quality == 100

            pil_img.save(filepath, **save_kwargs)

            # For jpg/webp, embed text as companion .txt file
            if extension != "png" and text:
                txt_path = os.path.splitext(filepath)[0] + ".txt"
                with open(txt_path, "w", encoding="utf-8") as f:
                    f.write(text)

            filepaths.append(filepath)

            if show_preview:
                # Get relative path for ComfyUI preview
                output_dir = folder_paths.get_output_directory()
                try:
                    rel = os.path.relpath(path, output_dir)
                except ValueError:
                    rel = ""
                results.append({
                    "filename": filename,
                    "subfolder": rel if rel != "." else "",
                    "type": "output",
                })

        return {"ui": {"images": results}, "result": (filepaths[0] if filepaths else "",)}


class LoadImageWithText:
    @classmethod
    def INPUT_TYPES(cls):
        input_dir = folder_paths.get_input_directory()
        files = sorted([
            f for f in os.listdir(input_dir)
            if os.path.splitext(f)[1].lower() in IMAGE_EXTENSIONS
        ])
        return {
            "required": {
                "image": (files, {"image_upload": True}),
            },
        }

    RETURN_TYPES = ("IMAGE", "MASK", "STRING",)
    RETURN_NAMES = ("image", "mask", "text",)
    FUNCTION = "execute"
    CATEGORY = "\U0001f48e Just Nodes"

    def execute(self, image):
        image_path = folder_paths.get_annotated_filepath(image)

        pil_img = Image.open(image_path)
        pil_img = ImageOps.exif_transpose(pil_img)

        # Extract text from PNG metadata
        text = ""
        if hasattr(pil_img, "info") and "just_text" in pil_img.info:
            text = pil_img.info["just_text"]

        img = pil_img.convert("RGB")
        img_np = np.array(img).astype(np.float32) / 255.0
        img_tensor = torch.from_numpy(img_np)[None,]

        if "A" in pil_img.getbands():
            mask = np.array(pil_img.getchannel("A")).astype(np.float32) / 255.0
            mask = 1.0 - torch.from_numpy(mask)
        else:
            mask = torch.zeros((64, 64), dtype=torch.float32)

        return (img_tensor, mask.unsqueeze(0), text,)

    @classmethod
    def IS_CHANGED(cls, image):
        image_path = folder_paths.get_annotated_filepath(image)
        import hashlib
        m = hashlib.sha256()
        with open(image_path, "rb") as f:
            m.update(f.read())
        return m.digest().hex()

    @classmethod
    def VALIDATE_INPUTS(cls, image):
        if not folder_paths.exists_annotated_filepath(image):
            return f"Invalid image file: {image}"
        return True
