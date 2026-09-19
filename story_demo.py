"""
Story Demo - Play through the complete "A Visit From Anu" narrative.
Shows the full 8-scene story flow with memory connections.
"""

from pathlib import Path
from memory_repository import MemoryRepository
from game_generator import GameGenerator
from outcome_tracker import OutcomeTracker
from story_builder import StoryBuilder
from story_flow import StoryFlowEngine


def print_section(title: str):
    """Print a formatted section header."""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)


def print_scene(scene_data: dict):
    """Print scene information."""
    print(f"\n🎬 SCENE: {scene_data['title']}")
    print(f"   Narration: {scene_data['narration']}")
    
    if scene_data['memory_chain']:
        print(f"\n   Memory Chain:")
        for i, link in enumerate(scene_data['memory_chain'], 1):
            print(f"   {i}. [{link['entity_type'].upper()}] {link['name']}")
            print(f"      {link['narration']}")
            if link['image']:
                print(f"      📁 {Path(link['image']).name}")
    
    if scene_data['question_text']:
        print(f"\n   ❓ Question: {scene_data['question_text']}")
        print(f"      Image: {Path(scene_data['question_image']).name if scene_data['question_image'] else 'N/A'}")
        print(f"      Options:")
        for opt in scene_data['options']:
            print(f"        • {opt['text']}")


def print_response(response: dict):
    """Print story response."""
    if response.get('result') == 'correct':
        print(f"\n   ✓ {response['message']}")
        print(f"     Animation: {response.get('animation_cue', 'none')}")
        print(f"     Hint level: {0 if not response.get('hint_used') else 1}")
    elif response.get('narration'):
        print(f"\n   💭 {response['narration']}")
        if response.get('animation_cue'):
            print(f"      Animation: {response['animation_cue']}")
    else:
        print(f"\n   Response: {response}")


def run_story_demo():
    """Run the complete story demo."""
    
    print_section("DEMENTIA MEMORY PLATFORM - STORY DEMO")
    print("'A Visit From Anu' - A Narrative Memory Experience")
    
    # Setup
    patient_folder = Path(r"C:\Users\DELL\Downloads\Cognitiveai\Patient_001_Lakshmi")
    
    # Load patient data
    print("\n📁 Loading patient data...")
    repo = MemoryRepository(patient_folder)
    profile = repo.load()
    print(f"✓ Loaded patient: {profile.patient_name}")
    print(f"  - People: {len(profile.people)}")
    print(f"  - Memories: {len(profile.memories)}")
    
    # Build the story
    print("\n🎭 Building story...")
    builder = StoryBuilder(repo)
    story = builder.build_visit_from_anu_story()
    print(f"✓ Story built: {story.title}")
    print(f"  - Scenes: {len(story.scenes)}")
    print(f"  - Cognitive target: {story.cognitive_target}")
    print(f"  - Memory chain goal: {' → '.join(story.memory_chain_goal)}")
    
    # Initialize game components
    generator = GameGenerator(repo)
    tracker = OutcomeTracker(profile.patient_id, patient_folder)
    flow = StoryFlowEngine(story, generator, tracker)
    
    # START STORY
    print_section("🎮 STARTING STORY")
    
    # Scene 1 - Welcome
    print("\n📍 SCENE 1: Welcome to Home")
    scene_1_data = flow.start_story("story_001")
    print_scene(scene_1_data)
    print("\n👵 Patient chooses: 'Yes, I remember'")
    response, next_scene = flow.handle_scene_choice("opt_remember_yes")
    print_response(response)
    
    # Scene 2 - Kitchen (First recall question)
    print("\n" + "─"*70)
    print("\n📍 SCENE 2: The Kitchen")
    scene_2_data = flow.present_scene(next_scene)
    print_scene(scene_2_data)
    
    # Get the question object to find correct answer
    scene_2_obj = story.get_scene_by_id(next_scene)
    correct_option_id = None
    wrong_option_id = None
    for opt in scene_2_obj.question.options:
        if opt.correct:
            correct_option_id = opt.id
        else:
            if not wrong_option_id:
                wrong_option_id = opt.id
    
    # Wrong answer first
    print("\n👵 Patient chooses: Wrong person")
    response, next_scene_or_retry = flow.handle_recall_answer(wrong_option_id)
    print_response(response)
    
    if response.get('memory_cue'):
        print(f"\n   💡 Memory Cue: {response['memory_cue']['text']}")
        if response['memory_cue']['image']:
            print(f"      📁 {Path(response['memory_cue']['image']).name}")
    
    # Retry with correct answer
    print("\n👵 Patient retries: 'Anu'")
    response, next_scene = flow.handle_recall_answer(correct_option_id)
    print_response(response)
    
    # Scene 3A - Celebration
    print("\n" + "─"*70)
    print("\n📍 SCENE 3: Found Anu!")
    scene_3a_data = flow.present_scene(next_scene)
    print_scene(scene_3a_data)
    print("\n👵 Patient continues...")
    response, next_scene = flow.handle_scene_choice(scene_3a_data['options'][0]['id'])
    print_response(response)
    
    # Scene 6 - Food Recognition
    print("\n" + "─"*70)
    print("\n📍 SCENE 6: Food Recognition")
    scene_6_data = flow.present_scene(next_scene)
    print_scene(scene_6_data)
    
    # Get correct option from question object
    scene_6_obj = story.get_scene_by_id(next_scene)
    food_correct_id = None
    for opt in scene_6_obj.question.options:
        if opt.correct:
            food_correct_id = opt.id
            break
    
    print("\n👵 Patient chooses: Chapathi")
    response, next_scene = flow.handle_recall_answer(food_correct_id)
    print_response(response)
    
    # Scene 7 - Family Memory
    print("\n" + "─"*70)
    print("\n📍 SCENE 7: Family Memory")
    scene_7_data = flow.present_scene(next_scene)
    print_scene(scene_7_data)
    
    # Get correct option from question object
    scene_7_obj = story.get_scene_by_id(next_scene)
    family_correct_id = None
    for opt in scene_7_obj.question.options:
        if opt.correct:
            family_correct_id = opt.id
            break
    
    print("\n👵 Patient chooses: Family member")
    response, next_scene = flow.handle_recall_answer(family_correct_id)
    print_response(response)
    
    # Scene 8 - Reward
    print("\n" + "─"*70)
    print("\n📍 SCENE 8: Well Remembered!")
    scene_8_data = flow.present_scene(next_scene)
    print_scene(scene_8_data)
    print("\n👵 Patient finishes the story")
    
    # End story
    print_section("✨ STORY COMPLETE")
    end_data = flow.end_story()
    
    print(f"\n{end_data['message']}")
    print(f"\nStory Metrics:")
    print(f"  - Scenes visited: {end_data['scenes_visited']}")
    print(f"  - Memory associations made: {len(end_data['associations_made'])}")
    print(f"  - Total interactions: {end_data['events_count']}")
    
    print(f"\nMemory Associations:")
    for assoc in end_data['associations_made']:
        print(f"  ✓ {assoc}")
    
    # Show detailed outcome
    print(f"\nDetailed Outcomes:")
    print(f"  - Independent recalls: {end_data['summary']['independent_recalls']}")
    print(f"  - Cue-assisted recalls: {end_data['summary']['cue_assisted_recalls']}")
    print(f"  - Incorrect answers: {end_data['summary']['incorrect_answers']}")
    
    # Show patient profile
    print_section("PATIENT COGNITIVE PROFILE")
    print(tracker.get_performance_summary())
    
    print("\n✅ Story demo complete!")


if __name__ == "__main__":
    run_story_demo()
