"""
CLI Game Demo - Test the game flow with actual patient data.
This demonstrates the complete flow without a UI.
"""

from pathlib import Path
from memory_repository import MemoryRepository
from game import GameScenario
from outcome_tracker import OutcomeTracker


def print_section(title: str):
    """Print a formatted section header."""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)


def display_game_question(question_data: dict):
    """Display a game question."""
    print(f"\n{question_data['question_text']}")
    print(f"\n[IMAGE: {Path(question_data['image']).name}]")
    print("\nOptions:")
    for i, option in enumerate(question_data['options'], 1):
        print(f"  {i}. {option['text']}")


def display_response(response: dict):
    """Display game response."""
    print(f"\n✓ {response['message']}")
    print(f"  Animation: {response.get('reward_animation') or response.get('encouragement_animation') or 'none'}")
    
    if response.get('memory_cue'):
        print("\n💡 Memory Cue:")
        print(f"   {response['memory_cue']['text']}")
        if response['memory_cue']['image']:
            print(f"   [IMAGE: {Path(response['memory_cue']['image']).name}]")
    
    if response.get('show_correct'):
        print(f"\n   The correct answer is: {response['correct_answer']}")


def run_demo():
    """Run a complete game demo."""
    
    print_section("DEMENTIA MEMORY PLATFORM - GAME DEMO")
    
    # Setup
    patient_folder = Path(r"C:\Users\DELL\Downloads\Cognitiveai\Patient_001_Lakshmi")
    
    # Load patient data
    print("\n📁 Loading patient data...")
    repo = MemoryRepository(patient_folder)
    profile = repo.load()
    print(f"✓ Loaded patient: {profile.patient_name}")
    print(f"  - People: {len(profile.people)}")
    print(f"  - Places: {len(profile.places)}")
    print(f"  - Food items: {len(profile.food)}")
    print(f"  - Memories: {len(profile.memories)}")
    
    # Initialize tracker and game
    tracker = OutcomeTracker(profile.patient_id, patient_folder)
    scenario = GameScenario(repo, tracker)
    
    # Start game
    print_section("GAME: REMEMBER MY DAUGHTER")
    
    # Question 1
    print("\n📖 Scene: Familiar Family Home")
    print("   'Good morning, Lakshmi. Let's spend time with your memories.'")
    
    print("\n🎮 Starting First Question...")
    scenario.flow.start_game_session("session_001")
    q1 = scenario.generator.generate_person_recognition_game("daughter")
    question = scenario.flow.present_question(q1)
    display_game_question(question)
    
    # Find correct option (Anu)
    correct_option_id = None
    wrong_option_id = None
    for opt in q1.options:
        if opt.correct:
            correct_option_id = opt.id
        elif wrong_option_id is None:
            wrong_option_id = opt.id
    
    # Simulate wrong answer first
    print(f"\n👵 Patient answers: {[o.text for o in q1.options if o.id == wrong_option_id][0]}")
    response, allow_retry = scenario.flow.handle_answer(wrong_option_id)
    display_response(response)
    
    if allow_retry:
        print("\n🔄 Retrying...")
        print(f"\n👵 Patient answers: {[o.text for o in q1.options if o.id == correct_option_id][0]}")
        response, _ = scenario.flow.handle_answer(correct_option_id)
        display_response(response)
    
    # Question 2 - Food recognition
    print("\n" + "-"*60)
    print("\n🎮 Second Question: Food Recognition")
    q2 = scenario.generator.generate_food_recognition_game("food_chapathi")
    question2 = scenario.flow.present_question(q2)
    display_game_question(question2)
    
    # Find correct option
    correct_food_id = None
    for opt in q2.options:
        if opt.correct:
            correct_food_id = opt.id
            break
    
    correct_text = [o.text for o in q2.options if o.id == correct_food_id][0]
    print(f"\n👵 Patient answers: {correct_text}")
    response, _ = scenario.flow.handle_answer(correct_food_id)
    display_response(response)
    
    # End game
    print_section("GAME COMPLETE")
    end_data = scenario.flow.end_game()
    print(f"\n{end_data['message']}")
    print(f"\nSession Summary:")
    for key, value in end_data['summary'].items():
        print(f"  {key}: {value}")
    
    # Show patient profile
    print_section("PATIENT COGNITIVE PROFILE")
    print(tracker.get_performance_summary())


if __name__ == "__main__":
    run_demo()
