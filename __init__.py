from .nodes import (
    PromptStack,
    Picker,
    SearchReplace_x1,
    SearchReplace_x3,
    SearchReplace_x6,
    SearchReplace_x9,
    LabeledIndex,
)

NODE_CLASS_MAPPINGS = {
    "PromptStack_JN": PromptStack,
    "Picker_JN": Picker,
    "SearchReplace_x1_JN": SearchReplace_x1,
    "SearchReplace_x3_JN": SearchReplace_x3,
    "SearchReplace_x6_JN": SearchReplace_x6,
    "SearchReplace_x9_JN": SearchReplace_x9,
    "LabeledIndex_JN": LabeledIndex,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "PromptStack_JN": "Prompt Stack \U0001f48e Just Nodes",
    "Picker_JN": "Picker \U0001f48e Just Nodes",
    "SearchReplace_x1_JN": "Search & Replace x1 \U0001f48e Just Nodes",
    "SearchReplace_x3_JN": "Search & Replace x3 \U0001f48e Just Nodes",
    "SearchReplace_x6_JN": "Search & Replace x6 \U0001f48e Just Nodes",
    "SearchReplace_x9_JN": "Search & Replace x9 \U0001f48e Just Nodes",
    "LabeledIndex_JN": "Labeled Index \U0001f48e Just Nodes",
}

WEB_DIRECTORY = "./js"
