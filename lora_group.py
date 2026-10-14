import json
import math
import os

import folder_paths
from nodes import LoraLoaderModelOnly


class LoraGroupModelOnly:
    def __init__(self):
        self.loaders = []

    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {
            "model": ("MODEL",),
            "loras": ("STRING", {"default": "[]"}),
        }}

    RETURN_TYPES = ("MODEL",)
    RETURN_NAMES = ("model",)
    FUNCTION = "load_loras"
    CATEGORY = "💎 Just Nodes"
    DESCRIPTION = "Apply up to 12 LoRAs in order using the core Model Only loader."

    def load_loras(self, model, loras):
        rows = json.loads(loras)
        if not isinstance(rows, list) or len(rows) > 12:
            raise ValueError("LoRA Group requires a list of at most 12 LoRAs.")
        selected = []
        available = set(folder_paths.get_filename_list("loras"))
        for index, row in enumerate(rows, 1):
            if not isinstance(row, dict):
                raise ValueError(f"LoRA {index}: invalid row.")
            enabled = row.get("enabled", True)
            if not isinstance(enabled, bool):
                raise ValueError(f"LoRA {index}: enabled must be true or false.")
            if not enabled:
                continue
            name = row.get("lora", "")
            weight = row.get("weight", 1.0)
            if isinstance(weight, bool) or not isinstance(weight, (int, float)) or not math.isfinite(weight) or not -100 <= weight <= 100:
                raise ValueError(f"LoRA {index}: weight must be between -100 and 100.")
            if not name or weight == 0:
                continue
            if not isinstance(name, str) or name not in available:
                raise ValueError(f"LoRA {index}: file missing. Refresh the list and select an existing LoRA.")
            path = folder_paths.get_full_path_or_raise("loras", name)
            stat = os.stat(path)
            selected.append((name, weight, (path, stat.st_mtime_ns, stat.st_size)))
        self.loaders = self.loaders[:len(selected)]
        for index, (name, weight, signature) in enumerate(selected):
            if index >= len(self.loaders):
                self.loaders.append((signature, LoraLoaderModelOnly()))
            elif self.loaders[index][0] != signature:
                self.loaders[index] = (signature, LoraLoaderModelOnly())
            loader = self.loaders[index][1]
            model = loader.load_lora_model_only(model, name, weight)[0]
        return (model,)
