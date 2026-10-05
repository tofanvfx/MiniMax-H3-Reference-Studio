"""
MiniMax H3 ComfyUI Custom Node Suite (Individual Audio Mute Edition)
Each of the 3 audio slots has an independent 'None (Muted)' option.
If you only have 1 audio file (<Audio 1>), Audio 2 and Audio 3 can be set to 'None (Muted)',
and they are completely omitted from the prompt.
"""

import re

class MiniMaxH3AutoDirectorNode:
    """
    1-Click Auto-Director Node with Independent Audio Slots and Mute Controls
    """
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "picture_1_role": ([
                    "Character 1: Woman", 
                    "Character 1: Man", 
                    "Location"
                ],),
                "picture_2_role": ([
                    "Character 2: Man", 
                    "Character 2: Woman", 
                    "Location", 
                    "None"
                ],),
                "picture_3_role": ([
                    "Location", 
                    "Prop: Fountain Pen", 
                    "Prop: Journal / Book", 
                    "None"
                ],),
                "audio_1_slot": ([
                    "Voice: Character 1 (S1)", 
                    "Ambience / Foley", 
                    "Background Music", 
                    "None (Muted)"
                ],),
                "audio_2_slot": ([
                    "None (Muted)", 
                    "Voice: Character 2 (S2)", 
                    "Ambience / Foley", 
                    "Background Music"
                ],),
                "audio_3_slot": ([
                    "None (Muted)", 
                    "Background Music", 
                    "Voice: Character 3 (S3)", 
                    "Ambience / Foley"
                ],),
                "actions_list": ("STRING", {
                    "multiline": True,
                    "default": (
                        "1. Woman sits at the library desk writing notes\n"
                        "2. Young Man enters and leans by her table\n"
                        "3. Woman looks up at him and speaks dialogue\n"
                        "4. Man replies gently to her"
                    )
                }),
                "speaker_1_language": (["Odia", "Hindi", "English", "None"],),
                "speaker_1_line": ("STRING", {"default": "ପ୍ରତ୍ୟେକଟି ଭୁଲିଯାଇଥିବା ପୃଷ୍ଠା ଆଜି ବି ମନେ ରଖିଛି ତା'ର ଲେଖକକୁ।"}),
                "speaker_2_language": (["Hindi", "Odia", "English", "None"],),
                "speaker_2_line": ("STRING", {"default": "कुछ कहानियां हमेशा हमारे साथ चलती हैं।"}),
                "duration_seconds": ("INT", {"default": 12, "min": 4, "max": 15}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("minimax_prompt",)
    FUNCTION = "auto_direct"
    CATEGORY = "MiniMax-H3"

    def auto_direct(self, picture_1_role, picture_2_role, picture_3_role, 
                    audio_1_slot, audio_2_slot, audio_3_slot, 
                    actions_list, speaker_1_language, speaker_1_line, 
                    speaker_2_language, speaker_2_line, duration_seconds=12):
        
        slots = []

        def parse_slot(role_val, pic_num):
            if "Character 1" in role_val:
                gender = "woman" if "Woman" in role_val else "man"
                pronoun = "her" if gender == "woman" else "his"
                return {
                    "type": "char1",
                    "def": f"is the first character in <Picture {pic_num}>, {pronoun} character reference sheet, preserving {pronoun} exact identity, facial features, build, hairstyle, clothing, and overall character design.",
                    "ret": f"the exact identity, facial features, build, hairstyle, and wardrobe of the first character from <Picture {pic_num}> are faithfully maintained."
                }
            elif "Character 2" in role_val:
                gender = "man" if "Man" in role_val else "woman"
                pronoun = "his" if gender == "man" else "her"
                return {
                    "type": "char2",
                    "def": f"is the second character in <Picture {pic_num}>, {pronoun} character reference sheet, preserving {pronoun} exact identity, facial features, build, hairstyle, clothing, and character design.",
                    "ret": f"the exact appearance, build, hairstyle, and wardrobe of the second character from <Picture {pic_num}> are faithfully maintained."
                }
            elif role_val == "Location":
                return {
                    "type": "location",
                    "def": f"is the environment in <Picture {pic_num}>, its location reference, preserving its exact architectural style, interior details, lighting, atmosphere, and spatial layout.",
                    "ret": f"the architectural setting, lighting, and environmental atmosphere from <Picture {pic_num}> are faithfully maintained."
                }
            return None

        # Build image slots
        for idx, role in enumerate([picture_1_role, picture_2_role, picture_3_role], 1):
            if role != "None":
                parsed = parse_slot(role, idx)
                if parsed:
                    slots.append((parsed, f"<Subject {len(slots)+1}>"))

        c1 = next((s for s in slots if s[0]["type"] == "char1"), slots[0])
        c2 = next((s for s in slots if s[0]["type"] == "char2"), None)
        loc = next((s for s in slots if s[0]["type"] == "location"), None)

        # Build active audio slots (filter out None / Muted)
        active_audios = []
        if audio_1_slot != "None (Muted)":
            desc = f"<Audio 1> is the voice-timbre and vocal delivery reference for {c1[1]} (S1)." if "Voice" in audio_1_slot else f"<Audio 1> is the ambience and foley reference."
            active_audios.append((1, audio_1_slot, desc))
        if audio_2_slot != "None (Muted)":
            desc = f"<Audio 2> is the voice-timbre reference for {c2[1]} (S2)." if (c2 and "Voice" in audio_2_slot) else f"<Audio 2> is the acoustic reference for the scene."
            active_audios.append((2, audio_2_slot, desc))
        if audio_3_slot != "None (Muted)":
            desc = f"<Audio 3> is the musical score reference for the background soundtrack."
            active_audios.append((3, audio_3_slot, desc))

        # Parse actions
        raw_lines = actions_list.strip().split("\n")
        actions = [re.sub(r'^\d+[\.\)\-]\s*', '', l).strip() for l in raw_lines if l.strip()]
        if not actions:
            actions = ["Characters interact in scene", "Speaks dialogue"]

        total_shots = len(actions)
        step = duration_seconds / total_shots
        shot_labels = ", ".join([f"[Shot {i+1}]" for i in range(total_shots)])

        # 1. subject_definitions
        prompt = "subject_definitions:\n"
        for s, label in slots:
            prompt += f"{label} {s['def']}\n"
        for _, _, desc in active_audios:
            prompt += f"{desc}\n"
        prompt += "\n"

        # 2. summary
        has_audio = len(active_audios) > 0
        task_header = "[reference generation + audio reference]" if has_audio else "[reference generation]"
        loc_str = f"set in {loc[1]}" if loc else "in the scene"
        char_str = f"featuring {c1[1]} and secondary character {c2[1]}" if c2 else f"following {c1[1]}"
        
        aud_summary = ""
        if len(active_audios) == 1:
            aud_summary = f" with voice matching <Audio {active_audios[0][0]}>"
        elif len(active_audios) > 1:
            aud_summary = f" with references matching {' and '.join([f'<Audio {a[0]}>' for a in active_audios])}"

        prompt += f"summary:\n{task_header} A {duration_seconds}-second cinematic sequence {loc_str}, {char_str} across {total_shots} shots{aud_summary}.\n\n"

        # 3. retention_analysis
        prompt += "retention_analysis:\n"
        for s, label in slots:
            prompt += f"{label} (appears in {shot_labels}): fully_preserved - {s['ret']}\n"
        for num, role, _ in active_audios:
            if "Voice" in role and num == 1:
                prompt += f"<Audio 1>: reference - {c1[1]} matches the vocal timbre, pacing, and delivery of <Audio 1>.\n"
            elif "Voice" in role and num == 2 and c2:
                prompt += f"<Audio 2>: reference - {c2[1]} matches the vocal timbre and delivery of <Audio 2>.\n"
            elif "Music" in role:
                prompt += f"<Audio {num}>: reference - background music adheres to the tempo and instrumentation of <Audio {num}>.\n"
            else:
                prompt += f"<Audio {num}>: reference - ambient acoustic qualities adhere to <Audio {num}>.\n"
        prompt += "\n"

        # 4. detailed_description
        prompt += "detailed_description:\n"
        prompt += "The target video is filmed in a cinematic live-action style with shallow depth of field, warm golden-hour lighting, and an introspective atmosphere.\n"

        shots_output = []
        for i, act in enumerate(actions):
            if i == 0:
                header = f"[Shot 1] A Wide Establishing Shot frames the scene. The camera executes a slow subtle push-in. "
                body = f"Within {loc[1]}, {c1[1]} sits at the desk. " if loc else f"{c1[1]} sits at the desk. "
            elif i == 1 and c2:
                header = f"[Shot 2] At 00:{int(i*step):02d}.000, the shot cuts to a Medium Shot. "
                body = f"{c2[1]} approaches the table. "
            else:
                header = f"[Shot {i+1}] At 00:{int(i*step):02d}.000, the shot cuts to a Medium Shot. "
                body = f"The characters converse around the table. "

            # Dialogues (clean fallback if audio slot is muted)
            if i == 2 and speaker_1_language != "None" and speaker_1_line.strip():
                aud_tag = " matching <Audio 1>'s timbre" if any(a[0] == 1 for a in active_audios) else ""
                body += f" {c1[1]} (S1) speaks with synchronized lip movements{aud_tag}, <d>[{speaker_1_language}] {speaker_1_line.strip()}</d>."
            elif i == total_shots - 1 and c2 and speaker_2_language != "None" and speaker_2_line.strip():
                aud_tag = " matching <Audio 2>'s timbre" if any(a[0] == 2 for a in active_audios) else " in a natural voice"
                body += f" {c2[1]} (S2) replies with synchronized lip movements{aud_tag}, <d>[{speaker_2_language}] {speaker_2_line.strip()}</d>."

            shots_output.append(header + body)

        prompt += "\n".join(shots_output)

        # 5 & 6: Sound & Music
        prompt += (
            f"\n\noverall_soundscape:\n"
            f"Ambient room tone of the library, footsteps on wooden flooring, and tactile paper foley.\n\n"
            f"non_diegetic_music:\n"
            f"A gentle, subtle acoustic piano accompaniment at a slow tempo, complementing the conversation without overpowering the spoken dialogue."
        )

        return (prompt,)


NODE_CLASS_MAPPINGS = {
    "MiniMaxH3AutoDirectorNode": MiniMaxH3AutoDirectorNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "MiniMaxH3AutoDirectorNode": "MiniMax H3 Multi-Character Auto-Director"
}
