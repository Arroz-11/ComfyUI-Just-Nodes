import { app } from "../../scripts/app.js";

function toggleWidget(node, widget, show = false) {
  if (!widget) return;

  if (!widget._jn_origType) {
    widget._jn_origType = widget.type;
    widget._jn_origComputeSize = widget.computeSize;
  }

  widget.type = show ? widget._jn_origType : "jnHidden";
  widget.computeSize = show ? widget._jn_origComputeSize : () => [0, -4];

  // Handle linked widgets (e.g. seed → control_after_generate)
  if (widget.linkedWidgets) {
    for (const w of widget.linkedWidgets) {
      toggleWidget(node, w, show);
    }
  }
}

function findWidget(node, name) {
  return node.widgets.find((w) => w.name === name);
}

function updateNodeHeight(node) {
  node.setSize([node.size[0], node.computeSize()[1]]);
}

function updateModeVisibility(node, manualWidgets, randomWidgets) {
  const modeWidget = findWidget(node, "mode");
  if (!modeWidget) return;
  const isRandom = modeWidget.value === "random";

  for (const name of manualWidgets)
    toggleWidget(node, findWidget(node, name), !isRandom);
  for (const name of randomWidgets)
    toggleWidget(node, findWidget(node, name), isRandom);

  updateNodeHeight(node);
}

function hookModeWidget(node, manualWidgets, randomWidgets) {
  const modeWidget = findWidget(node, "mode");
  if (!modeWidget) return;
  const origCallback = modeWidget.callback;
  modeWidget.callback = function (value) {
    origCallback?.call(modeWidget, value);
    updateModeVisibility(node, manualWidgets, randomWidgets);
  };
}

app.registerExtension({
  name: "just_nodes",

  beforeRegisterNodeDef(nodeType, nodeData) {
    // --- Picker: dynamic input slots + refresh button + mode visibility ---
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

        // Mode visibility: manual=line, random=seed
        // Defer to let ComfyUI finish adding all widgets (e.g. control_after_generate)
        const self = this;
        hookModeWidget(this, ["line"], ["seed"]);
        setTimeout(() => {
          updateModeVisibility(self, ["line"], ["seed"]);
        }, 0);
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

        updateNodeHeight(this);
      };

      const onConfigure = nodeType.prototype.onConfigure;
      nodeType.prototype.onConfigure = function (data) {
        onConfigure?.apply(this, arguments);
        setTimeout(() => {
          updateModeVisibility(this, ["line"], ["seed"]);
        }, 0);
      };
    }

    // --- Search & Replace: pairs slider controls visibility ---
    if (nodeData.name === "SearchReplace_JN") {
      function updatePairsVisibility(node) {
        const pairsWidget = findWidget(node, "pairs");
        if (!pairsWidget) return;
        const visible = pairsWidget.value;

        for (const w of node.widgets) {
          const match = w.name.match(/^(search|replace)_(\d+)$/);
          if (match) {
            const num = parseInt(match[2]);
            toggleWidget(node, w, num <= visible);
          }
        }
        updateNodeHeight(node);
      }

      const onNodeCreated = nodeType.prototype.onNodeCreated;
      nodeType.prototype.onNodeCreated = function () {
        onNodeCreated?.apply(this, arguments);

        const self = this;
        const pairsWidget = findWidget(this, "pairs");
        if (pairsWidget) {
          const origCallback = pairsWidget.callback;
          pairsWidget.callback = (value) => {
            origCallback?.call(pairsWidget, value);
            updatePairsVisibility(self);
          };
        }

        // Defer initial hide to let ComfyUI finish widget setup
        setTimeout(() => {
          updatePairsVisibility(self);
        }, 0);
      };

      const onConfigure = nodeType.prototype.onConfigure;
      nodeType.prototype.onConfigure = function (data) {
        onConfigure?.apply(this, arguments);
        const self = this;
        setTimeout(() => {
          updatePairsVisibility(self);
        }, 0);
      };
    }

    // --- Labeled Index: mode visibility ---
    if (nodeData.name === "LabeledIndex_JN") {
      const onNodeCreated = nodeType.prototype.onNodeCreated;
      nodeType.prototype.onNodeCreated = function () {
        onNodeCreated?.apply(this, arguments);

        const self = this;
        hookModeWidget(this, ["value"], ["seed", "min", "max"]);

        // Defer to let ComfyUI finish adding control_after_generate for seed
        setTimeout(() => {
          updateModeVisibility(self, ["value"], ["seed", "min", "max"]);
        }, 0);
      };

      const onConfigure = nodeType.prototype.onConfigure;
      nodeType.prototype.onConfigure = function (data) {
        onConfigure?.apply(this, arguments);
        const self = this;
        setTimeout(() => {
          updateModeVisibility(self, ["value"], ["seed", "min", "max"]);
        }, 0);
      };
    }
  },
});
