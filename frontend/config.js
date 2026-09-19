/* ========================================================================== */
/* Configuration - Backend URL and Patient Info                              */
/* ========================================================================== */

const CONFIG = {
    // Backend API URL
    BACKEND_URL: 'https://cognitive-ai-q1ib.onrender.com',

    ASSET_ALIASES: {
        mother_lakshmi: 'patient_lakshmi',
        patient_lakshmi: 'patient_lakshmi',
    },
    
    // Patient Configuration
    PATIENT: {
        id: 'Patient_001_Lakshmi',
        name: 'Lakshmi',
        age: 75,
    },
    
    // Game Configuration
    GAME: {
        goal: 'Help Lakshmi remember her daughter Anu',
        maxRetries: 3,
        enableDebug: true,
    },
    
    // Asset Base Paths
    ASSETS: {
        base: './assets/',
        characters: './assets/characters/',
        environments: './assets/environments/',
        food: './assets/food/',
        memories: './assets/memories/',
        animations: './assets/animations/',
    },
    
    // Fallback Image (if asset not found)
    FALLBACK_IMAGE: 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="200" height="200"%3E%3Crect fill="%23ccc" width="200" height="200"/%3E%3Ctext x="100" y="100" text-anchor="middle" dy=".3em" font-size="16" fill="%23999"%3EImage Not Found%3C/text%3E%3C/svg%3E',
    
    // API Endpoints
    ENDPOINTS: {
        createGame: '/game/create',
        getScene: '/game/scene',
        recordAction: '/game/action',
        recordOutcome: '/outcome/record',
        getCognitiveProfile: '/outcome/patient/{patient_id}/profile',
    },
    
    // Timing
    TIMING: {
        sceneTransition: 600,
        animationDuration: 1000,
        feedbackDuration: 3000,
        buttonCooldown: 500,
    }
};

// Helper function to build asset URL candidates
function getAssetCandidates(assetId, type = 'characters') {
    const paths = {
        characters: 'characters/',
        environments: 'environments/',
        food: 'food/',
        memories: 'memories/',
        animations: 'animations/',
    };

    const alias = CONFIG.ASSET_ALIASES?.[assetId] || assetId;
    const path = paths[type] || paths.characters;
    const base = `${CONFIG.ASSETS.base}${path}${alias}`;
    const extensions = ['png', 'jpg', 'jpeg', 'svg'];

    return extensions.map(ext => `${base}.${ext}`);
}

function getAssetUrl(assetId, type = 'characters') {
    return getAssetCandidates(assetId, type)[0];
}

function setImageWithFallback(imgElement, assetId, type = 'characters') {
    const candidates = getAssetCandidates(assetId, type);
    let index = 0;

    const tryNext = () => {
        if (index >= candidates.length) {
            imgElement.src = CONFIG.FALLBACK_IMAGE;
            return;
        }

        imgElement.src = candidates[index];
        index += 1;
    };

    imgElement.onerror = tryNext;
    tryNext();
}

// Helper function to build API URL
function getApiUrl(endpoint, params = {}) {
    let url = CONFIG.BACKEND_URL + endpoint;
    
    // Replace path parameters
    for (const [key, value] of Object.entries(params)) {
        url = url.replace(`{${key}}`, value);
    }
    
    return url;
}
