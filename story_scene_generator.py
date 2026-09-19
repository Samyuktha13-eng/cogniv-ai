"""
Story Scene Generator - Build the complete 11-scene Lakshmi-Anu narrative.

Constructs detailed scene objects with video prompts from patient repository assets.
"""

from typing import List, Optional
from pathlib import Path
from story_scene_schema import (
    StoryScene, SceneMetadata, ScenePeriod, Character, Reference
)


class StorySceneGenerator:
    """Generate structured video scenes from patient memories."""
    
    def __init__(self, patient_dir: str = "Patient_001_Lakshmi"):
        """
        Initialize the generator.
        
        Args:
            patient_dir: Path to patient data directory
        """
        self.patient_dir = Path(patient_dir)
        self.base_path = self.patient_dir
    
    def _make_ref(self, name: str, rel_path: str) -> Reference:
        """Create a reference to a patient asset."""
        full_path = str(self.base_path / rel_path)
        return Reference(name=name, asset_path=full_path)
    
    def build_all_scenes(self) -> List[StoryScene]:
        """Build all 11 scenes of the Lakshmi-Anu story."""
        scenes = [
            self._build_scene_01_home(),
            self._build_scene_02_remembers_anu(),
            self._build_scene_03_making_chapathi(),
            self._build_scene_04_temple(),
            self._build_scene_05_family_trip(),
            self._build_scene_06_family_meal(),
            self._build_scene_07_family_garden(),
            self._build_scene_08_old_radio(),
            self._build_scene_09_transition(),
            self._build_scene_10_anu_enters(),
            self._build_scene_11_reunion_hug(),
        ]
        return scenes
    
    def _build_scene_01_home(self) -> StoryScene:
        """Video 1 - Lakshmi at Home / Beginning"""
        return StoryScene(
            metadata=SceneMetadata(
                scene_id="memory_01_home",
                sequence_number=1,
                title="Lakshmi at Home / Beginning",
                period=ScenePeriod.PAST,
            ),
            characters=[
                Character(
                    name="Lakshmi",
                    character_id="lakshmi",
                    reference_images=[self._make_ref("Lakshmi", "people/patient_lakshmi")],
                    emotional_state="thoughtful, peaceful",
                )
            ],
            environment=self._make_ref("Living Room", "home/living_room"),
            objects=[self._make_ref("Family Photo", "objects/family_photo")],
            story_context="Lakshmi sits peacefully inside her familiar family home, remembering her daughter.",
            video_prompt="""Create a warm cinematic memory scene of Lakshmi, an elderly Indian woman, sitting peacefully inside her familiar family home.

Use the provided Lakshmi reference image to preserve her facial appearance, grey hair, saree, bindi, jewelry, age and overall identity.

Use the provided living-room and house reference images to preserve the actual architecture, furniture, colors, layout and atmosphere of Lakshmi's home.

Lakshmi sits quietly and looks around her familiar home. She gently looks toward a familiar family photograph and begins remembering her daughter.

Her expression slowly changes from thoughtful to warm and emotional.

Natural subtle movement: blinking, breathing, gentle head movement and natural hand movement.

The scene should feel like a gentle autobiographical memory, not a dramatic movie scene.

Warm nostalgic atmosphere, realistic Indian home, natural lighting, slow camera movement.

No text, no captions, no logos, no watermark.""",
            notes="Opening scene establishing Lakshmi in her home, beginning the memory journey.",
        )
    
    def _build_scene_02_remembers_anu(self) -> StoryScene:
        """Video 2 - Lakshmi Remembers Anu"""
        return StoryScene(
            metadata=SceneMetadata(
                scene_id="memory_02_anu",
                sequence_number=2,
                title="Lakshmi Remembers Anu",
                period=ScenePeriod.PAST,
            ),
            characters=[
                Character(
                    name="Lakshmi",
                    character_id="lakshmi",
                    reference_images=[self._make_ref("Lakshmi", "people/patient_lakshmi")],
                    emotional_state="nostalgic, recognizing",
                ),
                Character(
                    name="Anu",
                    character_id="anu",
                    reference_images=[self._make_ref("Anu", "people/anu")],
                    age_note="appearing younger in this past memory",
                    emotional_state="warm, smiling",
                )
            ],
            environment=self._make_ref("Living Room", "home/living_room"),
            objects=[self._make_ref("Family Photo", "objects/family_photo")],
            story_context="Lakshmi remembers her daughter Anu appearing in her home from past memories.",
            video_prompt="""Create a gentle autobiographical memory reconstruction in which Lakshmi remembers her daughter Anu.

Use the provided reference images of Lakshmi and Anu as the primary identity references.

Preserve the recognizable facial characteristics and overall appearance of both people, while allowing Anu to appear somewhat younger because this is a memory from the past.

Lakshmi sits in her familiar living room and looks at a photograph of Anu.

The memory gradually transitions to Anu appearing in Lakshmi's remembered home.

Anu smiles warmly at Lakshmi.

Lakshmi looks at Anu with a familiar motherly expression, as if she is trying to recognize and remember her daughter.

Use subtle natural movement: blinking, breathing, facial expressions and gentle body movement.

The scene should communicate recognition and emotional familiarity rather than sadness.

Warm nostalgic lighting and peaceful atmosphere.

No text, no captions, no logos, no watermark.""",
            notes="Key memory introduction scene - Anu appears in Lakshmi's memory.",
        )
    
    def _build_scene_03_making_chapathi(self) -> StoryScene:
        """Video 3 - Anu and Lakshmi Making Chapathi"""
        return StoryScene(
            metadata=SceneMetadata(
                scene_id="memory_03_chapathi",
                sequence_number=3,
                title="Anu and Lakshmi Making Chapathi",
                period=ScenePeriod.PAST,
            ),
            characters=[
                Character(
                    name="Lakshmi",
                    character_id="lakshmi",
                    reference_images=[self._make_ref("Lakshmi", "people/patient_lakshmi")],
                    emotional_state="content, engaged",
                ),
                Character(
                    name="Anu",
                    character_id="anu",
                    reference_images=[self._make_ref("Anu", "people/anu")],
                    age_note="appearing younger in this past memory",
                    emotional_state="loving, focused",
                )
            ],
            environment=self._make_ref("Kitchen", "home/kitchen"),
            objects=[self._make_ref("Chapathi", "food/chapathi")],
            story_context="Shared family memory of cooking chapathi together in the kitchen.",
            video_prompt="""Create a warm nostalgic memory reconstruction of Lakshmi and her daughter Anu spending time together in their familiar family kitchen.

Use the provided Anu and Lakshmi reference images to maintain recognizable identities.

Because this is a past memory, Anu may appear younger than her present-day reference while still remaining recognizably the same person.

Use the provided kitchen reference image to preserve the actual kitchen environment, layout and visual characteristics.

Use the provided chapathi reference image as a visual reference for the food.

Anu lovingly prepares chapathi dough and cooks chapathi while Lakshmi stands beside her and helps.

Show realistic hand movements while preparing the chapathi, gentle interaction between mother and daughter, natural facial expressions and warm smiles.

Show the chapathi clearly enough that it can function as a visual memory cue.

The scene should feel like a genuine warm family memory reconstruction.

Natural Indian home atmosphere, warm lighting, gentle camera movement.

No text, no captions, no logos, no watermark.""",
            notes="Important memory scene - cooking activity with clear food recognition element.",
        )
    
    def _build_scene_04_temple(self) -> StoryScene:
        """Video 4 - Temple Memory"""
        return StoryScene(
            metadata=SceneMetadata(
                scene_id="memory_04_temple",
                sequence_number=4,
                title="Temple Memory",
                period=ScenePeriod.PAST,
            ),
            characters=[
                Character(
                    name="Lakshmi",
                    character_id="lakshmi",
                    reference_images=[self._make_ref("Lakshmi", "people/patient_lakshmi")],
                    emotional_state="peaceful, reverent",
                ),
                Character(
                    name="Anu",
                    character_id="anu",
                    reference_images=[self._make_ref("Anu", "people/anu")],
                    age_note="appearing younger, before marriage",
                    emotional_state="reverent, affectionate",
                )
            ],
            environment=self._make_ref("Family Temple", "places/family_temple"),
            story_context="Lakshmi and Anu visit the family temple together before Anu's marriage.",
            video_prompt="""Create a peaceful nostalgic memory reconstruction of Lakshmi visiting the family's familiar temple with her daughter Anu before Anu's marriage.

Use the provided Lakshmi and Anu reference images to preserve their recognizable identities.

Because this is a memory from the past, Anu should appear younger while still remaining recognizable as the same daughter.

Use the provided family temple reference image as the primary environment reference.

Lakshmi and young adult Anu walk slowly together toward the familiar temple.

They walk naturally side by side, with realistic leg movement, arm movement and gentle body motion.

Anu looks at Lakshmi and smiles affectionately.

Lakshmi looks at Anu with a warm motherly expression.

The temple environment should closely resemble the provided reference image.

Peaceful, respectful atmosphere, warm natural lighting and nostalgic visual tone.

Do not add unrelated people or change the temple architecture significantly.

No text, no captions, no logos, no watermark.""",
            notes="Spiritual/cultural memory - demonstrates family traditions and milestones.",
        )
    
    def _build_scene_05_family_trip(self) -> StoryScene:
        """Video 5 - Family Trip"""
        return StoryScene(
            metadata=SceneMetadata(
                scene_id="memory_05_trip",
                sequence_number=5,
                title="Family Trip",
                period=ScenePeriod.PAST,
            ),
            characters=[
                Character(
                    name="Lakshmi",
                    character_id="lakshmi",
                    reference_images=[self._make_ref("Lakshmi", "people/patient_lakshmi")],
                    emotional_state="relaxed, happy",
                ),
                Character(
                    name="Anu",
                    character_id="anu",
                    reference_images=[self._make_ref("Anu", "people/anu")],
                    age_note="appearing younger",
                    emotional_state="joyful, engaged",
                ),
                Character(
                    name="Rahul",
                    character_id="rahul",
                    reference_images=[self._make_ref("Rahul", "people/rahul")],
                    age_note="appearing younger",
                    emotional_state="happy",
                )
            ],
            objects=[self._make_ref("Trip location", "places/trip_location")],
            story_context="Family spending happy time together during a trip.",
            video_prompt="""Create a warm nostalgic family-memory reconstruction showing Lakshmi spending happy family time with Anu and Rahul during a family trip.

Use the provided reference images of Lakshmi, Anu and Rahul to preserve their recognizable identities.

This is a memory from the past, so Anu and Rahul may appear younger than their present-day reference images while remaining recognizable as the same family members.

Show the family walking together, looking at the surroundings, smiling and enjoying their time together.

Lakshmi should appear relaxed and happy.

Anu should interact naturally with Lakshmi.

Rahul should remain part of the family scene and interact naturally with them.

Use natural walking, facial expressions, gestures and body movement.

The scene should feel like a cherished family memory rather than a staged photoshoot.

Warm nostalgic lighting, peaceful atmosphere and cinematic but realistic movement.

No text, no captions, no logos, no watermark.""",
            notes="Multi-generational family memory scene.",
        )
    
    def _build_scene_06_family_meal(self) -> StoryScene:
        """Video 6 - Family Meal"""
        return StoryScene(
            metadata=SceneMetadata(
                scene_id="memory_06_family_meal",
                sequence_number=6,
                title="Family Meal",
                period=ScenePeriod.PAST,
            ),
            characters=[
                Character(
                    name="Lakshmi",
                    character_id="lakshmi",
                    reference_images=[self._make_ref("Lakshmi", "people/patient_lakshmi")],
                    emotional_state="content, nurturing",
                ),
                Character(
                    name="Anu",
                    character_id="anu",
                    reference_images=[self._make_ref("Anu", "people/anu")],
                    age_note="appearing younger",
                    emotional_state="affectionate, present",
                ),
                Character(
                    name="Rahul",
                    character_id="rahul",
                    reference_images=[self._make_ref("Rahul", "people/rahul")],
                    age_note="appearing younger",
                    emotional_state="happy",
                )
            ],
            environment=self._make_ref("Dining Room", "home/dining_room"),
            objects=[
                self._make_ref("Rice", "food/rice"),
                self._make_ref("Banana", "food/banana"),
            ],
            story_context="Family sharing a meal together at home.",
            video_prompt="""Create a warm nostalgic reconstruction of a family meal at Lakshmi's home.

Use the provided reference images of Lakshmi, Anu and Rahul to preserve their recognizable identities.

Because this is a past family memory, Anu and Rahul may appear younger while remaining recognizable.

Use the provided home reference image to preserve the familiar family environment.

Lakshmi, Anu and Rahul sit together and share a peaceful family meal.

Show recognizable Indian food, including rice and banana based on the provided food references.

Show natural eating gestures, gentle conversation, smiling and affectionate family interaction.

Lakshmi looks happy while spending time with her daughter and son.

The scene should emphasize family connection and familiarity.

Natural movement, realistic expressions, warm nostalgic lighting.

No text, no captions, no logos, no watermark.""",
            notes="Family bonding scene with food and emotional connection.",
        )
    
    def _build_scene_07_family_garden(self) -> StoryScene:
        """Video 7 - Family Garden"""
        return StoryScene(
            metadata=SceneMetadata(
                scene_id="memory_07_garden",
                sequence_number=7,
                title="Family Garden",
                period=ScenePeriod.PAST,
            ),
            characters=[
                Character(
                    name="Lakshmi",
                    character_id="lakshmi",
                    reference_images=[self._make_ref("Lakshmi", "people/patient_lakshmi")],
                    emotional_state="peaceful, observant",
                ),
                Character(
                    name="Anu",
                    character_id="anu",
                    reference_images=[self._make_ref("Anu", "people/anu")],
                    age_note="appearing younger",
                    emotional_state="caring, engaged",
                )
            ],
            environment=self._make_ref("Family Garden", "places/family_garden"),
            story_context="Lakshmi and Anu spending time together in their familiar garden.",
            video_prompt="""Create a peaceful nostalgic memory reconstruction of Lakshmi spending time with her daughter Anu in their familiar family garden.

Use the provided Lakshmi and Anu reference images to preserve their recognizable identities.

This is a past memory, so Anu may appear younger while remaining recognizable as Lakshmi's daughter.

Use the provided family garden reference image to preserve the actual garden environment, plants, layout and atmosphere.

Lakshmi and Anu walk slowly through the garden together.

Anu gently talks with Lakshmi and smiles.

Lakshmi looks at the plants and then at Anu with a warm motherly expression.

Show natural walking, hand gestures, facial expressions and subtle environmental movement.

The scene should feel peaceful, familiar and emotionally positive.

Warm evening sunlight, gentle nostalgic atmosphere and realistic movement.

No text, no captions, no logos, no watermark.""",
            notes="Peaceful nature scene with intimate family connection.",
        )
    
    def _build_scene_08_old_radio(self) -> StoryScene:
        """Video 8 - Old Radio Memory"""
        return StoryScene(
            metadata=SceneMetadata(
                scene_id="memory_08_radio",
                sequence_number=8,
                title="Old Radio Memory",
                period=ScenePeriod.PAST,
            ),
            characters=[
                Character(
                    name="Lakshmi",
                    character_id="lakshmi",
                    reference_images=[self._make_ref("Lakshmi", "people/patient_lakshmi")],
                    emotional_state="nostalgic, content",
                ),
                Character(
                    name="Anu",
                    character_id="anu",
                    reference_images=[self._make_ref("Anu", "people/anu")],
                    age_note="appearing younger",
                    emotional_state="playful, attentive",
                )
            ],
            environment=self._make_ref("Living Room", "home/living_room"),
            objects=[self._make_ref("Old Radio", "objects/old_radio")],
            story_context="Lakshmi and Anu listening to the old radio together.",
            video_prompt="""Create a warm nostalgic memory reconstruction inside Lakshmi's familiar living room.

Use the provided Lakshmi and Anu reference images to preserve their recognizable identities.

Use the provided living-room and old-radio reference images to preserve the familiar environment and object.

This is a memory from the past, so Anu may appear younger while remaining recognizable as Lakshmi's daughter.

Lakshmi sits comfortably near the old radio.

Anu sits beside her.

The old radio is clearly visible.

Anu gently adjusts or switches on the radio while Lakshmi smiles.

They sit together peacefully and listen to the radio.

Show subtle natural movement such as blinking, breathing, gentle head movement and small hand gestures.

The atmosphere should feel like a quiet cherished family memory.

Warm vintage lighting and gentle nostalgic mood.

No text, no captions, no logos, no watermark.""",
            notes="Object-focused memory scene with vintage atmosphere.",
        )
    
    def _build_scene_09_transition(self) -> StoryScene:
        """Video 9 - Transition From Memory to Present"""
        return StoryScene(
            metadata=SceneMetadata(
                scene_id="present_01_transition",
                sequence_number=9,
                title="Transition From Memory to Present",
                period=ScenePeriod.TRANSITION,
            ),
            characters=[
                Character(
                    name="Lakshmi",
                    character_id="lakshmi",
                    reference_images=[self._make_ref("Lakshmi", "people/patient_lakshmi")],
                    emotional_state="awakening, emotional",
                ),
                Character(
                    name="Anu",
                    character_id="anu",
                    reference_images=[self._make_ref("Anu", "people/anu")],
                    age_note="present-day adult",
                    emotional_state="hopeful, emotional",
                )
            ],
            environment=self._make_ref("House", "home/house"),
            story_context="Transition from past memories into the present day as Anu returns home.",
            video_prompt="""Create a cinematic transition from Lakshmi's past memories into the present day.

Use the provided present-day reference images of Lakshmi and adult Anu.

Preserve their current facial appearance, age, hairstyle, clothing and identity accurately.

Begin with a gentle visual feeling of memories fading away.

Gradually transition into the present-day family home.

The home should closely match the provided house reference image.

Adult Anu has returned to India after many years and is approaching her mother's home.

Show Anu standing outside the familiar home and preparing to enter.

Her expression is emotional, caring and hopeful.

The scene should clearly feel different from the earlier younger-memory scenes: this is the present day.

Natural realistic movement and cinematic but believable camera motion.

No text, no captions, no logos, no watermark.""",
            notes="Critical transition - shift from memories to present day.",
        )
    
    def _build_scene_10_anu_enters(self) -> StoryScene:
        """Video 10 - Anu Enters the Home"""
        return StoryScene(
            metadata=SceneMetadata(
                scene_id="present_02_anu_enters",
                sequence_number=10,
                title="Anu Enters the Home",
                period=ScenePeriod.PRESENT,
            ),
            characters=[
                Character(
                    name="Lakshmi",
                    character_id="lakshmi",
                    reference_images=[self._make_ref("Lakshmi", "people/patient_lakshmi")],
                    emotional_state="surprised, recognizing",
                ),
                Character(
                    name="Anu",
                    character_id="anu",
                    reference_images=[self._make_ref("Anu", "people/anu")],
                    age_note="present-day adult",
                    emotional_state="emotional, gentle",
                )
            ],
            environment=self._make_ref("House", "home/house"),
            story_context="Adult Anu returns home and enters to see her mother Lakshmi.",
            video_prompt="""Create a realistic present-day emotional reunion scene.

Use the provided present-day reference image of adult Anu as the primary identity reference.

Use the provided present-day reference image of Lakshmi as the primary identity reference.

Use the provided house and living-room reference images to preserve Lakshmi's actual familiar home.

Adult Anu has returned home after many years to see her mother Lakshmi.

Show Anu naturally entering the familiar house and walking toward Lakshmi.

Anu must remain recognizable as the adult woman from the provided reference image.

Lakshmi must remain recognizable as the elderly woman from her provided reference image.

Show realistic walking movement: natural alternating leg movement, natural arm movement, body movement and facial expressions.

Lakshmi notices Anu and looks toward her.

Anu approaches slowly with an emotional but gentle smile.

The home environment should remain consistent with the provided reference images.

Do not invent a different house.

Natural cinematic camera movement, realistic lighting and emotionally warm atmosphere.

No text, no captions, no logos, no watermark.""",
            notes="Key present-day reunion scene - Anu enters the home.",
        )
    
    def _build_scene_11_reunion_hug(self) -> StoryScene:
        """Video 11 - Final Mother-Daughter Hug"""
        return StoryScene(
            metadata=SceneMetadata(
                scene_id="present_03_reunion_hug",
                sequence_number=11,
                title="Final Mother-Daughter Hug",
                period=ScenePeriod.PRESENT,
            ),
            characters=[
                Character(
                    name="Lakshmi",
                    character_id="lakshmi",
                    reference_images=[self._make_ref("Lakshmi", "people/patient_lakshmi")],
                    emotional_state="loving, recognizing, emotional",
                ),
                Character(
                    name="Anu",
                    character_id="anu",
                    reference_images=[self._make_ref("Anu", "people/anu")],
                    age_note="present-day adult",
                    emotional_state="affectionate, relieved, loving",
                )
            ],
            environment=self._make_ref("Living Room", "home/living_room"),
            story_context="Lakshmi and Anu embrace in a final emotional reunion.",
            video_prompt="""Create the final emotional present-day reunion between Lakshmi and her adult daughter Anu.

Use the provided present-day reference images of Lakshmi and Anu as strict identity references.

Preserve their facial appearance, age, hairstyle, clothing and recognizable identity.

Use the provided living-room reference image to preserve Lakshmi's familiar home environment.

Adult Anu has finally returned home after many years to see her mother.

Anu slowly approaches Lakshmi.

Lakshmi looks at Anu.

Anu gently reaches her mother and embraces her.

Show a natural, affectionate mother-daughter hug.

Both women gently hold each other.

Their expressions should communicate warmth, love, relief and emotional connection.

The hug should look physically natural: arms move around each other naturally, bodies make gentle contact, clothing moves naturally, and facial expressions remain stable.

Keep both characters recognizable throughout the entire video.

Do not change their faces or transform their identities.

Keep the living-room environment consistent with the provided reference.

End with Anu and Lakshmi peacefully embracing.

Warm soft lighting, subtle emotional background atmosphere, realistic cinematic movement.

No text, no captions, no logos, no watermark.""",
            notes="Emotional climax - final reunion scene with mother and daughter embrace.",
        )


def generate_lakshmi_anu_scenes() -> List[StoryScene]:
    """
    Generate all 11 scenes for the Lakshmi-Anu story.
    
    Returns:
        List of 11 StoryScene objects ready for video generation
    """
    generator = StorySceneGenerator()
    return generator.build_all_scenes()


if __name__ == "__main__":
    # Generate and print summary of all scenes
    scenes = generate_lakshmi_anu_scenes()
    print(f"Generated {len(scenes)} scenes for Lakshmi-Anu story:\n")
    
    for scene in scenes:
        print(f"[{scene.metadata.sequence_number}] {scene.metadata.scene_id}")
        print(f"    Title: {scene.metadata.title}")
        print(f"    Period: {scene.metadata.period.value}")
        print(f"    Characters: {[c.name for c in scene.characters]}")
        print()
