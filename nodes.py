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


class SearchReplace:
    @classmethod
    def INPUT_TYPES(cls):
        inputs = {
            "required": {
                "text": ("STRING", {"forceInput": True}),
                "pairs": ("INT", {"default": 1, "min": 1, "max": 20}),
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

    def execute(self, text, pairs, **kwargs):
        result = text
        for i in range(1, pairs + 1):
            search = kwargs.get(f"search_{i}", "")
            replace = kwargs.get(f"replace_{i}", "")
            if search:
                result = result.replace(search, replace)
        return (result,)


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
