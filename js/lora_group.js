import { app } from "../../scripts/app.js";
import { api } from "../../scripts/api.js";

const NONE = "— Select LoRA —";
const COLORS = { Red: "#d65a5a", Orange: "#e38a3c", Yellow: "#dcc143", Green: "#4fb368", Teal: "#3db6b6", Blue: "#5b8ce3", Purple: "#9d6ddb", Pink: "#e272b3", Grey: "#a0a0a0" };

function noteHeader(node, name, fallback, read, write) {
  const update = (values) => {
    node.jnChange(() => write(values));
  };
  const widget = {
    name, type: "custom", jnGroup: true, serialize: false,
    options: { serialize: false },
    computeSize: (width) => [width, 24],
    draw(ctx, host, width, y) {
      const { note, color } = read();
      const text = note || fallback;
      ctx.save();
      ctx.fillStyle = color ? `${color}40` : LiteGraph.WIDGET_BGCOLOR;
      ctx.fillRect(12, y, width - 24, 24);
      if (color) {
        ctx.fillStyle = color;
        ctx.fillRect(12, y, 4, 24);
      }
      ctx.fillStyle = LiteGraph.WIDGET_TEXT_COLOR;
      ctx.font = `12px ${LiteGraph.NODE_FONT || "sans-serif"}`;
      ctx.textBaseline = "middle";
      let fitted = text;
      if (ctx.measureText(text).width > width - 48) {
        let low = 0;
        let high = text.length;
        while (low < high) {
          const middle = Math.ceil((low + high) / 2);
          if (ctx.measureText(`${text.slice(0, middle)}…`).width <= width - 48) low = middle;
          else high = middle - 1;
        }
        fitted = `${text.slice(0, low)}…`;
      }
      ctx.fillText(fitted, 24, y + 12);
      ctx.restore();
    },
    mouse(event) {
      if (!["pointerdown", "mousedown"].includes(event.type)) return false;
      new LiteGraph.ContextMenu([
        { content: "Rename note", callback: async () => {
          const value = await app.extensionManager.dialog.prompt({ title: fallback, message: "Note", defaultValue: read().note || "" });
          if (value != null) update({ note: String(value) });
        } },
        { content: "Clear note", callback: () => update({ note: "" }) },
        null,
        ...Object.entries(COLORS).map(([label, color]) => ({ content: label, callback: () => update({ color }) })),
        { content: "Default color", callback: () => update({ color: null }) },
      ], { event, title: fallback });
      return true;
    },
  };
  node.addCustomWidget(widget);
  return widget;
}

app.registerExtension({
  name: "JustNodes.LoRAGroup",
  async beforeRegisterNodeDef(nodeType, nodeData) {
    if (nodeData.name !== "LoraGroupModelOnly_JN") return;
    const created = nodeType.prototype.onNodeCreated;
    nodeType.prototype.onNodeCreated = function () {
      created?.apply(this, arguments);
      const node = this;
      const data = this.widgets.find((w) => w.name === "loras");
      data.type = "jn_lora_data";
      data.computeSize = () => [0, -4];
      data.draw = () => {};
      data.serializeValue = () => JSON.stringify(node.properties.lora_rows.map(({ lora, weight }) => ({ lora, weight })));
      this.properties.group_note ??= "";
      this.properties.lora_rows ??= [{ note: "", lora: "", weight: 1 }];
      this.jnLoraFiles = [];
      this.jnRefreshGeneration = 0;
      this.jnChange = function (change) {
        const tracker = app.extensionManager.workflow.activeWorkflow?.changeTracker;
        tracker?.captureCanvasState();
        tracker?.beforeChange();
        try {
          change();
        } finally {
          tracker?.afterChange();
        }
        this.setDirtyCanvas(true, true);
      };
      this.jnRebuild = function () {
        for (const widget of this.widgets.filter((w) => w.jnGroup)) widget.onRemove?.();
        this.widgets = this.widgets.filter((w) => !w.jnGroup);
        const add = (type, name, value, callback, options = {}) => {
          const widget = this.addWidget(type, name, value, callback, options);
          widget.value = value;
          widget.callback = callback;
          widget.jnGroup = true;
          widget.serialize = false;
          widget.options = { ...widget.options, ...options, serialize: false };
          return widget;
        };
        noteHeader(this, "Group note", "Group note · click to edit", () => ({ note: this.properties.group_note, color: this.properties.group_color }), ({ note, color }) => {
          if (note !== undefined) this.properties.group_note = note;
          if (color !== undefined) this.properties.group_color = color;
        });
        this.properties.lora_rows.forEach((row, index) => {
          const number = index + 1;
          noteHeader(this, `Note ${number}`, `LoRA ${number} · click to add note`, () => row, (values) => Object.assign(row, values));
          const missing = row.lora && !this.jnLoraFiles.includes(row.lora);
          const combo = add("combo", `LoRA ${number}`, row.lora || NONE, (value) => {
            this.jnChange(() => { row.lora = value === NONE ? "" : value; });
            combo.label = row.lora && !this.jnLoraFiles.includes(row.lora) ? `LoRA ${number} · missing` : `LoRA ${number}`;
          }, {
            values: [NONE, ...this.jnLoraFiles, ...(missing ? [row.lora] : [])],
          });
          combo.label = missing ? `LoRA ${number} · missing` : `LoRA ${number}`;
          add("number", `Weight ${number}`, row.weight, (value) => {
            this.jnChange(() => { row.weight = value; });
          }, { min: -100, max: 100, step: 0.1, precision: 2 });
          add("button", `Remove LoRA ${number}`, null, () => {
            this.jnChange(() => {
              this.properties.lora_rows.splice(index, 1);
              this.jnRebuild();
            });
          });
        });
        add("button", this.properties.lora_rows.length < 12 ? "+ Add LoRA" : "12 / 12 LoRAs", null, () => {
          if (this.properties.lora_rows.length >= 12) return;
          this.jnChange(() => {
            this.properties.lora_rows.push({ note: "", lora: "", weight: 1 });
            this.jnRebuild();
          });
        });
        const refresh = add("button", "Refresh LoRA list", null, async () => {
          refresh.label = "Refreshing…";
          this.setDirtyCanvas(true, true);
          await this.jnRefresh();
        });
        refresh.label = "Refresh LoRA list";
        this.size = [Math.max(this.size[0], 300), this.computeSize()[1]];
        this.setDirtyCanvas(true, true);
      };
      this.jnRefresh = async function () {
        const generation = ++this.jnRefreshGeneration;
        try {
          const response = await api.fetchApi("/just_nodes/lora_list");
          if (!response.ok) throw new Error(`HTTP ${response.status}`);
          const result = await response.json();
          if (generation !== this.jnRefreshGeneration) return;
          if (!Array.isArray(result.loras) || !result.loras.every((name) => typeof name === "string")) throw new Error("Invalid LoRA list response");
          this.jnLoraFiles = result.loras;
          this.jnRebuild();
        } catch (error) {
          if (generation !== this.jnRefreshGeneration) return;
          const button = this.widgets.find((w) => w.jnGroup && w.type === "button" && /Refresh/.test(w.name));
          if (button) button.label = "Refresh failed · click to retry";
          this.setDirtyCanvas(true, true);
          console.error("[Just Nodes] Could not refresh LoRA list:", error);
        }
      };
      this.jnRebuild();
      this.jnRefresh();
    };
    const configured = nodeType.prototype.onConfigure;
    nodeType.prototype.onConfigure = function () {
      configured?.apply(this, arguments);
      this.jnRebuild?.();
    };
  },
});
