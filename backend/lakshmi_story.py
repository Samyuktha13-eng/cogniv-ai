def _scene(
    scene_id,
    title,
    period,
    scene_type,
    image,
    prompt,
    question=None,
    options=None,
    next_scene=None,
    reference_bundle=None,
    action=None,
    characters=None,
    environment=None,
    objects=None,
    story=None,
    reference_image_direct=False,
    reference_images=None,
    character_reference_images=None,
):
    return {
        "id": scene_id,
        "title": title,
        "period": period,
        "scene_type": scene_type,
        "image": image,
        "prompt": prompt.strip(),
        "question": question,
        "options": options or [],
        "next_scene": next_scene,
        "reference_bundle": reference_bundle or [],
        "action": action,
        "characters": characters or [],
        "environment": environment,
        "objects": objects or [],
        "story": story,
        "reference_image_direct": reference_image_direct,
        "reference_images": reference_images or [],
        "character_reference_images": character_reference_images or [],
    }


def build_lakshmi_memory_journey():
    scenes = [
        _scene(
            scene_id="intro",
            title="Lakshmi's Memories",
            period="present",
            scene_type="intro",
            image="home/family_house_front.png",
            prompt="""
Create a cinematic establishing shot of the exact family house shown in the supplied reference image.
Preserve the house architecture exactly: roof, walls, doors, windows, veranda, plants, compound, surrounding environment and overall appearance. Do not redesign the house.
Start with a quiet exterior view of the house. Slowly move the camera forward toward the entrance with a gentle realistic cinematic motion.
There are NO PEOPLE in this shot.
The house should feel like Lakshmi's longtime family home in India. Warm natural daylight, realistic Indian residential environment, emotionally nostalgic but natural.
No character generation. No people entering the frame. No scene transition. No sudden camera movement.
Maintain a consistent 16:9 landscape composition throughout.
""".strip(),
            question=None,
            options=[],
            next_scene="memory_01_anu",
            reference_bundle=[
                {"type": "environment", "path": "home/family_house_front.png"},
            ],
            action="intro",
            characters=[],
            environment="home/family_house_front.png",
            story="The camera slowly moves toward Lakshmi's familiar home while the entire house remains visible.",
        ),
        _scene(
            scene_id="memory_01_anu",
            title="Who is Anu?",
            period="past",
            scene_type="recall_question",
            image="home/living_room.jpg",
            prompt="""
Animate the supplied living-room reference image as a realistic cinematic scene.
The elderly woman shown in the supplied Lakshmi reference is Lakshmi. Preserve her exact identity, elderly age, face, skin tone, hairstyle, saree, jewelry and overall appearance.
Lakshmi is sitting naturally in the living room near the family photographs.
She quietly looks toward the photographs, slowly turns her head slightly toward them, blinks naturally and breathes gently.
Preserve the exact living-room environment from the supplied reference image, including furniture, walls, windows, doors and family photographs.
Do not replace Lakshmi with another woman. Do not make her younger. Do not change her clothing or appearance.
No additional people.
Use subtle realistic movement only. Stable cinematic camera. No cuts or transitions.
16:9 landscape.
""".strip(),
            question="Who is this person with Lakshmi?",
            options=[
                {"id": "anu", "label": "Anu", "correct": True, "action": "positive_recall"},
                {"id": "rahul", "label": "Rahul", "correct": False, "action": "memory_cue"},
            ],
            next_scene="memory_02_chapathi",
            reference_bundle=[
                {"type": "character", "path": "people/patient_lakshmi.png"},
                {"type": "character", "path": "people/daughter_anu.png"},
                {"type": "environment", "path": "home/living_room.jpg"},
            ],
            action="positive_recall",
            characters=["people/patient_lakshmi.png", "people/daughter_anu.png"],
            environment="home/living_room.jpg",
            story="Lakshmi remembers her daughter Anu.",
        ),
        _scene(
            scene_id="memory_02_chapathi",
            title="Chapathi Memory",
            period="past",
            scene_type="recall_question",
            image="memories/anu_cooking_with_lakshmi.jpg",
            prompt="""
Create a nostalgic memory reconstruction of Lakshmi and her daughter Anu
preparing chapathi together in Lakshmi's family kitchen.
Use the supplied cooking memory image as the primary visual reference.
Create a realistic, warm nostalgic memory inside the exact same kitchen shown in the reference image.
Preserve the recognizable identities, faces, ages, skin tones, hairstyles, sarees, jewelry and overall appearances of elderly Lakshmi and her adult daughter Anu exactly as supplied.
Keep Lakshmi on the left beside the gas stove and tawa, and Anu on the right beside the rolling board.
Keep the metal dish rack and utensils, tiled wall, window, gas stove and cooking counter unchanged.
Only show body portions supported by the supplied image; keep the counter and stove covering unsupported lower-body areas. Do not generate, reconstruct or hallucinate legs, feet or clothing below the visible reference areas.
Lakshmi gently cooks chapathi on the tawa with a spatula and looks toward Anu with a warm motherly smile.
Anu gently rolls dough on the wooden rolling board and smiles naturally toward Lakshmi.
Use subtle hand, arm, eye, facial and breathing motion only. No exaggerated gestures, sudden movements, dancing or theatrical acting.
Keep the camera stable with a slight gentle push-in. Do not change the kitchen layout or location.
No face morphing, age changes, character replacement, extra people, furniture, architecture, text, captions, logos or watermarks.
Maintain a consistent 16:9 landscape composition for a short 5-8 second clip.
""".strip(),
            question="What were Lakshmi and Anu making together?",
            options=[
                {"id": "chapathi", "label": "Chapathi", "correct": True, "action": "positive_recall"},
                {"id": "rice", "label": "Rice", "correct": False, "action": "memory_cue"},
                {"id": "banana", "label": "Banana", "correct": False, "action": "memory_cue"},
            ],
            next_scene="memory_03_temple",
            reference_bundle=[
                {"type": "character", "path": "people/patient_lakshmi.png"},
                {"type": "character", "path": "people/daughter_anu.png"},
                {"type": "environment", "path": "home/family_kitchen.jpg"},
                {"type": "food", "path": "food/chapathi.jpg"},
            ],
            action="positive_recall",
            characters=["people/patient_lakshmi.png", "people/daughter_anu.png"],
            environment="home/family_kitchen.jpg",
            objects=["food/chapathi.jpg"],
            story="Lakshmi remembers making chapathi with Anu.",
            reference_image_direct=True,
        ),
        _scene(
            scene_id="memory_03_temple",
            title="Temple Visit",
            period="past",
            scene_type="recall_question",
            image="memories/anu_lakshmi_temple.jpg",
            prompt="""
Create a warm, realistic nostalgic childhood memory of Lakshmi and her young daughter Anu visiting their favorite Indian temple together.
Use the supplied interior temple reference as the primary reference for the Krishna shrine, carved stone pillars, brass lamps, flowers and devotional atmosphere.
Use the supplied exterior temple reference for the stone architecture, gopuram, green garden, trees, flowers, pathway and peaceful outdoor surroundings. Do not combine or redesign the two locations; maintain visual continuity between exterior and interior.
Lakshmi must remain the same elderly person shown in the supplied reference. Young Anu must remain the same young daughter shown in the childhood memory reference; do not use an adult woman as Anu.
Preserve Lakshmi's face, age, skin tone, hairstyle, bindi, saree and jewelry. Preserve young Anu's face, age, hairstyle and cream-colored traditional clothing. No face morphing, age transformation or character replacement.
Begin with a peaceful view of the temple garden and pathway. Lakshmi and young Anu slowly walk toward the entrance, with Lakshmi gently holding Anu's hand. Then make a smooth transition toward the interior Krishna shrine, where they stop and look at Krishna peacefully.
Inside, show the recognizable Krishna idol with flute, ornaments, flowers and garlands, warm brass oil lamps, devotional decorations and carved stone pillars. Anu looks with curiosity and admiration while Lakshmi smiles and places her hand near Anu's shoulder.
Use natural walking, hand, eye, facial, saree, hair, flower, leaf and lamp-flicker motion only. Slow stable camera, no fast cuts, dramatic zoom or shake.
Keep the architecture, identities and ages consistent. Do not add modern buildings, unrelated objects, prominent unrelated people, duplicate people, extra arms, hands or fingers. Maintain 16:9 landscape composition for 5-8 seconds.
""".strip(),
            question="Where did Lakshmi and Anu visit together?",
            options=[
                {"id": "temple", "label": "Temple", "correct": True, "action": "positive_recall"},
                {"id": "school", "label": "School", "correct": False, "action": "memory_cue"},
                {"id": "hospital", "label": "Hospital", "correct": False, "action": "memory_cue"},
            ],
            next_scene="memory_04_trip",
            reference_bundle=[
                {"type": "character", "path": "people/patient_lakshmi.png"},
                {"type": "character", "path": "people/daughter_anu.png"},
                {"type": "environment", "path": "memories/anu_lakshmi_temple.jpg"},
                {"type": "environment_exterior", "path": "places/family_temple.jpg"},
            ],
            action="positive_recall",
            characters=["people/patient_lakshmi.png", "people/daughter_anu.png"],
            environment="places/family_temple.jpg",
            story="Lakshmi remembers visiting the family temple with Anu.",
            reference_image_direct=True,
            character_reference_images=["memories/young_anu.jpeg"],
        ),
        _scene(
            scene_id="memory_04_trip",
            title="Family Trip",
            period="past",
            scene_type="recall_question",
            image="places/family_garden.jpg",
            prompt="""
Create a warm nostalgic reconstruction of Lakshmi and her daughter Anu
enjoying a family trip when Anu was younger.
Use the provided Lakshmi and Anu reference images.
Preserve their recognizable identities.
Use any provided travel or trip environment reference as the visual setting.
Show the mother and daughter enjoying their journey together.
Their expressions should be happy and relaxed.
This is a cherished memory from the past.
Anu should appear younger while remaining recognizable as Anu.
Natural movement.
Warm nostalgic atmosphere.
No text or captions.
""".strip(),
            question="What did Lakshmi and Anu enjoy doing together?",
            options=[
                {"id": "trip", "label": "Going on trips", "correct": True, "action": "positive_recall"},
                {"id": "home", "label": "Staying home", "correct": False, "action": "memory_cue"},
                {"id": "school", "label": "Going to school", "correct": False, "action": "memory_cue"},
            ],
            next_scene="memory_05_family",
            reference_bundle=[
                {"type": "character", "path": "people/patient_lakshmi.png"},
                {"type": "character", "path": "people/daughter_anu.png"},
            ],
            action="positive_recall",
            characters=["people/patient_lakshmi.png", "people/daughter_anu.png"],
            environment="places/family_garden.jpg",
            story="Lakshmi remembers enjoying a family trip with Anu.",
        ),
        _scene(
            scene_id="memory_05_family",
            title="Family Meal",
            period="past",
            scene_type="recall_question",
            image="food/rice.jpg",
            prompt="""
Create a warm nostalgic family-memory reconstruction.
Use the provided reference images of Lakshmi, Anu and Rahul.
Preserve their recognizable identities and family relationships.
Use the provided family meal image as the environment and composition reference.
Show Lakshmi, Anu and Rahul spending time together during a family meal.
Anu is Lakshmi's daughter.
Rahul is Lakshmi's son.
This is a memory from the past.
Show a peaceful, loving family atmosphere.
Natural gestures and subtle movement.
No text or captions.
""".strip(),
            question="Who is with Lakshmi?",
            options=[
                {"id": "anu_rahul", "label": "Anu and Rahul", "correct": True, "action": "positive_recall"},
                {"id": "anu_only", "label": "Anu", "correct": False, "action": "memory_cue"},
                {"id": "neighbor", "label": "A neighbor", "correct": False, "action": "memory_cue"},
            ],
            next_scene="memory_06_garden",
            reference_bundle=[
                {"type": "character", "path": "people/patient_lakshmi.png"},
                {"type": "character", "path": "people/daughter_anu.png"},
                {"type": "character", "path": "people/son_rahul.png"},
                {"type": "food", "path": "food/rice.jpg"},
            ],
            action="positive_recall",
            characters=["people/patient_lakshmi.png", "people/daughter_anu.png", "people/son_rahul.png"],
            environment="home/living_room.jpg",
            objects=["food/rice.jpg", "food/banana.jpg"],
            story="Lakshmi remembers sharing a family meal with Anu and Rahul.",
        ),
        _scene(
            scene_id="memory_06_garden",
            title="Family Garden",
            period="past",
            scene_type="recall_question",
            image="places/family_garden.jpg",
            prompt="""
Create a peaceful nostalgic memory reconstruction of Lakshmi
and her daughter Anu spending time together in their family garden.
Use the provided Lakshmi and Anu images as character references.
Preserve their recognizable identities.
Use the provided family garden image as the environment reference.
Preserve the recognizable plants, layout and surroundings.
Show Lakshmi and Anu walking slowly together and enjoying the garden.
This is a memory from Anu's younger years.
Anu may appear younger while remaining recognizable.
Gentle natural movement.
Warm sunlight.
Peaceful emotional atmosphere.
No text or captions.
""".strip(),
            question="Where did Lakshmi and Anu spend time together?",
            options=[
                {"id": "garden", "label": "Garden", "correct": True, "action": "positive_recall"},
                {"id": "hospital", "label": "Hospital", "correct": False, "action": "memory_cue"},
                {"id": "school", "label": "School", "correct": False, "action": "memory_cue"},
            ],
            next_scene="memory_07_radio",
            reference_bundle=[
                {"type": "character", "path": "people/patient_lakshmi.png"},
                {"type": "character", "path": "people/daughter_anu.png"},
                {"type": "environment", "path": "places/family_garden.jpg"},
            ],
            action="positive_recall",
            characters=["people/patient_lakshmi.png", "people/daughter_anu.png"],
            environment="places/family_garden.jpg",
            story="Lakshmi remembers spending time with Anu in the family garden.",
        ),
        _scene(
            scene_id="memory_07_radio",
            title="Old Radio",
            period="past",
            scene_type="recall_question",
            image="home/living_room.jpg",
            prompt="""
Create a nostalgic evening memory inside Lakshmi's familiar home.
Use the provided images of Lakshmi and Anu as character references.
Preserve their recognizable identities.
Use the provided living-room image as the environment reference.
Use the provided old radio image as the object reference.
Show Lakshmi sitting near the old radio while her daughter Anu
spends a peaceful evening with her.
This is a cherished memory from the past.
Show subtle interaction between mother and daughter.
Warm evening lighting.
Gentle natural movement.
No text or captions.
""".strip(),
            question="What familiar object reminds Lakshmi of her home?",
            options=[
                {"id": "radio", "label": "Old radio", "correct": True, "action": "positive_recall"},
                {"id": "smartphone", "label": "Smartphone", "correct": False, "action": "memory_cue"},
                {"id": "laptop", "label": "Laptop", "correct": False, "action": "memory_cue"},
            ],
            next_scene="present_transition",
            reference_bundle=[
                {"type": "character", "path": "people/patient_lakshmi.png"},
                {"type": "character", "path": "people/daughter_anu.png"},
                {"type": "environment", "path": "home/living_room.jpg"},
                {"type": "object", "path": "objects/old_radio.jpg"},
            ],
            action="positive_recall",
            characters=["people/patient_lakshmi.png", "people/daughter_anu.png"],
            environment="home/living_room.jpg",
            objects=["objects/old_radio.jpg"],
            story="Lakshmi remembers listening to the old radio with Anu.",
        ),
        _scene(
            scene_id="present_transition",
            title="Memory to Present",
            period="present",
            scene_type="narrative",
            image="home/family_house_front.png",
            prompt="""
Create a gentle present-day reunion scene.
Use the provided present-day images of Lakshmi and adult Anu
as the primary character references.
Preserve their recognizable facial features, hairstyles,
complexion, clothing characteristics and identities.
Use the provided image of Lakshmi's actual house as the environment reference.
Preserve the recognizable architecture and surroundings.
Show adult Anu returning to her mother's home after many years away.
Anu slowly approaches the familiar home.
She is emotional but calm and hopeful.
Lakshmi is inside her familiar home.
This is the present day, not a childhood memory.
Do not make Anu young.
Do not replace Lakshmi or Anu with different people.
Do not change the house.
Natural realistic movement.
Gentle emotional atmosphere.
No text, captions or logos.
""".strip(),
            question=None,
            options=[],
            next_scene="present_entry",
            reference_bundle=[
                {"type": "character", "path": "people/patient_lakshmi.png"},
                {"type": "character", "path": "people/daughter_anu.png"},
                {"type": "environment", "path": "home/family_house_front.png"},
            ],
            action="reunion_intro",
            characters=["people/patient_lakshmi.png", "people/daughter_anu.png"],
            environment="home/family_house_front.png",
            story="Lakshmi's memories fade into the present as adult Anu returns home.",
        ),
        _scene(
            scene_id="present_entry",
            title="Anu Enters the Home",
            period="present",
            scene_type="narrative",
            image="home/living_room.jpg",
            prompt="""
Create a realistic present-day mother-daughter reunion.
Use the provided present-day Lakshmi and adult Anu images
as strict visual character references.
Use the provided living-room/home image as the environment reference.
Adult Anu enters the familiar home and slowly walks toward
her elderly mother Lakshmi.
Preserve the identities and recognizable appearance of both women.
Anu walks naturally with realistic leg and arm movement.
Lakshmi looks toward Anu with uncertainty and emotion.
Anu approaches her mother gently.
Keep the scene calm, intimate and hopeful.
Do not create a different house.
Do not replace either character.
Do not make Anu younger.
No text, captions or logos.
""".strip(),
            question=None,
            options=[],
            next_scene="reunion_hug",
            reference_bundle=[
                {"type": "character", "path": "people/patient_lakshmi.png"},
                {"type": "character", "path": "people/daughter_anu.png"},
                {"type": "environment", "path": "home/living_room.jpg"},
            ],
            action="walk_toward_mother",
            characters=["people/patient_lakshmi.png", "people/daughter_anu.png"],
            environment="home/living_room.jpg",
            story="Adult Anu enters the familiar home and walks toward Lakshmi.",
        ),
        _scene(
            scene_id="reunion_hug",
            title="Mother and Daughter Reunion",
            period="present",
            scene_type="reward",
            image="home/living_room.jpg",
            prompt="""
Create the final emotional present-day reunion between Lakshmi and her adult daughter Anu.
Use the provided present-day reference images of Lakshmi and Anu as strict identity references.
Preserve their facial appearance, age, hairstyle, clothing and recognizable identity.
Use the provided living-room image to preserve Lakshmi's familiar home environment.
Adult Anu gently reaches Lakshmi and embraces her.
Show a natural affectionate mother-daughter hug with realistic arm movement and gentle contact.
Their expressions communicate warmth, love, relief and emotional connection.
Keep both characters recognizable throughout and end with them peacefully embracing.
No text, captions, logos or watermark.
""".strip(),
            question=None,
            options=[],
            next_scene=None,
            reference_bundle=[
                {"type": "character", "path": "people/patient_lakshmi.png"},
                {"type": "character", "path": "people/daughter_anu.png"},
                {"type": "environment", "path": "home/living_room.jpg"},
            ],
            action="hug",
            characters=["people/patient_lakshmi.png", "people/daughter_anu.png"],
            environment="home/living_room.jpg",
            story="Adult Anu and Lakshmi reunite in a loving embrace.",
        ),
    ]

    return {
        "story_id": "lakshmi_anu_memory_journey",
        "title": "Lakshmi's Memories",
        "patient": "Lakshmi",
        "main_character": "Anu",
        "description": "A gentle scene-by-scene memory journey from past memories to a present-day mother-daughter reunion.",
        "scenes": scenes,
    }


def build_lakshmi_anu_story():
    return build_lakshmi_memory_journey()
