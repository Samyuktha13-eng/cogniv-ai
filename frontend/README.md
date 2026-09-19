# Cognitive AI Memory Game - Web Frontend

A responsive web-based prototype for the Cognitive AI Memory Game Platform. This frontend consumes blueprints from the FastAPI backend and provides an interactive, accessible interface for patients to play memory games.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    CAREGIVER INTERFACE                          │
│              (Web Browser - This Frontend)                      │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         │ REST API Calls
                         │ (POST /game/create, /game/outcome)
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│                    FASTAPI BACKEND                              │
│            (localhost:8000)                                     │
│                                                                  │
│  • AI Agents (Goal, Memory, Story, Game)                        │
│  • Blueprint Generation                                         │
│  • Outcome Recording                                            │
│  • Cognitive Profile Aggregation                                │
└─────────────────────────────────────────────────────────────────┘
```

## Features

### ✅ Complete Game Flow

1. **Caregiver Input** → Sets patient goal ("Help Lakshmi remember Anu")
2. **Blueprint Generation** → AI creates personalized 8-scene game
3. **Scene Rendering** → Dynamic scene display with assets
4. **Interaction** → Patient selects answer from multiple choices
5. **Animations** → Visual feedback based on action sequences
6. **Outcome Recording** → Tracks responses and cognitive patterns
7. **Results** → Shows cognitive profile and performance metrics

### ✅ UI Components

- **Loading Screen** → Fetches blueprint from backend
- **Game Screen** → Main interactive scene with:
  - Background environment image
  - Character animations
  - Memory asset displays (food, objects)
  - Narration text
  - Question text (if applicable)
  - Answer option buttons
  - Scene progression info
- **Results Screen** → Summary statistics and cognitive profile
- **Error Screen** → Handles connection/validation errors

### ✅ Animation System

- **Character Animations**: Appear, smile, walk, hug, celebrate
- **Asset Animations**: Food/object appear, memory transitions
- **Feedback Animations**: Shake (error), pulse (success)
- **Scene Transitions**: Smooth fade-in/out between scenes

### ✅ Responsive Design

- Works on desktop (1200px+)
- Works on tablet (768px+)
- Works on mobile (320px+)
- Touch-friendly button sizes
- Accessible color schemes

## File Structure

```
frontend/
├── index.html              # Main HTML structure
├── style.css              # Comprehensive styling
├── app.js                 # Main game logic (700+ lines)
├── config.js              # Backend URL & configuration
├── animation-manager.js   # Animation orchestration
├── frontend_server.py     # Simple HTTP server
├── README.md              # This file
└── assets/                # (Optional) Local asset images
    ├── characters/
    │   ├── daughter_anu.png
    │   ├── son_rahul.png
    │   └── mother_lakshmi.png
    ├── environments/
    │   ├── family_house_front.png
    │   ├── family_kitchen.png
    │   └── family_temple.png
    ├── food/
    │   ├── chapathi.png
    │   ├── rice.png
    │   └── banana.png
    └── memories/
        ├── anu_cooking_with_lakshmi.png
        └── family_meal.png
```

## Getting Started

### Prerequisites

- Backend running on `http://localhost:8000`
  ```bash
  cd backend
  python -m main
  ```
- Python 3.x (for frontend server)
- Modern web browser

### 1. Start Backend

```bash
cd c:\Users\DELL\Downloads\Cognitiveai
python -m backend.main
```

You should see:
```
✅ Cognitive AI Game Backend
API Documentation: http://localhost:8000/docs
Health: http://localhost:8000/health
```

### 2. Start Frontend Server

```bash
cd frontend
python frontend_server.py
```

You should see:
```
✅ Frontend server running at http://localhost:8080
📁 Serving from: ...
🎮 Open http://localhost:8080 in your browser
```

### 3. Open in Browser

Visit: **http://localhost:8080**

You should see:
- Loading screen (fetching blueprint)
- Game loads with first scene
- "A Familiar Home" intro scene
- Patient can interact with buttons

## Configuration

Edit `config.js` to customize:

```javascript
CONFIG = {
    BACKEND_URL: 'http://localhost:8000',      // Backend URL
    
    PATIENT: {
        id: 'Patient_001_Lakshmi',              // Patient ID
        name: 'Lakshmi',                        // Patient name
        age: 75,
    },
    
    GAME: {
        goal: 'Help Lakshmi remember her daughter Anu',
        maxRetries: 3,
        enableDebug: true,                      // Console logging
    },
    
    ASSETS: {
        base: './assets/',                      // Asset folder path
        characters: './assets/characters/',
        environments: './assets/environments/',
        // ... other paths
    },
    
    TIMING: {
        sceneTransition: 600,                   // Transition duration (ms)
        animationDuration: 1000,                // Animation duration (ms)
        feedbackDuration: 3000,                 // Feedback display (ms)
        buttonCooldown: 500,                    // Button click cooldown (ms)
    }
};
```

## Data Flow

### Game Creation

```
Frontend
  ├─ User loads page
  ├─ app.js initializes
  ├─ POST /game/create
  │   {
  │     "patient_id": "Patient_001_Lakshmi",
  │     "goal": "Help Lakshmi remember her daughter Anu"
  │   }
  └─ Receives GameBlueprint
       {
         "blueprint_id": "bp_story_...",
         "scenes": [
           {
             "scene_id": "scene_0_welcome",
             "scene_type": "narrative",
             "narration": "Good morning, Lakshmi!",
             "environment": "family_house_front",
             "characters": ["mother_lakshmi"],
             "options": [...],
             "action_map": {...}
           },
           ... 7 more scenes ...
         ]
       }
```

### Scene Rendering

```
Blueprint Scene
  ├─ Set background image
  ├─ Render characters
  ├─ Render memory assets
  ├─ Display narration text
  ├─ Show question (if applicable)
  ├─ Show options as buttons
  └─ Play initial animation

Patient Interaction
  ├─ Patient clicks option button
  ├─ Frontend looks up action_map[option_id]
  ├─ Animation plays (e.g., "daughter_recognition_success")
  ├─ POST /game/action with outcome
  └─ Move to next scene
```

### Outcome Recording

```
When patient selects option:
  POST /game/action
  {
    "patient_id": "Patient_001_Lakshmi",
    "game_id": "game_story_...",
    "scene_id": "scene_2_kitchen",
    "option_id": "person_anu",
    "is_correct": true,
    "timestamp": "2024-01-01T12:00:00Z"
  }

Backend processes outcome:
  ├─ Record in _outcomes storage
  ├─ Update cognitive profile
  ├─ Return ActionResponse
  │   {
  │     "action_id": "daughter_recognition_success",
  │     "is_correct": true,
  │     "hint_level": 0,
  │     "duration": 8.0
  │   }
```

## Animation Sequences

Supported animations (in `animation-manager.js`):

### Correct Answer Animations
- `daughter_recognition_success`: Daughter appears → smiles → walks → hugs → celebrates
- `food_recognition_success`: Food shakes → celebrates
- `family_recognition_success`: Multiple family members appear and celebrate

### Wrong Answer Animations
- `wrong_answer_encouragement`: Narration box shakes gently
- `show_memory_cue`: Memory asset appears to help
- `gentle_continue_to_kitchen`: Fade transition

### Transition Animations
- `house_intro`: Background slides in
- `enter_kitchen`: Scene environment appears
- `positive_feedback`: Positive reinforcement animation
- `final_reward`: Multiple characters celebrate

## Scene Types

### 1. Narrative Scenes
- No question, just story setup
- Options are "Continue" buttons
- Shows environment + characters + narration

### 2. Recall Question Scenes
- Question with multiple-choice answers
- Options are answer choices
- Backend validates correctness
- Different animations for correct vs. wrong

### 3. Reward Scenes
- Celebration and positive reinforcement
- "Continue" button to next scene
- Happy animations

## Debugging

### Enable Debug Logging

```javascript
// In config.js
CONFIG.GAME.enableDebug = true;
```

Check browser console (F12) for:
- Blueprint loading
- Scene rendering
- Animation sequencing
- Outcome recording
- API calls

### Common Issues

**"Cannot connect to backend"**
- Ensure backend is running: `python -m backend.main`
- Check URL in `config.js` matches backend URL
- Check CORS is enabled (should be in FastAPI backend)

**Images not loading**
- Place images in `frontend/assets/` folder
- Filename should match asset ID + `.png`
- Check browser console for 404 errors

**Buttons not working**
- Check browser console for JavaScript errors
- Ensure `config.js` is loaded
- Try clearing browser cache (Ctrl+Shift+Delete)

**Animations not playing**
- Open DevTools → Animation Inspector
- Verify CSS animations are defined in `style.css`
- Check `animation-manager.js` for action definitions

## Customization

### Adding New Characters

1. Add character image to `frontend/assets/characters/`
   - Filename: `{character_name}.png`
2. Character will auto-load in any scene that includes it
3. Add animation styles to `style.css`

### Adding New Animations

1. Define animation in `style.css`:
   ```css
   @keyframes my-animation {
       from { transform: translateX(0); }
       to { transform: translateX(100px); }
   }
   
   .character.my-animation {
       animation-name: my-animation;
   }
   ```

2. Add action handler in `animation-manager.js`:
   ```javascript
   'my_action_id': async () => {
       await this.play('element-id', 'my-animation', 1000);
   }
   ```

### Styling Customization

Edit `style.css` to change:
- Colors: `:root` variables
- Fonts: `body` font-family
- Layout: Flexbox/grid settings
- Animations: Keyframe definitions
- Responsive breakpoints: Media queries

## Performance

- **Blueprint Loading**: ~4.5ms (backend)
- **Scene Rendering**: ~100ms (frontend)
- **Animation Duration**: 1-8 seconds (configurable)
- **Outcome Recording**: <100ms (async)

### Optimization Tips

1. **Preload Images**:
   ```javascript
   // In app.js, preload all character images
   const images = new Image();
   images.src = getAssetUrl('daughter_anu', 'characters');
   ```

2. **Cache Blueprints**:
   ```javascript
   // Backend caches by patient + goal
   // Frontend stores in sessionStorage
   ```

3. **Reduce Animation Duration** (for faster testing):
   ```javascript
   CONFIG.TIMING.animationDuration = 300;
   ```

## Browser Support

- ✅ Chrome/Edge 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Mobile browsers (iOS Safari, Chrome Mobile)

## API Integration

### Required Backend Endpoints

1. **POST /game/create**
   - Input: `{ patient_id, goal }`
   - Output: `GameBlueprint` (with scenes)

2. **POST /game/action**
   - Input: `{ patient_id, game_id, scene_id, option_id, is_correct }`
   - Output: `ActionResponse`

3. **GET /outcome/patient/{patient_id}/profile**
   - Output: `CognitiveProfileResponse`

See `backend/API_DOCUMENTATION.md` for details.

## Next Steps

### Phase 1 (Current): Web Prototype ✅
- HTML/CSS/JS frontend
- Connect to backend
- Basic animations
- Results tracking

### Phase 2: Add Real Assets
- Place patient images in `frontend/assets/`
- Create 5-10 animation sequences
- Test with actual patient photos

### Phase 3: Unity Migration
- Export blueprint logic to C#
- Reimplement UI in Unity
- Add 3D animations/effects
- Deploy to VR headset (if available)

### Phase 4: Advanced Features
- Multi-patient administration
- Caregiver dashboard
- Detailed cognitive analytics
- Mobile app (React Native)

## Resources

- [Frontend Code Overview](./README_CODE.md) (internal documentation)
- [Backend API Docs](../API_DOCUMENTATION.md)
- [System Architecture](../ARCHITECTURE.md)
- [AI Agents Implementation](../AI_AGENTS_COMPLETION.md)

## Support

For issues or questions:
1. Check browser console (F12) for errors
2. Enable debug logging in `config.js`
3. Review logs in backend terminal
4. Check `API_DOCUMENTATION.md` for endpoint details

## License

Part of Cognitive AI Memory Game Platform
