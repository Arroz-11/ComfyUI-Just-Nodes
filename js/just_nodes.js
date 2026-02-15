import { app } from "../../scripts/app.js";

app.registerExtension({
  name: "just_nodes",

  beforeRegisterNodeDef(nodeType, nodeData) {
    // --- Picker: dynamic input slots ---
    if (nodeData.name === "Picker_JN") {
      const onNodeCreated = nodeType.prototype.onNodeCreated;
      nodeType.prototype.onNodeCreated = function () {
        onNodeCreated?.apply(this, arguments);

        // Remove all optional inputs except input_0
        const toRemove = [];
        for (const inp of this.inputs) {
          if (inp.name.startsWith("input_") && inp.name !== "input_0") {
            toRemove.push(inp.name);
          }
        }
        for (const name of toRemove) {
          const idx = this.inputs.findIndex((i) => i.name === name);
          if (idx !== -1) this.removeInput(idx);
        }

        this.setSize(this.computeSize());
      };

      const onConnectionsChange = nodeType.prototype.onConnectionsChange;
      nodeType.prototype.onConnectionsChange = function (
        side,
        slotIndex,
        connected,
      ) {
        onConnectionsChange?.apply(this, arguments);

        if (side !== 1) return; // 1 = input side

        const inputSlots = this.inputs.filter((i) =>
          i.name.startsWith("input_"),
        );

        if (connected) {
          // If the last input_ slot is now connected, add a new one
          const lastInput = inputSlots[inputSlots.length - 1];
          if (lastInput && lastInput.link != null) {
            const nextIndex = inputSlots.length;
            if (nextIndex < 20) {
              this.addInput(`input_${nextIndex}`, "STRING");
            }
          }
        } else {
          // Remove trailing disconnected slots (keep at least 1)
          const allInputSlots = this.inputs.filter((i) =>
            i.name.startsWith("input_"),
          );
          for (let i = allInputSlots.length - 1; i >= 1; i--) {
            if (allInputSlots[i].link != null) break;
            const idx = this.inputs.findIndex(
              (inp) => inp.name === allInputSlots[i].name,
            );
            if (idx !== -1) this.removeInput(idx);
          }
        }

        this.setSize(this.computeSize());
      };
    }

    // --- Search & Replace: show/hide pairs ---
    if (nodeData.name === "SearchReplace_JN") {
      const onNodeCreated = nodeType.prototype.onNodeCreated;
      nodeType.prototype.onNodeCreated = function () {
        onNodeCreated?.apply(this, arguments);

        // Hide all pairs except pair 1
        for (const w of this.widgets) {
          const match = w.name.match(/^(search|replace)_(\d+)$/);
          if (match) {
            const num = parseInt(match[2]);
            if (num > 1) {
              w.type = "hidden";
            }
          }
        }

        this._visiblePairs = 1;
        this.setSize(this.computeSize());
      };

      const onWidgetChanged = nodeType.prototype.onWidgetChanged;
      nodeType.prototype.onWidgetChanged = function (name, value) {
        onWidgetChanged?.apply(this, arguments);

        const match = name.match(/^search_(\d+)$/);
        if (match) {
          const num = parseInt(match[1]);
          // If user types in the last visible search, show the next pair
          if (num === this._visiblePairs && value.length > 0) {
            const nextPair = num + 1;
            if (nextPair <= 20) {
              const searchWidget = this.widgets.find(
                (w) => w.name === `search_${nextPair}`,
              );
              const replaceWidget = this.widgets.find(
                (w) => w.name === `replace_${nextPair}`,
              );
              if (searchWidget) searchWidget.type = "STRING";
              if (replaceWidget) replaceWidget.type = "STRING";
              this._visiblePairs = nextPair;
              this.setSize(this.computeSize());
            }
          }
        }
      };

      // Restore visibility on deserialization
      const onConfigure = nodeType.prototype.onConfigure;
      nodeType.prototype.onConfigure = function (data) {
        onConfigure?.apply(this, arguments);

        let maxVisible = 1;
        if (data.widgets_values) {
          // Find which pairs have data by scanning widget values
          for (const w of this.widgets) {
            const match = w.name.match(/^search_(\d+)$/);
            if (match) {
              const num = parseInt(match[1]);
              if (w.value && w.value.length > 0) {
                maxVisible = Math.max(maxVisible, num + 1);
              }
            }
          }
        }

        // Cap at 20
        maxVisible = Math.min(maxVisible, 20);
        this._visiblePairs = maxVisible;

        for (const w of this.widgets) {
          const match = w.name.match(/^(search|replace)_(\d+)$/);
          if (match) {
            const num = parseInt(match[2]);
            w.type = num <= maxVisible ? "STRING" : "hidden";
          }
        }

        this.setSize(this.computeSize());
      };
    }
  },
});
