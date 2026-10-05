# MiniMax H3 Reference Studio for ComfyUI 🎬

An intelligent **ComfyUI Custom Node Suite** for generating strictly compliant multimodal prompts for the **MiniMax Hailuo H3** video generation model (T2VA, I2VA, and Ref2VA).

Zero manual tags required. Write simple, everyday action bullet points, and the **Auto-Director** automatically determines cinematic framing, camera motion, cut timestamps, character reference bindings, audio references, and lip-sync dialogue formatting.

---

## ✨ Features

- **⚡ 1-Click Auto-Director**: Takes simple plain-text action sentences and automatically detects:
  - **Framing**: Wide Shot, Medium Shot, Macro Close-Up, Low-Angle, etc.
  - **Camera Motion**: Slow push-in, lateral drift, tracking shot, static focus.
  - **Timing**: Computes exact cut timestamps (`00:03.000`, `00:06.000`, etc.).
- **🎭 Character Reference Sheet Support**:
  - Automatically formats `<Subject 1>` as a character reference sheet from `<Picture 1>` without manual descriptions.
  - Supports Main Character + Secondary Character interactions.
- **🎙️ Flexible Audio Reference Engine (0 to 3 Audios)**:
  - **1 Audio File**: Binds `<Audio 1>` for voice timbre; completely omits unused audio references.
  - **No Audio**: Generates clean reference prompts without `<Audio>` tags.
  - **2-3 Audios**: Supports individual character voices (S1, S2, S3), foley/ambience, or background music.
- **🗣️ Synchronized Multilingual Dialogue**:
  - Auto-formats speech into `<d>[Language] ...</d>` with native lip-sync tags (Odia, Hindi, English, Spanish, Bengali, French, etc.).
- **📦 Zero External Dependencies**: Runs entirely on Python standard library without heavy dependencies.

---

## 🚀 Installation

### Option 1: Git Clone into ComfyUI
Open a terminal in your `ComfyUI/custom_nodes` directory and clone this repository:

```bash
cd ComfyUI/custom_nodes
git clone https://github.com/tofanvfx/MiniMax-H3-Reference-Studio.git
```

Restart ComfyUI, and the nodes will be available under the **`MiniMax-H3`** category!

### Option 2: ComfyUI Manager
Search for `MiniMax H3 Reference Studio` in the ComfyUI Manager and click Install.

---

## 🛠️ Included Nodes

### 1. `MiniMax H3 1-Click Auto-Director`
The all-in-one node for high-speed prompt generation.

| Input | Description |
| :--- | :--- |
| **`audio_mode`** | Choose between `1 Audio File`, `No Audio`, `2 Audio Files`, or `3 Audio Files`. |
| **`picture_1_role`** | Character 1 (Woman / Man) or Location. |
| **`picture_2_role`** | Location, Secondary Character, Props (Pen, Journal), or Disabled. |
| **`picture_3_role`** | Location, Props, Character 3, or Disabled. |
| **`actions_list`** | Plain-text action sentences (one per line). |
| **`speaker_1_language`** | Spoken language for Speaker 1 (`Odia`, `Hindi`, `English`, etc.). |
| **`speaker_1_line`** | Dialogue words for Speaker 1 (no tags needed). |
| **`speaker_2_language`** | Spoken language for Speaker 2 (if present). |
| **`speaker_2_line`** | Dialogue words for Speaker 2. |
| **`duration_seconds`** | Video length (4 to 15 seconds). |

**Output**:
- `minimax_prompt`: A formatted 6-section Ref2VA / T2VA prompt ready to pass to API caller nodes or clipboard.

---

### 2. `MiniMax H3 Shot Builder`
Modular node for users who want granular, shot-by-shot control. Chain multiple shot nodes together into a final prompt sequence.

---

## 📝 Example Output

```text
subject_definitions:
<Subject 1> is the first character in <Picture 1>, her character reference sheet, preserving her exact identity, facial features, build, hairstyle, clothing, and overall character design.
<Subject 2> is the environment in <Picture 2>, its location reference, preserving its exact architectural style, interior details, lighting, atmosphere, and spatial layout.
<Audio 1> is the voice-timbre and vocal delivery reference for <Subject 1> (S1), providing an authentic, warm, and articulate vocal timbre with natural pacing.

summary:
[reference generation + audio reference] A 12-second cinematic sequence set in <Subject 2>, following <Subject 1> across 4 shots with voice matching <Audio 1>.

retention_analysis:
<Subject 1> (appears in [Shot 1], [Shot 2], [Shot 3], [Shot 4]): fully_preserved - the exact identity, facial features, build, hairstyle, and wardrobe of the first character from <Picture 1> are faithfully maintained.
<Subject 2> (appears in [Shot 1], [Shot 2], [Shot 3], [Shot 4]): fully_preserved - the architectural setting, lighting, and environmental atmosphere from <Picture 2> are faithfully maintained.
<Audio 1>: reference - <Subject 1> matches the vocal timbre, pacing, and delivery of <Audio 1>.

detailed_description:
The target video is filmed in a cinematic live-action style with shallow depth of field, warm golden-hour lighting, and an introspective atmosphere.
[Shot 1] A Wide Establishing Shot frames the scene. The camera executes a slow subtle push-in. Within <Subject 2>, <Subject 1> sits on a chair reading a book.
[Shot 2] At 00:03.000, the shot cuts to a Medium Shot. The camera executes a subtle lateral drift to the right. <Subject 1> starts writing a story in a notebook.
[Shot 3] At 00:06.000, the shot cuts to a Macro Close-Up. The camera executes a static lock-off focus. The pen nib glides across the paper.
[Shot 4] At 00:09.000, the shot cuts to a Low-Angle Medium Close-Up. The camera executes a slow tilt up toward the face. <Subject 1> looks up at camera and speaks dialogue. <Subject 1> (S1) speaks with synchronized lip movement matching <Audio 1>'s timbre, <d>[Odia] ପ୍ରତ୍ୟେକଟି ଭୁଲିଯାଇଥିବା ପୃଷ୍ଠା ଆଜି ବି ମନେ ରଖିଛି ତା'ର ଲେଖକକୁ।</d>.

overall_soundscape:
Ambient room tone of the environment, realistic footsteps on wooden flooring, and tactile paper foley.

non_diegetic_music:
A gentle, subtle acoustic piano accompaniment at a slow tempo, complementing the mood without overpowering dialogue.
```

---

## 📄 License
This project is licensed under the [MIT License](LICENSE).

Created by [@tofanvfx](https://github.com/tofanvfx).
