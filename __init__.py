from .nodes import PromptStack, Picker, SearchReplace, LabeledIndex

NODE_CLASS_MAPPINGS = {
    "PromptStack_JN": PromptStack,
    "Picker_JN": Picker,
    "SearchReplace_JN": SearchReplace,
    "LabeledIndex_JN": LabeledIndex,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "PromptStack_JN": "Prompt Stack \U0001f48e Just Nodes",
    "Picker_JN": "Picker \U0001f48e Just Nodes",
    "SearchReplace_JN": "Search & Replace \U0001f48e Just Nodes",
    "LabeledIndex_JN": "Labeled Index \U0001f48e Just Nodes",
}

WEB_DIRECTORY = "./js"
