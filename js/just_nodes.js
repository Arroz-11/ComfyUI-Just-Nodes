import { app } from "../../scripts/app.js";

app.registerExtension({
  name: "just_nodes",

  beforeRegisterNodeDef(nodeType, nodeData) {
    // --- Picker: dynamic input slots + refresh button ---
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

        this.setSize(this.computeSize());
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
    }
  },
});
