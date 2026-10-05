import { app } from "../../scripts/app.js";
import { ComfyWidgets } from "../../scripts/widgets.js";

app.registerExtension({
    name: "MiniMax.H3.ReferenceStudio",
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name === "MiniMaxH3AutoDirectorNode" || nodeData.name === "MiniMaxH3ShotNode") {
            const onNodeCreated = nodeType.prototype.onNodeCreated;
            nodeType.prototype.onNodeCreated = function () {
                const r = onNodeCreated ? onNodeCreated.apply(this, arguments) : undefined;

                // 1. Add "Copy Prompt" button directly onto the node
                const copyBtn = this.addWidget("button", "📋 Copy Generated Prompt", null, () => {
                    const w = this.widgets?.find(x => x.name === "generated_prompt");
                    if (w && w.value && w.value.trim() !== "") {
                        navigator.clipboard.writeText(w.value);
                        const prevName = copyBtn.name;
                        copyBtn.name = "✓ Copied to Clipboard!";
                        this.setDirtyCanvas(true, true);
                        setTimeout(() => {
                            copyBtn.name = prevName;
                            this.setDirtyCanvas(true, true);
                        }, 2000);
                    } else {
                        alert("Please click 'Queue Prompt' (or Ctrl+Enter) first to generate the prompt text!");
                    }
                });

                // 2. Add multiline display widget directly inside the node
                const displayWidget = ComfyWidgets["STRING"](
                    this, 
                    "generated_prompt", 
                    ["STRING", { multiline: true }], 
                    app
                ).widget;

                if (displayWidget && displayWidget.inputEl) {
                    displayWidget.inputEl.readOnly = true;
                    displayWidget.inputEl.placeholder = "Click 'Queue Prompt' to generate and see full prompt here...";
                    displayWidget.inputEl.style.fontSize = "11px";
                    displayWidget.inputEl.style.height = "160px";
                    displayWidget.inputEl.style.fontFamily = "monospace";
                    displayWidget.inputEl.style.backgroundColor = "rgba(0, 0, 0, 0.35)";
                    displayWidget.inputEl.style.color = "#a7f3d0";
                    displayWidget.inputEl.style.border = "1px solid rgba(52, 211, 153, 0.3)";
                }

                // Expand node size so full text and button fit comfortably
                const currentWidth = this.size[0] || 380;
                const currentHeight = this.size[1] || 450;
                this.setSize([Math.max(currentWidth, 420), currentHeight + 200]);

                return r;
            };

            // When ComfyUI executes the node, populate the display widget automatically!
            const onExecuted = nodeType.prototype.onExecuted;
            nodeType.prototype.onExecuted = function (message) {
                onExecuted?.apply(this, arguments);
                if (message?.text) {
                    const w = this.widgets?.find(x => x.name === "generated_prompt");
                    if (w) {
                        w.value = Array.isArray(message.text) ? message.text.join("\n") : message.text;
                    }
                    this.setDirtyCanvas(true, true);
                }
            };
        }
    }
});
