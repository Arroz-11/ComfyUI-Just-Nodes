# ComfyUI-Just-Nodes

Utility nodes for ComfyUI that solve common tasks without chaining multiple nodes.

## Nodes

### Prompt Stack
Multiline text input that strips empty lines and outputs clean text joined by newlines.

### Picker
Connect multiple text inputs and select one by index or randomly. Inputs grow dynamically as you connect them.

- **manual** mode: select which connected input to use (`list`) and which line within it (`index`)
- **random** mode: uses `seed` to pick a line (`seed % num_lines`)

### Search & Replace
Takes text input and applies search/replace pairs sequentially. Pairs appear as you fill them in (up to 20). Replace widgets support "Convert to input" for dynamic values.

### Labeled Index
Decorative labels alongside an integer passthrough. Write label names in the multiline field as visual reference — the output is the `value` integer unchanged.

### Preset Manager
Loads presets from `presets/presets.json` and `presets/lists.json`. Resolves `{VARIABLE}` placeholders in templates using either manual values or random picks from lists. Supports synchronized pools and an LLM system prompt slot.

**Outputs (6):**

| Output | Source | Notes |
|---|---|---|
| `prompt` | input `prompt_template` > pool `positive` > preset `_template` | required path |
| `extra_text` | input `extra_text_override` > pool `extra_text` > preset `_extra_text` | optional |
| `output_path` | preset `_output_path` | for `SaveImageWithText_JN` |
| `output_prefix` | preset `_output_prefix` | for `SaveImageWithText_JN` |
| `negative` | input `negative_template` > pool `negative` > preset `_negative` | optional |
| `system_prompt` | input `system_prompt_override` > pool `system_prompt` > preset `_system_prompt` | for LLM nodes (e.g. QwenVL) |

**Preset special fields:** `_template`, `_extra_text`, `_negative`, `_system_prompt`, `_pool`, `_output_path`, `_output_prefix`.

**Pool entries** are dicts with keys `positive`, `negative`, `extra_text`, `system_prompt`. If `_pool` is defined, the seed selects `seed % len(pool)` and bypasses `_template`/`_extra_text`/`_negative`/`_system_prompt`.

**Variable modes:** `"mode": "manual"` (uses `value`) or `"mode": "random"` (picks from `lists.json[VAR_NAME]`).

## Installation

### ComfyUI Manager
Search for "Just Nodes" in the ComfyUI Manager.

### Manual
Clone into your `custom_nodes` folder:
```
cd ComfyUI/custom_nodes
git clone https://github.com/Arroz-11/ComfyUI-Just-Nodes.git
```

Restart ComfyUI. Nodes appear under the **Just Nodes** category.

## License

MIT
