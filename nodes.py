"""
MiniMax H3 Reference Studio - ComfyUI Custom Node Suite
Author: tofanvfx
GitHub: https://github.com/tofanvfx/MiniMax-H3-Reference-Studio
"""

import re

class MiniMaxH3AutoDirectorNode:
    """
    1-Click Auto-Director Node for MiniMax H3:
    Converts simple plain-text actions into strictly formatted MiniMax H3 prompts.
    Zero tags required from the user.
    """
    OUTPUT_NODE = True
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "audio_mode": ([
                    "1 Audio File (<Audio 1> Only)",
                    "No Audio References (0)",
                    "2 Audio Files (<Audio 1> & <Audio 2>)",
                    "3 Audio Files (<Audio 1>, <Audio 2>, <Audio 3>)"
                ],),
                "picture_1_role": ([
                    "Character 1: Woman (Ref Sheet)", 
                    "Character 1: Man (Ref Sheet)", 
                    "Location / Environment"
                ],),
                "picture_2_role": ([
                    "Location / Environment", 
                    "Secondary Character: Man", 
                    "Secondary Character: Woman", 
                    "Prop: Fountain Pen", 
                    "Prop: Journal / Book", 
                    "None (Disabled)"
                ],),
                "picture_3_role": ([
                    "None (Disabled)", 
                    "Prop: Fountain Pen", 
                    "Prop: Journal / Book", 
                    "Location / Environment",
                    "Character 3: Elder / Scholar"
                ],),
                "actions_list": ("STRING", {
                    "multiline": True,
                    "default": (
                        "1. Sits on a chair reading a book\n"
                        "2. Starts writing a story in a notebook\n"
                        "3. Close-up of pen nib gliding across the paper\n"
                        "4. Looks up at camera and speaks dialogue"
                    )
                }),
                "speaker_1_language": ([
                    "Odia", "Hindi", "English", "Bengali", "Spanish", "French", "None"
                ],),
                "speaker_1_line": ("STRING", {
                    "default": "ପ୍ରତ୍ୟେକଟି ଭୁଲିଯାଇଥିବା ପୃଷ୍ଠା ଆଜି ବି ମନେ ରଖିଛି ତା'ର ଲେଖକକୁ।"
                }),
                "speaker_2_language": ([
                    "None", "Hindi", "Odia", "English", "Bengali", "Spanish", "French"
                ],),
                "speaker_2_line": ("STRING", {
                    "default": "कुछ कहानियां हमेशा हमारे साथ चलती हैं।"
                }),
                "duration_seconds": ("INT", {"default": 12, "min": 4, "max": 15}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("minimax_prompt",)
    FUNCTION = "auto_direct"
    CATEGORY = "MiniMax-H3"

    def auto_direct(self, audio_mode, picture_1_role, picture_2_role, 
                    picture_3_role, actions_list, speaker_1_language, 
                    speaker_1_line, speaker_2_language, speaker_2_line, 
                    duration_seconds=12):
        
        slots = []

        def parse_role(role_val, pic_num):
            if "Character 1" in role_val:
                gender = "woman" if "Woman" in role_val else "man"
                pronoun = "her" if gender == "woman" else "his"
                return {
                    "type": "char1",
                    "def": f"is the first character in <Picture {pic_num}>, {pronoun} character reference sheet, preserving {pronoun} exact identity, facial features, build, hairstyle, clothing, and overall character design.",
                    "ret": f"the exact identity, facial features, build, hairstyle, and wardrobe of the first character from <Picture {pic_num}> are faithfully maintained."
                }
            elif "Secondary Character" in role_val:
                gender = "man" if "Man" in role_val else "woman"
                pronoun = "his" if gender == "man" else "her"
                return {
                    "type": "char2",
                    "def": f"is the secondary character in <Picture {pic_num}>, {pronoun} character reference sheet, preserving {pronoun} exact identity, facial features, build, hairstyle, clothing, and character design.",
                    "ret": f"the exact appearance, build, hairstyle, and wardrobe of the secondary character from <Picture {pic_num}> are faithfully maintained."
                }
            elif "Location" in role_val:
                return {
                    "type": "location",
                    "def": f"is the environment in <Picture {pic_num}>, its location reference, preserving its exact architectural style, interior details, lighting, atmosphere, and spatial layout.",
                    "ret": f"the architectural setting, lighting, and environmental atmosphere from <Picture {pic_num}> are faithfully maintained."
                }
            elif "Prop: Fountain Pen" in role_val:
                return {
                    "type": "prop",
                    "keyword": "pen",
                    "def": f"is the fountain pen in <Picture {pic_num}>, its prop reference, preserving its exact metallic casing, nib craftsmanship, finish, and physical design.",
                    "ret": f"the physical design and finish of the fountain pen from <Picture {pic_num}> are fully preserved."
                }
            elif "Prop: Journal" in role_val:
                return {
                    "type": "prop",
                    "keyword": "journal",
                    "def": f"is the leather-bound notebook in <Picture {pic_num}>, its prop reference, preserving its exact cover texture, binding, paper tone, and dimensions.",
                    "ret": f"the texture and design of the journal from <Picture {pic_num}> are fully preserved."
                }
            elif "Character 3" in role_val:
                return {
                    "type": "char3",
                    "def": f"is the third character in <Picture {pic_num}>, their character reference sheet, preserving their exact identity, facial features, build, hairstyle, clothing, and character design.",
                    "ret": f"the appearance and character design of the third character from <Picture {pic_num}> are faithfully maintained."
                }
            return None

        # Build image slots
        for idx, role in enumerate([picture_1_role, picture_2_role, picture_3_role], 1):
            if role != "None (Disabled)":
                parsed = parse_role(role, idx)
                if parsed:
                    slots.append((parsed, f"<Subject {len(slots)+1}>"))

        c1 = next((s for s in slots if s[0]["type"] == "char1"), slots[0])
        c2 = next((s for s in slots if s[0]["type"] == "char2"), None)
        c3 = next((s for s in slots if s[0]["type"] == "char3"), None)
        loc = next((s for s in slots if s[0]["type"] == "location"), None)
        props = [s for s in slots if s[0]["type"] == "prop"]

        # Parse actions
        raw_lines = actions_list.strip().split("\n")
        actions = [re.sub(r'^\d+[\.\)\-]\s*', '', l).strip() for l in raw_lines if l.strip()]
        if not actions:
            actions = ["Sits quietly reading", "Writes in notebook", "Speaks dialogue"]

        total_shots = len(actions)
        step = duration_seconds / total_shots
        shot_labels = ", ".join([f"[Shot {i+1}]" for i in range(total_shots)])

        # 1. subject_definitions
        prompt = "subject_definitions:\n"
        for s, label in slots:
            prompt += f"{label} {s['def']}\n"

        # Strictly add ONLY the selected number of audios!
        has_audio = audio_mode != "No Audio References (0)"
        if audio_mode == "1 Audio File (<Audio 1> Only)":
            prompt += f"<Audio 1> is the voice-timbre and vocal delivery reference for {c1[1]} (S1), providing an authentic, warm, and articulate vocal timbre with natural pacing.\n"
        elif audio_mode == "2 Audio Files (<Audio 1> & <Audio 2>)":
            prompt += f"<Audio 1> is the voice-timbre and vocal delivery reference for {c1[1]} (S1).\n"
            if c2:
                prompt += f"<Audio 2> is the voice-timbre and vocal delivery reference for {c2[1]} (S2).\n"
            else:
                prompt += f"<Audio 2> is the ambience and tactile foley reference for the scene.\n"
        elif audio_mode == "3 Audio Files (<Audio 1>, <Audio 2>, <Audio 3>)":
            prompt += f"<Audio 1> is the voice-timbre and vocal delivery reference for {c1[1]} (S1).\n"
            if c2:
                prompt += f"<Audio 2> is the voice-timbre reference for {c2[1]} (S2).\n"
            else:
                prompt += f"<Audio 2> is the ambience and foley reference for the scene.\n"
            if c3:
                prompt += f"<Audio 3> is the voice-timbre reference for {c3[1]} (S3).\n"
            else:
                prompt += f"<Audio 3> is the musical score reference for the background soundtrack.\n"
        prompt += "\n"

        # 2. summary
        task_header = "[reference generation + audio reference]" if has_audio else "[reference generation]"
        loc_str = f"set in {loc[1]}" if loc else "in the scene"
        char_str = f"featuring {c1[1]} and secondary character {c2[1]}" if c2 else f"following {c1[1]}"
        
        aud_summary = ""
        if audio_mode == "1 Audio File (<Audio 1> Only)":
            aud_summary = f" with voice matching <Audio 1>"
        elif audio_mode == "2 Audio Files (<Audio 1> & <Audio 2>)":
            aud_summary = f" with references matching <Audio 1> and <Audio 2>"
        elif audio_mode == "3 Audio Files (<Audio 1>, <Audio 2>, <Audio 3>)":
            aud_summary = f" with 3 audio references matching <Audio 1>, <Audio 2>, and <Audio 3>"

        prompt += f"summary:\n{task_header} A {duration_seconds}-second cinematic sequence {loc_str}, {char_str} across {total_shots} shots{aud_summary}.\n\n"

        # 3. retention_analysis
        prompt += "retention_analysis:\n"
        for s, label in slots:
            prompt += f"{label} (appears in {shot_labels}): fully_preserved - {s['ret']}\n"

        if audio_mode == "1 Audio File (<Audio 1> Only)":
            prompt += f"<Audio 1>: reference - {c1[1]} matches the vocal timbre, pacing, and delivery of <Audio 1>.\n"
        elif audio_mode == "2 Audio Files (<Audio 1> & <Audio 2>)":
            prompt += f"<Audio 1>: reference - {c1[1]} matches the vocal timbre and delivery of <Audio 1>.\n"
            prompt += f"<Audio 2>: reference - secondary audio reference adheres to <Audio 2>.\n"
        elif audio_mode == "3 Audio Files (<Audio 1>, <Audio 2>, <Audio 3>)":
            prompt += f"<Audio 1>: reference - {c1[1]} matches the vocal timbre of <Audio 1>.\n"
            prompt += f"<Audio 2>: reference - secondary audio reference adheres to <Audio 2>.\n"
            prompt += f"<Audio 3>: reference - tertiary audio reference adheres to <Audio 3>.\n"
        prompt += "\n"

        # 4. detailed_description
        prompt += "detailed_description:\n"
        prompt += "The target video is filmed in a cinematic live-action style with shallow depth of field, warm golden-hour lighting, and an introspective atmosphere.\n"

        shots_output = []
        for i, act in enumerate(actions):
            lower_act = act.lower()
            
            # Detect framing & movement
            if any(k in lower_act for k in ["close", "pen", "hand", "paper", "macro"]):
                size = "Macro Close-Up"
                camera = "static lock-off focus"
            elif any(k in lower_act for k in ["speak", "dialogue", "face", "look at camera", "looks up"]):
                size = "Low-Angle Medium Close-Up"
                camera = "slow tilt up toward the face"
            elif i == 0 or any(k in lower_act for k in ["enter", "room", "sitting", "wide"]):
                size = "Wide Establishing Shot"
                camera = "slow subtle push-in"
            elif any(k in lower_act for k in ["walk", "shelf", "approach"]):
                size = "Medium Tracking Shot"
                camera = "smooth lateral tracking motion"
            else:
                size = "Medium Shot"
                camera = "subtle lateral drift to the right"

            if i == 0:
                header = f"[Shot 1] A {size} frames the scene. The camera executes a {camera}. "
            else:
                secs = i * step
                mins = int(secs // 60)
                rem_secs = secs % 60
                time_str = f"{mins:02d}:{rem_secs:06.3f}"
                header = f"[Shot {i+1}] At {time_str}, the shot cuts to a {size}. The camera executes a {camera}. "

            # Match prop if mentioned
            matched_prop = next((p for p in props if p[0].get("keyword", "") in lower_act), None)

            mentions_c2 = any(w in lower_act for w in ["man", "secondary", "approaches", "replies"])
            target = c2[1] if (mentions_c2 and c2) else c1[1]

            if size == "Macro Close-Up":
                if matched_prop:
                    body = f"The shot focuses sharply on {matched_prop[1]} as {act}."
                else:
                    body = f"{act}."
            elif i == 0 and loc:
                body = f"Within {loc[1]}, {target} {act[:1].lower() + act[1:]}."
            else:
                body = f"{target} {act[:1].lower() + act[1:]}."

            # Speaker 1 dialogue
            if (i == total_shots - 1 or any(k in lower_act for k in ["speak", "dialogue"])) and speaker_1_language != "None" and speaker_1_line.strip():
                aud_tag = " matching <Audio 1>'s timbre" if has_audio else " in a natural, clear voice"
                body += f" {c1[1]} (S1) speaks with synchronized lip movement{aud_tag}, <d>[{speaker_1_language}] {speaker_1_line.strip()}</d>."

            # Speaker 2 dialogue (if active)
            if mentions_c2 and c2 and speaker_2_language != "None" and speaker_2_line.strip():
                aud_tag = " matching <Audio 2>'s timbre" if "2 Audio" in audio_mode or "3 Audio" in audio_mode else " in a natural, clear voice"
                body += f" {c2[1]} (S2) replies with synchronized lip movement{aud_tag}, <d>[{speaker_2_language}] {speaker_2_line.strip()}</d>."

            shots_output.append(header + body)

        prompt += "\n".join(shots_output)

        # 5. Soundscape & 6. Music
        prompt += (
            f"\n\noverall_soundscape:\n"
            f"Ambient room tone of the environment, realistic footsteps on wooden flooring, and tactile paper foley.\n\n"
            f"non_diegetic_music:\n"
            f"A gentle, subtle acoustic piano accompaniment at a slow tempo, complementing the mood without overpowering dialogue."
        )

        return {"ui": {"text": [prompt]}, "result": (prompt,)}


class MiniMaxH3ShotNode:
    """
    Manual Shot Builder Node for modular shot-by-shot workflows.
    """
    OUTPUT_NODE = True
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "shot_number": ("INT", {"default": 1, "min": 1, "max": 20, "step": 1}),
                "cut_timestamp": ("STRING", {"default": "00:03.500"}),
                "shot_size": ([
                    "Wide Shot", "Extreme Wide Shot", "Medium Wide Shot",
                    "Medium Shot", "Medium Close-Up", "Close-Up", "Macro Close-Up",
                    "Low-Angle Medium Close-Up", "High-Angle Overview"
                ],),
                "camera_movement": ([
                    "slow subtle push-in", "slow pull-out",
                    "subtle lateral drift to the right", "subtle lateral drift to the left",
                    "smooth tracking shot", "slow tilt up toward her face",
                    "static lock-off focus"
                ],),
                "action_description": ("STRING", {"multiline": True, "default": "<Subject 1> interacts with the environment."}),
                "dialogue_language": (["None", "Odia", "Hindi", "English", "Bengali", "Spanish"],),
                "dialogue_text": ("STRING", {"default": ""}),
            },
            "optional": {
                "previous_shots": ("STRING", {"forceInput": True}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("shot_chain",)
    FUNCTION = "build_shot"
    CATEGORY = "MiniMax-H3"

    def build_shot(self, shot_number, cut_timestamp, shot_size, camera_movement, 
                   action_description, dialogue_language, dialogue_text, previous_shots=""):
        if shot_number == 1:
            shot_str = f"[Shot 1] A {shot_size} frames the scene. The camera executes a {camera_movement}. {action_description.strip()}"
        else:
            shot_str = f"[Shot {shot_number}] At {cut_timestamp}, the shot cuts to a {shot_size}. The camera executes a {camera_movement}. {action_description.strip()}"

        if dialogue_language != "None" and dialogue_text.strip():
            shot_str += f" <Subject 1> (S1) speaks with synchronized lip movement, <d>[{dialogue_language}] {dialogue_text.strip()}</d>."

        final_result = f"{previous_shots.strip()}\n{shot_str}" if (previous_shots and previous_shots.strip()) else shot_str
        return {"ui": {"text": [final_result]}, "result": (final_result,)}


NODE_CLASS_MAPPINGS = {
    "MiniMaxH3AutoDirectorNode": MiniMaxH3AutoDirectorNode,
    "MiniMaxH3ShotNode": MiniMaxH3ShotNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "MiniMaxH3AutoDirectorNode": "MiniMax H3 1-Click Auto-Director",
    "MiniMaxH3ShotNode": "MiniMax H3 Shot Builder"
}
