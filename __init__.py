import os
from aiohttp import web
from server import PromptServer

from .nodes import (
    ImageFromFolder,
    PromptStack,
    Picker,
    SearchReplace_x1,
    SearchReplace_x3,
    SearchReplace_x6,
    SearchReplace_x9,
    LabeledIndex,
    ModelChecker,
    IMAGE_EXTENSIONS,
)

NODE_CLASS_MAPPINGS = {
    "ImageFromFolder_JN": ImageFromFolder,
    "PromptStack_JN": PromptStack,
    "Picker_JN": Picker,
    "SearchReplace_x1_JN": SearchReplace_x1,
    "SearchReplace_x3_JN": SearchReplace_x3,
    "SearchReplace_x6_JN": SearchReplace_x6,
    "SearchReplace_x9_JN": SearchReplace_x9,
    "LabeledIndex_JN": LabeledIndex,
    "ModelChecker_JN": ModelChecker,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ImageFromFolder_JN": "Image From Folder \U0001f48e Just Nodes",
    "PromptStack_JN": "Prompt Stack \U0001f48e Just Nodes",
    "Picker_JN": "Picker \U0001f48e Just Nodes",
    "SearchReplace_x1_JN": "Search & Replace x1 \U0001f48e Just Nodes",
    "SearchReplace_x3_JN": "Search & Replace x3 \U0001f48e Just Nodes",
    "SearchReplace_x6_JN": "Search & Replace x6 \U0001f48e Just Nodes",
    "SearchReplace_x9_JN": "Search & Replace x9 \U0001f48e Just Nodes",
    "LabeledIndex_JN": "Labeled Index \U0001f48e Just Nodes",
    "ModelChecker_JN": "Model Checker \U0001f48e Just Nodes",
}

WEB_DIRECTORY = "./js"


@PromptServer.instance.routes.get("/just_nodes/scan_folder")
async def scan_folder(request):
    folder = request.query.get("folder", "")
    if not os.path.isdir(folder):
        return web.json_response({"count": 0})
    count = sum(
        1 for f in os.listdir(folder)
        if os.path.splitext(f)[1].lower() in IMAGE_EXTENSIONS
    )
    return web.json_response({"count": count})


MODEL_EXTENSIONS = {'.safetensors', '.ckpt', '.pt', '.pth', '.bin', '.onnx', '.gguf'}


@PromptServer.instance.routes.post("/just_nodes/check_models")
async def check_models(request):
    import nodes as comfy_nodes

    data = await request.json()
    workflow_nodes = data.get("nodes", [])

    found = []
    missing = []
    debug = []

    for node_info in workflow_nodes:
        class_type = node_info.get("type", "")
        widgets = node_info.get("widgets", {})
        node_id = node_info.get("id", "?")
        title = node_info.get("title", class_type)

        node_class = comfy_nodes.NODE_CLASS_MAPPINGS.get(class_type)
        if not node_class:
            if widgets:
                debug.append(f"[{node_id}] {class_type}: class not in NODE_CLASS_MAPPINGS")
            continue

        try:
            input_types = node_class.INPUT_TYPES()
        except Exception as e:
            debug.append(f"[{node_id}] {class_type}: INPUT_TYPES error: {e}")
            continue

        for category in ("required", "optional"):
            cat_inputs = input_types.get(category, {})
            for input_name, input_config in cat_inputs.items():
                if not isinstance(input_config, (tuple, list)) or len(input_config) == 0:
                    continue
                options = input_config[0]
                if not isinstance(options, (list, tuple)) or len(options) == 0:
                    continue

                is_model = False
                for item in list(options)[:10]:
                    if any(str(item).lower().endswith(ext) for ext in MODEL_EXTENSIONS):
                        is_model = True
                        break

                if not is_model:
                    continue

                value = widgets.get(input_name)
                if not isinstance(value, str) or not value:
                    continue

                entry = {
                    "node_id": node_id,
                    "title": title,
                    "input": input_name,
                    "model": value,
                }

                if value in options:
                    found.append(entry)
                else:
                    missing.append(entry)

    return web.json_response({"found": found, "missing": missing, "debug": debug})
