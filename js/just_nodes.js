import { app } from "../../scripts/app.js";

// Toggle widget visibility and handle seed's companion control widget
function setWidgetVisible(node, name, visible) {
  const w = node.widgets.find((w) => w.name === name);
  if (!w) return;
  w.type = visible ? w._origType || "number" : "hidden";

  // ComfyUI adds a control_after_generate widget right after seed
  if (name === "seed") {
    const seedIdx = node.widgets.indexOf(w);
    if (seedIdx !== -1 && seedIdx + 1 < node.widgets.length) {
      const control = node.widgets[seedIdx + 1];
      if (control.name === "control_after_generate") {
        control.type = visible ? control._origType || "combo" : "hidden";
      }
    }
  }
}

// Store original widget types so we can restore them
function storeOrigTypes(node, names) {
  for (const name of names) {
    const w = node.widgets.find((w) => w.name === name);
    if (w && !w._origType) w._origType = w.type;
  }
  // Also store for seed's control widget
  const seedW = node.widgets.find((w) => w.name === "seed");
  if (seedW) {
    const idx = node.widgets.indexOf(seedW);
    if (idx !== -1 && idx + 1 < node.widgets.length) {
      const control = node.widgets[idx + 1];
      if (control.name === "control_after_generate" && !control._origType) {
        control._origType = control.type;
      }
    }
  }
}

function updateModeVisibility(node, manualWidgets, randomWidgets) {
  const modeWidget = node.widgets.find((w) => w.name === "mode");
  if (!modeWidget) return;
  const isRandom = modeWidget.value === "random";

  for (const name of manualWidgets) setWidgetVisible(node, name, !isRandom);
  for (const name of randomWidgets) setWidgetVisible(node, name, isRandom);

  node.setSize(node.computeSize());
}

function hookModeWidget(node, manualWidgets, randomWidgets) {
  storeOrigTypes(node, [...manualWidgets, ...randomWidgets]);

  const modeWidget = node.widgets.find((w) => w.name === "mode");
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
        hookModeWidget(this, ["line"], ["seed"]);
        updateModeVisibility(this, ["line"], ["seed"]);
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

        this.setSize(this.computeSize());
      };

      const onConfigure = nodeType.prototype.onConfigure;
      nodeType.prototype.onConfigure = function (data) {
        onConfigure?.apply(this, arguments);
        storeOrigTypes(this, ["line", "seed"]);
        updateModeVisibility(this, ["line"], ["seed"]);
      };
    }

    // --- Search & Replace: pairs slider controls visibility ---
    if (nodeData.name === "SearchReplace_JN") {
      function updatePairsVisibility(node) {
        const pairsWidget = node.widgets.find((w) => w.name === "pairs");
        if (!pairsWidget) return;
        const visible = pairsWidget.value;

        for (const w of node.widgets) {
          const match = w.name.match(/^(search|replace)_(\d+)$/);
          if (match) {
            const num = parseInt(match[2]);
            w.type = num <= visible ? "STRING" : "hidden";
          }
        }
        node.setSize(node.computeSize());
      }

      const onNodeCreated = nodeType.prototype.onNodeCreated;
      nodeType.prototype.onNodeCreated = function () {
        onNodeCreated?.apply(this, arguments);
        updatePairsVisibility(this);

        const pairsWidget = this.widgets.find((w) => w.name === "pairs");
        if (pairsWidget) {
          const origCallback = pairsWidget.callback;
          pairsWidget.callback = (value) => {
            origCallback?.call(pairsWidget, value);
            updatePairsVisibility(this);
          };
        }
      };

      const onConfigure = nodeType.prototype.onConfigure;
      nodeType.prototype.onConfigure = function (data) {
        onConfigure?.apply(this, arguments);
        updatePairsVisibility(this);
      };
    }

    // --- Labeled Index: mode visibility ---
    if (nodeData.name === "LabeledIndex_JN") {
      const onNodeCreated = nodeType.prototype.onNodeCreated;
      nodeType.prototype.onNodeCreated = function () {
        onNodeCreated?.apply(this, arguments);
        hookModeWidget(this, ["value"], ["seed", "min", "max"]);
        updateModeVisibility(this, ["value"], ["seed", "min", "max"]);
      };

      const onConfigure = nodeType.prototype.onConfigure;
      nodeType.prototype.onConfigure = function (data) {
        onConfigure?.apply(this, arguments);
        storeOrigTypes(this, ["value", "seed", "min", "max"]);
        updateModeVisibility(this, ["value"], ["seed", "min", "max"]);
      };
    }
  },
});
