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
                "list": ("INT", {"default": 0, "min": 0, "max": 19}),
                "mode": (["manual", "random"],),
                "index": ("INT", {"default": 0, "min": 0}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xFFFFFFFFFFFFFFFF}),
            },
            "optional": {},
        }
        for i in range(20):
            inputs["optional"][f"input_{i}"] = ("STRING", {"forceInput": True})
        return inputs

    @classmethod
    def VALIDATE_INPUTS(cls, **kwargs):
        return True

    RETURN_TYPES = ("STRING",)
    FUNCTION = "execute"
    CATEGORY = "\U0001f48e Just Nodes"

    def execute(self, list, mode, index, seed, **kwargs):
        connected = []
        for i in range(20):
            key = f"input_{i}"
            if key in kwargs and kwargs[key] is not None:
                connected.append(kwargs[key])

        if not connected:
            return ("",)

        slot = max(0, min(list, len(connected) - 1))
        text = connected[slot]
        lines = [line for line in text.split("\n") if line.strip()]

        if not lines:
            return ("",)

        if mode == "random":
            pick = seed % len(lines)
        else:
            pick = max(0, min(index, len(lines) - 1))

        return (lines[pick],)


class SearchReplace:
    @classmethod
    def INPUT_TYPES(cls):
        inputs = {
            "required": {
                "text": ("STRING", {"forceInput": True}),
            },
            "optional": {},
        }
        for i in range(1, 21):
            inputs["optional"][f"search_{i}"] = ("STRING", {"default": ""})
            inputs["optional"][f"replace_{i}"] = ("STRING", {"default": ""})
        return inputs

    @classmethod
    def VALIDATE_INPUTS(cls, **kwargs):
        return True

    RETURN_TYPES = ("STRING",)
    FUNCTION = "execute"
    CATEGORY = "\U0001f48e Just Nodes"

    def execute(self, text, **kwargs):
        result = text
        for i in range(1, 21):
            search_key = f"search_{i}"
            replace_key = f"replace_{i}"
            search = kwargs.get(search_key, "")
            replace = kwargs.get(replace_key, "")
            if search:
                result = result.replace(search, replace)
        return (result,)


class LabeledIndex:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "labels": ("STRING", {"multiline": True, "default": "Option A\nOption B\nOption C"}),
                "value": ("INT", {"default": 0, "min": 0}),
            }
        }

    RETURN_TYPES = ("INT",)
    FUNCTION = "execute"
    CATEGORY = "\U0001f48e Just Nodes"

    def execute(self, labels, value):
        return (value,)
