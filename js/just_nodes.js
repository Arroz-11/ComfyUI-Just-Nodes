import { app } from "../../scripts/app.js";

function toggleWidget(node, widget, show = false) {
  if (!widget) return;
  if (node.inputs?.some((i) => i.widget?.name === widget.name)) return;

  if (!widget._jn_origType) {
    widget._jn_origType = widget.type;
    widget._jn_origComputeSize = widget.computeSize;
  }

  widget.type = show ? widget._jn_origType : "jnHidden";
  widget.computeSize = show ? widget._jn_origComputeSize : () => [0, -4];

  if (widget.linkedWidgets) {
    for (const w of widget.linkedWidgets) {
      toggleWidget(node, w, show);
    }
  }

  const height = show
    ? Math.max(node.computeSize()[1], node.size[1])
    : node.computeSize()[1];
  node.setSize([node.size[0], height]);
}

function findWidget(node, name) {
  return node.widgets?.find((w) => w.name === name);
}

// Apply mode visibility and install reactive setter via Object.defineProperty
function setupModeToggle(node, manualWidgets, randomWidgets) {
  const modeWidget = findWidget(node, "mode");
  if (!modeWidget) return;

  function applyVisibility() {
    const isRandom = modeWidget.value === "random";
    for (const name of manualWidgets)
      toggleWidget(node, findWidget(node, name), !isRandom);
    for (const name of randomWidgets)
      toggleWidget(node, findWidget(node, name), isRandom);
  }

  // Install reactive setter so every change triggers visibility update
  if (!modeWidget._jn_setter) {
    modeWidget._jn_setter = true;
    let currentValue = modeWidget.value;
    Object.defineProperty(modeWidget, "value", {
      get() {
        return currentValue;
      },
      set(newValue) {
        currentValue = newValue;
        applyVisibility();
      },
      configurable: true,
    });
  }

  applyVisibility();
}

// Apply pairs visibility and install reactive setter
function setupPairsToggle(node) {
  const pairsWidget = findWidget(node, "pairs");
  if (!pairsWidget) return;

  function applyVisibility() {
    const visible = pairsWidget.value;
    for (const w of node.widgets) {
      const match = w.name.match(/^(search|replace)_(\d+)$/);
      if (match) {
        toggleWidget(node, w, parseInt(match[2]) <= visible);
      }
    }
  }

  if (!pairsWidget._jn_setter) {
    pairsWidget._jn_setter = true;
    let currentValue = pairsWidget.value;
    Object.defineProperty(pairsWidget, "value", {
      get() {
        return currentValue;
      },
      set(newValue) {
        currentValue = newValue;
        applyVisibility();
      },
      configurable: true,
    });
  }

  applyVisibility();
}

app.registerExtension({
  name: "just_nodes",

  beforeRegisterNodeDef(nodeType, nodeData) {
    // --- Picker: dynamic input slots ---
    if (nodeData.name === "Picker_JN") {
      const onNodeCreated = nodeType.prototype.onNodeCreated;
      nodeType.prototype.onNodeCreated = function () {
        onNodeCreated?.apply(this, arguments);

        // Remove all optional inputs except text_1
        const toRemove = [];
        for (const inp of this.inputs) {
          if (inp.name.startsWith("text_") && inp.name !== "text_1") {
            toRemove.push(inp.name);
          }
        }
        for (const name of toRemove) {
          const idx = this.inputs.findIndex((i) => i.name === name);
          if (idx !== -1) this.removeInput(idx);
        }

        // Add Refresh button to count lines from connected nodes
        this.addWidget("button", "refresh_lines", null, () => {
          const graph = app.graph;
          for (const inp of this.inputs) {
            if (!inp.name.startsWith("text_")) continue;
            const num = inp.name.match(/^text_(\d+)/)?.[1];
            if (!num) continue;

            if (inp.link != null) {
              const linkInfo = graph.links[inp.link];
              if (linkInfo) {
                const sourceNode = graph.getNodeById(linkInfo.origin_id);
                if (sourceNode) {
                  let text = "";
                  for (const w of sourceNode.widgets || []) {
                    if (
                      w.type === "customtext" ||
                      w.type === "text" ||
                      w.type === "STRING"
                    ) {
                      text = w.value || "";
                      break;
                    }
                  }
                  const lineCount = text
                    .split("\n")
                    .filter((l) => l.trim()).length;
                  inp.label = `text_${num}: ${lineCount} lines`;
                }
              }
            } else {
              inp.label = `text_${num}`;
            }
          }
          this.setDirtyCanvas(true);
        });
      };

      const onConnectionsChange = nodeType.prototype.onConnectionsChange;
      nodeType.prototype.onConnectionsChange = function (
        side,
        slotIndex,
        connected,
      ) {
        onConnectionsChange?.apply(this, arguments);

        if (side !== 1) return;

        const inputSlots = this.inputs.filter((i) =>
          i.name.startsWith("text_"),
        );

        if (connected) {
          const lastInput = inputSlots[inputSlots.length - 1];
          if (lastInput && lastInput.link != null) {
            const nextIndex = inputSlots.length + 1;
            if (nextIndex <= 20) {
              this.addInput(`text_${nextIndex}`, "STRING");
            }
          }
        } else {
          const allInputSlots = this.inputs.filter((i) =>
            i.name.startsWith("text_"),
          );
          for (let i = allInputSlots.length - 1; i >= 1; i--) {
            if (allInputSlots[i].link != null) break;
            allInputSlots[i].label = null;
            const idx = this.inputs.findIndex(
              (inp) => inp.name === allInputSlots[i].name,
            );
            if (idx !== -1) this.removeInput(idx);
          }
        }

        this.setSize([this.size[0], this.computeSize()[1]]);
      };
    }
  },

  // nodeCreated fires AFTER ComfyUI fully creates the node (unlike onNodeCreated)
  nodeCreated(node) {
    const setupWithDelay = (fn) => setTimeout(() => fn(node), 10);

    if (node.comfyClass === "Picker_JN") {
      setupWithDelay((n) => setupModeToggle(n, ["line"], ["seed"]));
    }

    if (node.comfyClass === "SearchReplace_JN") {
      setupWithDelay((n) => setupPairsToggle(n));
    }

    if (node.comfyClass === "LabeledIndex_JN") {
      setupWithDelay((n) =>
        setupModeToggle(n, ["value"], ["seed", "min", "max"]),
      );
    }
  },
});
