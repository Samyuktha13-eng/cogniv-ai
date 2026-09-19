const PATIENT_ASSET = '/patient-assets/';

const TELUGU_SPEECH = {
    WELCOME: ['హాయ్ లక్ష్మీ గారు... ఎలా ఉన్నారు?', 'లక్ష్మీ గారు... బాగున్నారా?', 'చాలా బాగుంది లక్ష్మీ గారు!'],
    ASK_PERMISSION: ['లక్ష్మీ గారు... నేను ఇవాళ మీతో ఒక చిన్న గేమ్ ఆడుతాను. మీకు ఇష్టమేనా?', 'లక్ష్మీ గారు... మనం కలిసి ఆడుదామా?', 'చాలా బాగుంది! మనం మెల్లగా, కలిసి ఆడుదాం.'],
    ASK_NAME: ['ముందుగా... మీ పేరు చెప్పండి.', 'మీ పేరు ఏమిటి?', 'అవును... లక్ష్మీ గారు. చాలా బాగుంది.'],
    HOME_RECALL: ['లక్ష్మీ గారు... ఇప్పుడు మనం ఒక మెమరీ జర్నీకి వెళ్దాం. నేను మీకు మీతో ఉన్న జ్ఞాపకాలు చూపిస్తాను. మీరు చూసిన తరువాత... మీకు గుర్తొచ్చింది నాతో చెప్పండి. రెడీ ఆ?', 'లక్ష్మీ గారు... మీరు ఏమి చూస్తున్నారు?', 'అవును లక్ష్మీ గారు... ఇది మీ ఇల్లు. చాలా బాగా గుర్తుపెట్టుకున్నారు.'],
    PHOTO_RECALL: ['ఓహ్... మీకు ఫోటో ఫ్రేమ్స్ కనిపిస్తున్నాయా?', 'అక్కడ ఎవరి ఫోటోలు ఉన్నాయో... గుర్తొస్తుందా?', 'అవునా! చాలా బాగుంది లక్ష్మీ గారు. మీ పాపతో ఉన్న ఒక మెమరీ చూద్దాం.'],
    CHAPATHI_RECALL: ['అయితే మీ పాపతో ఉన్న ఒక మెమరీ చూద్దాం.', 'లక్ష్మీ గారు... అక్కడ మీరు ఏమి చేస్తున్నారు?', 'అవును... మీరు చపాతీ చేస్తున్నారు.'],
    ANU_RECALL: ['లక్ష్మీ గారు... ఈ అమ్మాయిని చూస్తున్నారా? ఎవరు అని గుర్తొస్తుందా?', 'ఈ అమ్మాయి పేరు గుర్తుందా?', 'అవును! అనూ. మీ పాప అనూ. చాలా బాగా గుర్తుపెట్టుకున్నారు.'],
    TEMPLE_RECALL: ['ఇప్పుడు మీకు ఇంకొక బ్యూటిఫుల్ మెమరీ చూపిస్తాను.', 'లక్ష్మీ గారు... ఇక్కడ మీరు ఎక్కడికి వచ్చారు?', 'అవును! టెంపుల్‌కి వచ్చారు. చాలా బాగుంది.'],
    MEMORY_CONNECTION: ['లక్ష్మీ గారు... మీరు మీ పాపతో చాలా మెమరీస్ క్రియేట్ చేసుకున్నారు. మీ ఇల్లు... మీ ఫోటో ఫ్రేమ్స్... చపాతీ చేస్తూ... పిండితో ఆడుకుంటూ... టెంపుల్‌కి వెళ్తూ... మీ పాప అనూతో.', 'మీకు మీ పాప పేరు గుర్తుందా?', 'అవును... అనూ. మీ పాప అనూ.'],
    COMPLETE: ['చాలా బాగా గుర్తుపెట్టుకున్నారు, లక్ష్మీ గారు. ఇవాళ చాలా బాగా ఆడారు. మీ మెమరీస్‌తో మనం కలిసి ఒక బ్యూటిఫుల్ జర్నీ చేశాం. థాంక్యూ లక్ష్మీ గారు.']
};

const ENGLISH_SPEECH = {
    WELCOME: ['Hi Lakshmi garu... how are you?', 'Lakshmi garu... are you feeling well?', 'That is wonderful, Lakshmi garu!'],
    ASK_PERMISSION: ['Lakshmi garu... today we will spend a little time together. Would you like to play?', 'Would you like to play with me?', 'That is lovely! We will take it slowly and do it together.'],
    ASK_NAME: ['First... please tell me your name.', 'What is your name?', 'Yes... Lakshmi garu. Very good.'],
    HOME_RECALL: ["Lakshmi garu... now we are going on a little memory journey. I will show you memories from your life. After you look... tell me whatever comes to your mind. Are you ready?", 'Lakshmi garu... what do you see here?', 'Yes, Lakshmi garu... this is your home. You remembered that beautifully.'],
    HOME_OWNERSHIP: ['Now... let us look a little closer at this familiar home.', 'Whose home is this?', 'Yes, Lakshmi garu... this is your home.'],
    HOME_ENTRY: ['Shall we go inside and look around?', 'Shall we go inside and look around?', 'Okay... let us go inside.'],
    PHOTO_OBSERVATION: ['Come, Lakshmi garu... let us look inside your home.', 'Take a look around...', 'What do you notice here?'],
    PHOTO_RECALL: ['Do you see the photographs?', 'Do you see the photographs?', 'Yes... those are your family photographs.'],
    PHOTO_FAMILIARITY: ['Lakshmi garu... do any of these people look familiar to you?', 'Do any of these people look familiar to you?', 'Yes... someone very special to you.'],
    FAMILY_RECALL: ['Lakshmi garu... look at this.', 'Who is sitting here?', 'Yes... that is you. You look very comfortable here.'],
    CHAPATHI_RECALL: ['Now... look at this memory.', 'What are you doing here?', 'Yes... you are making chapathi.'],
    CHAPATHI_DAUGHTER: ['And Lakshmi garu... look beside you.', 'Is someone there with you?', 'Yes... she is someone very special to you.'],
    ANU_RECALL: ['Lakshmi garu... look at this woman.', 'Does she look familiar to you?', 'Yes! Anu. She is your daughter.'],
    DEEPER_CHAPATHI: ['Let us look at that warm kitchen memory once more.', 'What are you doing with your daughter here?', 'Yes... you are making chapathi together.'],
    NAME_RECALL: ['Lakshmi garu... think of that beautiful kitchen memory.', 'Do you remember your daughter\'s name?', 'Yes! Anu. Your daughter\'s name is Anu.'],
    TEMPLE_RECALL: ['I have another beautiful memory to show you.', 'Lakshmi garu... where did you come here?', 'Yes! You came to the temple. That is lovely.'],
    KRISHNA: ['Look carefully inside the temple memory.', 'Who did you see inside the temple?', 'Yes... Krishna. That is a beautiful memory.'],
    MEMORY_CONNECTION: ['Lakshmi garu... you and your daughter made many beautiful memories together. Your home... your family photos... making chapathi... playing with flour... going to the temple... with your daughter Anu.', 'Do you remember your daughter\'s name?', 'Yes... Anu. Your daughter Anu.'],
    FINAL_ANU: ['Lakshmi garu... look at this woman. She is someone very special.', 'Do you remember her name?', 'Yes... Anu. Your daughter Anu.'],
    ANU_ARRIVAL: ['Lakshmi garu... I think someone special has come to meet you. Look... someone has come to see you.', 'Do you recognize this woman?', 'Yes, Lakshmi garu... Anu. Your daughter Anu.'],
    COMPLETE: ['You remembered so many beautiful moments today, Lakshmi garu. We went on a beautiful journey through your memories. Thank you for sharing them with me.']
};

const JOURNEY = [
    { state: 'WELCOME', label: 'Welcome', title: 'Namaskaram Lakshmi garu!', speech: 'Hi Lakshmi garu... ala unnaru?', question: 'Lakshmi garu... are you feeling well?', answers: ['bagunnanu', 'baagaunnanu', 'fine', 'good', 'yes', 'well', 'feeling well', 'i am well', 'i am fine', 'doing well'], response: 'That is wonderful, Lakshmi garu!' },
    { state: 'ASK_PERMISSION', label: 'A gentle beginning', title: 'Shall we spend a little time together?', speech: 'Lakshmi garu... nenu ivala meetho oka chinna game aaduthanu. Meeku istamena?', question: 'Would you like to play with me?', answers: ['yes', 'avunu', 'sare', 'okay', 'ishtam'], response: 'That is lovely. We will take it slowly and do it together.' },
    { state: 'ASK_NAME', label: 'Your name', title: 'Let us begin with your name', speech: 'Munduga... mee peru cheppandi.', question: 'What is your name?', answers: ['lakshmi'], response: 'Yes... Lakshmi garu. Very good.' },
    { state: 'HOME_RECALL', label: 'Home', title: "A place close to your heart", video: 'memory_01_home.mp4', speech: 'Lakshmi garu... ippudu manam oka memory journey ki veldham. Nenu meeku me tho unna gyapakalu chupisthanu. Meeru chusina tarvatha... meeku gurthochindhi naatho cheppandi. Ready aa?', question: 'Lakshmi garu... what do you see here?', answers: ['home', 'house', 'illu', 'illlu', 'naa illu', 'na illu'], response: 'Yes, Lakshmi garu... this is your home.' },
    { state: 'HOME_OWNERSHIP', label: 'Home', title: 'A place close to your heart', video: 'memory_01_home.mp4', question: 'Lakshmi garu... does this place look familiar to you?', answers: ['home', 'house', 'my house', 'my home', 'our house', 'naa illu', 'na illu'], response: 'Yes, Lakshmi garu... this is your home.' },
    { state: 'HOME_ENTRY', label: 'Going inside', title: 'Let us go inside your home', video: 'memory_01_home.mp4', question: 'Shall we go inside and look around?', answers: ['yes', 'okay', 'sure', 'lets go', 'let us go', 'avunu', 'sare'], response: 'Okay... let us go inside.', voiceLines: ['Shall we go inside and look around?'] },
    { state: 'PHOTO_OBSERVATION', label: 'Inside the house', title: 'Look around your home', video: 'memory_02_anu.mp4', question: 'What do you notice here?', openObservation: true, response: 'Yes... take a good look.', voiceLines: ['Come, Lakshmi garu... let us look inside your home.', 'Take a look around...', 'What do you notice here?'] },
    { state: 'PHOTO_RECALL', label: 'Family photos', title: 'Notice the photographs', video: 'memory_02_anu.mp4', question: 'Do you see the photographs?', answers: ['yes', 'photo', 'photos', 'pictures', 'frames', 'family', 'people', 'living room', 'my family', 'avunu'], response: 'Yes... those are your family photographs.', voiceLines: ['Do you see the photographs?'] },
    { state: 'PHOTO_FAMILIARITY', label: 'Family photos', title: 'People you know', video: 'memory_02_anu.mp4', question: 'Do any of these people look familiar to you?', answers: ['anu', 'daughter', 'family', 'papa', 'my daughter'], response: 'Yes... someone very special to you.' },
    { state: 'FAMILY_RECALL', label: 'Family', title: 'A family moment', image: 'home/living_room.jpg', question: 'Who is sitting here?', answers: ['me', 'myself', 'nene', 'lakshmi'], response: 'Yes... that is you sitting there. You look very comfortable here.' },
    { state: 'CHAPATHI_RECALL', label: 'Chapathi', title: 'A warm kitchen memory', video: 'memory_03_chapathi.mp4', question: 'Lakshmi garu... what are you doing here?', answers: ['chapathi', 'chapati', 'roti', 'pindi'], response: 'Yes... you are making chapathi.' },
    { state: 'CHAPATHI_DAUGHTER', label: 'Together', title: 'A special kitchen memory', video: 'memory_03_chapathi.mp4', speech: 'And Miss Lakshmi... look beside you. Is someone there with you?', question: 'Is someone there with you?', answers: ['yes', 'daughter', 'anu', 'papa', 'someone'], response: 'Yes... she is someone very special to you.' },
    { state: 'ANU_RECALL', label: 'Anu', title: 'Someone very special', image: 'elder anu.jpg', question: 'Do you recognize this woman?', answers: ['anu', 'daughter', 'papa', 'my daughter'], response: 'Yes! Anu. Your daughter Anu.' },
    { state: 'DEEPER_CHAPATHI', label: 'A deeper memory', title: 'Making chapathi together', video: 'memory_03_chapathi.mp4', question: 'What are you doing with your daughter here?', answers: ['chapathi', 'chapati', 'roti', 'pindi', 'playing'], response: 'Yes... you are making chapathi together.' },
    { state: 'PERSONAL_MEMORY', label: 'A personal memory', title: 'A memory of your own', video: 'memory_03_chapathi.mp4', question: 'Do you remember anything else you used to do together?', openObservation: true, response: 'Aww... yes, Lakshmi garu. That sounds like a very happy memory.', voiceLines: ['Lakshmi garu... look at this memory again.', 'Do you remember anything else you used to do together?'] },
    { state: 'NAME_RECALL', label: 'Her name', title: 'A name close to your heart', image: 'elder anu.jpg', question: 'Do you remember your daughter\'s name?', answers: ['anu', 'daughter', 'papa'], response: 'Yes! Anu. Your daughter\'s name is Anu.' },
    { state: 'TEMPLE_RECALL', label: 'Temple', title: 'A peaceful temple memory', video: 'memory_04_temple.mp4', question: 'Where did you come here?', answers: ['temple', 'gudi', 'devalayam'], response: 'Yes! You came to the temple.' },
    { state: 'KRISHNA', label: 'Temple memory', title: 'A peaceful moment inside', video: 'memory_04_temple.mp4', question: 'Who did you see inside the temple?', answers: ['krishna', 'krishnudu'], response: 'Yes... Krishna.' },
    { state: 'TEMPLE_COMPANION', label: 'Together', title: 'A family temple memory', video: 'memory_04_temple.mp4', question: 'And who came with you?', answers: ['anu', 'daughter', 'papa', 'family'], response: 'Yes... Anu came with you.' },
    { state: 'MEMORY_CONNECTION', label: 'Together', title: 'The memories you made together', image: 'memories/anu_lakshmi_temple.jpg', speech: 'Miss Lakshmi... look at these memories. Your home... your family photographs... making chapathi together... spending time together... going to the temple... and Anu. You and Anu shared many beautiful moments together. These are your memories.', question: null },
    { state: 'FINAL_ANU', label: 'Anu', title: 'Someone very special', image: 'elder anu.jpg', question: 'Do you remember her name?', answers: ['anu', 'daughter', 'papa'], response: 'Yes... Anu. Your daughter Anu.' },
    { state: 'ANU_ARRIVAL', label: 'A special visit', title: 'Someone has come to see you', image: 'elder anu.jpg', question: 'Do you recognize this woman?', answers: ['anu', 'daughter', 'papa'], response: 'Yes, Lakshmi garu... Anu. Your daughter Anu.' },
    { state: 'COMPLETE', label: 'Beautiful memories', title: 'Thank you, Lakshmi garu.', image: 'elder anu.jpg', speech: 'Chaala baaga gurthupettukunnaru, Lakshmi garu. Lakshmi garu... ivala chaala baaga aadaru. Mee memories tho manam kalisi oka beautiful journey chesam. Thank you Lakshmi garu.', question: null }
];

class MemoryJourney {
    constructor() {
        this.index = 0;
        this.scenes = [];
        this.recognition = null;
        this.listening = false;
        this.busy = false;
        this.moments = [];
        this.music = document.getElementById('background-music');
        this.voiceUnlocked = false;
        this.voiceUnlocking = false;
        this.recognitionRetried = false;
        this.entryTimer = null;
    }

    async init() {
        try {
            await this.loadScenes();
            this.setupRecognition();
            document.getElementById('mic-button').addEventListener('click', () => this.toggleListening());
            document.getElementById('send-typed-answer').addEventListener('click', () => this.submitTypedAnswer());
            document.getElementById('typed-answer').addEventListener('keydown', event => { if (event.key === 'Enter') this.submitTypedAnswer(); });
            document.getElementById('replay-button').addEventListener('click', () => location.reload());
            document.getElementById('voice-button')?.addEventListener('click', () => this.unlockVoice());
            document.addEventListener('pointerdown', () => this.unlockVoice(), { once: true });
            this.showScreen('conversation-screen');
            await this.transitionTo(0, true);
        } catch (error) {
            console.error(error);
            this.showError(error.message);
        }
    }

    async loadScenes() {
        const response = await fetch(`${CONFIG.BACKEND_URL}/video/story/lakshmi-anu?limit=4`);
        if (!response.ok) throw new Error('The memory album is taking a small pause.');
        const payload = await response.json();
        this.scenes = Array.isArray(payload.scenes) ? payload.scenes : [];
        if (!this.scenes.length) throw new Error('No memories are available right now.');
    }

    setupRecognition() {
        const Recognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (!Recognition) return;
        this.recognition = new Recognition();
        this.recognition.continuous = false;
        this.recognition.interimResults = false;
        this.recognition.maxAlternatives = 1;
        this.recognition.lang = 'en-IN';
        this.recognition.onstart = () => { this.listening = true; this.setListeningState('listening'); };
        this.recognition.onresult = event => this.handleTranscript(event.results[0][0].transcript);
        this.recognition.onnomatch = () => { this.listening = false; this.setListeningState('fallback'); this.showFallback('nomatch'); };
        this.recognition.onerror = event => { console.warn('Speech recognition:', event.error); this.listening = false; if (event.error === 'network' && !this.recognitionRetried) { this.recognitionRetried = true; this.recognition.lang = 'en-US'; this.setListeningState('fallback'); document.getElementById('listening-status').textContent = 'Trying the English speech service...'; window.setTimeout(() => this.startRecognition(), 300); return; } this.setListeningState('fallback'); this.showFallback(event.error); };
        this.recognition.onend = () => { this.listening = false; if (!this.busy && !this.recognitionRetried) this.setListeningState('ready'); this.restoreMusic(); };
    }

    async transitionTo(index, first = false) {
        if (index >= JOURNEY.length) return this.complete();
        window.clearTimeout(this.entryTimer);
        this.index = index;
        const stage = JOURNEY[index];
        const apiScene = this.scenes[Math.min(Math.max(index - 3, 0), this.scenes.length - 1)] || {};
        this.busy = false;
        window.scrollTo({ top: 0, behavior: 'smooth' });
        document.getElementById('stage-label').textContent = stage.label;
        document.getElementById('stage-title').textContent = this.addressUser(stage.title);
        document.getElementById('stage-count').textContent = index < 2 ? 'A gentle beginning' : `Memory ${index - 1} of ${JOURNEY.length - 2}`;
        document.getElementById('assistant-text').textContent = this.addressUser(this.getVoiceLines(stage)[0] || apiScene.narration || '');
        const mediaFrame = document.getElementById('media-frame');
        mediaFrame.classList.remove('scene-transition');
        void mediaFrame.offsetWidth;
        mediaFrame.classList.add('scene-transition');
        window.setTimeout(() => mediaFrame.classList.remove('scene-transition'), 650);
        this.renderMedia(stage, apiScene);
        this.renderConversation(stage);
        this.updateMemoryIndicator();
            if (this.voiceUnlocked) { this.setMicEnabled(false); await this.speakSequence(this.getVoiceLines(stage)); this.setMicEnabled(Boolean(stage.question)); }
        else document.getElementById('audio-status').textContent = 'Tap Start voice';
        if (stage.state === 'HOME_ENTRY') this.entryTimer = window.setTimeout(() => { if (this.index === index && !this.busy) this.handleTranscript('telidhu'); }, 8000);
        if (!stage.question && stage.state !== 'COMPLETE' && this.voiceUnlocked) window.setTimeout(() => this.transitionTo(this.index + 1), 1300);
            if (stage.state === 'COMPLETE') { this.showScreen('results-screen'); return; }
    }

    renderMedia(stage, apiScene) {
        const video = document.getElementById('memory-video');
        const image = document.getElementById('memory-image');
        const placeholder = document.getElementById('media-placeholder');
        video.hidden = true; image.hidden = true; placeholder.hidden = true;
        if (stage.video) {
            video.hidden = false; video.src = `${CONFIG.BACKEND_URL}/videos/${stage.video}`; video.load();
            video.play().catch(() => {});
            video.onerror = () => this.showMissingMedia(`Missing video: ${stage.video}`);
        } else if (stage.image) {
            image.hidden = false; image.src = PATIENT_ASSET + encodeURI(stage.image); image.onerror = () => this.showMissingMedia(`Missing image: ${stage.image}`);
        } else if (apiScene.video) {
            video.hidden = false; video.src = `${CONFIG.BACKEND_URL}${apiScene.video}`; video.load(); video.play().catch(() => {});
        } else this.showMissingMedia('No media configured for this memory.');
    }

    getVoiceLines(stage) {
        if (stage.voiceLines) return stage.voiceLines;
        const lines = (ENGLISH_SPEECH[stage.state] || [stage.speech]).filter(Boolean);
        return stage.question ? lines.slice(0, 2) : lines;
    }

    showMissingMedia(message) { console.warn(message); document.getElementById('memory-video').hidden = true; document.getElementById('memory-image').hidden = true; document.getElementById('media-placeholder').hidden = false; document.getElementById('media-placeholder-text').textContent = 'This beautiful memory is resting for a moment.'; }

    renderConversation(stage) {
        const question = document.getElementById('question-card');
        const fallback = document.getElementById('fallback-actions');
        document.getElementById('question-text').textContent = this.addressUser(stage.question || ENGLISH_SPEECH[stage.state]?.[1] || 'Let us keep this memory close.');
        question.hidden = !stage.question;
        fallback.hidden = true; fallback.innerHTML = '';
        document.getElementById('text-fallback').hidden = true;
        document.getElementById('transcript').textContent = '';
        this.setListeningState('ready');
        document.getElementById('conversation-feedback').hidden = true;
        if (stage.question) this.showFallback();
    }

    showFallback(error = '') {
        const fallback = document.getElementById('fallback-actions');
        document.getElementById('text-fallback').hidden = Boolean(error) === false;
        if (!JOURNEY[this.index].question) return;
        if (error === 'network') document.getElementById('listening-status').textContent = 'Speech service is unavailable. You can type your answer below.';
        if (error === 'nomatch') document.getElementById('listening-status').textContent = 'I did not quite hear that. Please speak once more, or type your answer below.';
        if (error === 'not-allowed' || error === 'service-not-allowed') document.getElementById('listening-status').textContent = 'Please allow microphone access, then tap Speak Answer again.';
        const fallbackByState = {
            WELCOME: [['good', '🙂 I am fine'], ['telidhu', '🤔 I am not sure']],
            ASK_PERMISSION: [['yes', '🌸 Yes, let us'], ['telidhu', '🤔 Not sure']],
            ASK_NAME: [['lakshmi', '👩 Lakshmi'], ['telidhu', '🤔 I forgot']],
            HOME_RECALL: [['home', '🏠 Home'], ['telidhu', '🤔 I am not sure']],
            HOME_OWNERSHIP: [['home', '🏠 My home'], ['telidhu', '🤔 I am not sure']],
            HOME_ENTRY: [['yes', '🚪 Yes, let us go inside'], ['telidhu', '🤔 Take a little look together']],
            PHOTO_OBSERVATION: [['photos', '🖼️ Photos'], ['family', '👨‍👩‍👧 Family'], ['telidhu', '🤔 I am not sure']],
            PHOTO_RECALL: [['yes', '🖼️ Yes, photographs'], ['telidhu', '🤔 I am not sure']],
            PHOTO_FAMILIARITY: [['daughter', '👩 My daughter'], ['family', '👨‍👩‍👧 My family'], ['telidhu', '🤔 I am not sure']],
            FAMILY_RECALL: [['me', '🙂 Me'], ['telidhu', '🤔 I am not sure']],
            CHAPATHI_RECALL: [['chapathi', '🍽️ Chapathi'], ['telidhu', '🤔 I am not sure']],
            CHAPATHI_DAUGHTER: [['daughter', '👩 Someone special'], ['telidhu', '🤔 I am not sure']],
            ANU_RECALL: [['anu', '👩 Anu'], ['telidhu', '🤔 I am not sure']],
            DEEPER_CHAPATHI: [['chapathi', '🍽️ Making chapathi'], ['telidhu', '🤔 I am not sure']],
            PERSONAL_MEMORY: [['play', '🙂 We played together'], ['flour', '🫓 We played with flour'], ['telidhu', '🤔 I am not sure']],
            NAME_RECALL: [['anu', '👩 Anu'], ['telidhu', '🤔 I am not sure']],
            TEMPLE_RECALL: [['temple', '🛕 Temple'], ['telidhu', '🤔 I am not sure']],
            KRISHNA: [['krishna', '🛕 Krishna'], ['telidhu', '🤔 I am not sure']],
            TEMPLE_COMPANION: [['anu', '👩 Anu'], ['family', '👨‍👩‍👧 Family'], ['telidhu', '🤔 I am not sure']],
            MEMORY_CONNECTION: [['anu', '👩 Anu'], ['telidhu', '🤔 I am not sure']],
            FINAL_ANU: [['anu', '👩 Anu'], ['telidhu', '🤔 I am not sure']],
            ANU_ARRIVAL: [['anu', '👩 Anu'], ['telidhu', '🤔 I am not sure']]
        };
        const choices = fallbackByState[JOURNEY[this.index].state] || [['telidhu', '🤔 I am not sure']];
        fallback.hidden = false; fallback.innerHTML = choices.map(([answer, label]) => `<button type="button" data-answer="${answer}">${label}</button>`).join('');
        fallback.querySelectorAll('button').forEach(button => {
            button.onclick = () => this.handleTranscript(button.dataset.answer, true);
        });
    }

    async unlockVoice() {
        if (this.voiceUnlocking) return;
        this.voiceUnlocking = true;
        this.voiceUnlocked = true;
        const button = document.getElementById('voice-button');
        if (button) button.textContent = '🔊 Hear again';
        this.playBackgroundMusic();
        try {
            this.setMicEnabled(false);
            await this.speakSequence((ENGLISH_SPEECH[JOURNEY[this.index].state] || [JOURNEY[this.index].speech]).slice(0, 2));
            this.setMicEnabled(Boolean(JOURNEY[this.index].question));
        } finally {
            this.voiceUnlocking = false;
        }
    }

    async speakSequence(lines) {
        for (const line of lines.filter(Boolean)) {
            await this.speak(line);
            await this.wait(450);
        }
    }

    wait(milliseconds) {
        return new Promise(resolve => window.setTimeout(resolve, milliseconds));
    }

    submitTypedAnswer() {
        const input = document.getElementById('typed-answer');
        const answer = input.value.trim();
        if (answer) { input.value = ''; this.handleTranscript(answer); }
    }

    toggleListening() { if (window.speechSynthesis?.speaking) { document.getElementById('listening-status').textContent = 'Please wait until Meera finishes speaking.'; return; } if (!this.recognition) return this.showFallback(); if (this.listening) this.stopListening(); else this.startListening(); }
    setMicEnabled(enabled) { const button = document.getElementById('mic-button'); button.disabled = !enabled; button.setAttribute('aria-disabled', String(!enabled)); }
    async startListening() { this.playBackgroundMusic(); this.duckMusic(); this.setListeningState('listening'); this.recognitionRetried = false; try { if (navigator.mediaDevices?.getUserMedia) { const stream = await navigator.mediaDevices.getUserMedia({ audio: true }); stream.getTracks().forEach(track => track.stop()); } this.startRecognition(); } catch (error) { console.warn('Microphone permission failed', error); this.setListeningState('fallback'); this.showFallback('not-allowed'); } }
    startRecognition() { try { this.recognition.start(); } catch (error) { console.warn('Microphone is already opening', error); this.showFallback(); } }
    stopListening() { if (this.recognition && this.listening) this.recognition.stop(); }

    handleTranscript(transcript, fromButton = false) {
        if (this.busy) return;
        this.busy = true; this.stopListening();
        document.getElementById('transcript').textContent = `You said: “${transcript}”`;
        this.setListeningState('processing');
        const stage = JOURNEY[this.index];
        const intent = stage.openObservation ? 'observed' : this.classifyAnswer(transcript, stage.answers || []);
        const remembered = stage.openObservation || intent !== 'uncertain';
        if (!stage.openObservation && stage.state !== 'HOME_ENTRY') this.moments.push(remembered ? '❤️' : '🤔');
        this.updateMemoryIndicator();
        const response = remembered ? stage.response : (stage.state === 'HOME_ENTRY' ? 'That is alright... we can take a little look inside together.' : this.gentleUnknown(stage.state));
        this.showFeedback(response, remembered);
        if (!stage.openObservation && stage.state !== 'HOME_ENTRY') this.recordOutcome(transcript, intent, remembered, stage.state);
        const spokenResponse = remembered ? (ENGLISH_SPEECH[stage.state]?.[2] || response) : "That's okay, Miss Lakshmi... take your time. We can look at the memory together.";
        const nextIndex = this.index + 1;
        this.speak(spokenResponse).catch(() => {}).finally(() => window.setTimeout(() => {
            if (this.index === nextIndex - 1) this.transitionTo(nextIndex);
        }, 1600));
        window.setTimeout(() => {
            if (this.index === nextIndex - 1) this.transitionTo(nextIndex);
        }, fromButton ? 2200 : 3500);
    }

    addressUser(text) {
        return text.replaceAll('Lakshmi garu', 'Miss Lakshmi');
    }

    normalizeTranscript(value) { return value.toLowerCase().replace(/[.,!?]/g, ' ').replace(/\s+/g, ' ').trim(); }
    classifyAnswer(value, answers) {
        const text = this.normalizeTranscript(value);
        const uncertain = ['telidhu','teliyadu','gurthuku ledhu','gurthu ledu','naku gurthu ledu','naku gurthuku ledhu','dont know','i dont remember','not remember','forgot','cant remember'];
        if (uncertain.some(item => text.includes(item))) return 'uncertain';
        const aliases = { bagunnanu: ['bagaunannu', 'bagunanu', 'baagunnanu'], anu: ['anutho', 'anu kada'], home: ['naa illu', 'na illu'], chapathi: ['chapati', 'roti'] };
        const matches = answers.some(answer => text.includes(this.normalizeTranscript(answer)) || this.normalizeTranscript(answer).includes(text) || (aliases[answer] || []).some(alias => text.includes(alias)));
        return matches ? answers[0] : 'uncertain';
    }

    gentleUnknown(state) { if (state === 'HOME_RECALL') return 'That is okay, Miss Lakshmi... this is your home. Let us look at it together.'; if (state === 'ANU_RECALL') return 'That is okay, Miss Lakshmi... she is someone very special from your family.'; return 'That is okay, Miss Lakshmi... take your time. We can remember together.'; }
    showFeedback(message, remembered) { const box = document.getElementById('conversation-feedback'); box.hidden = false; box.className = `conversation-feedback ${remembered ? 'remembered' : 'uncertain'}`; box.textContent = `${remembered ? '❤️ ' : '🤔 '}${this.addressUser(message)}`; }
    setListeningState(state) { const button = document.getElementById('mic-button'); const status = document.getElementById('listening-status'); const states = { ready: ['🎙️', 'Speak Answer', 'Tap the microphone and speak naturally.'], listening: ['🎧', 'Listening...', 'Listening... please speak'], processing: ['◌', 'Processing...', 'I am listening carefully.'], fallback: ['🎙️', 'Speak Answer', 'Meeku cheppali anipisthe... ikkada tap cheyyandi.'] }; const current = states[state]; button.querySelector('span').textContent = current[0]; button.querySelector('strong').textContent = current[1]; status.textContent = current[2]; button.classList.toggle('listening', state === 'listening'); }

    async speak(text) { if (!('speechSynthesis' in window) || !text) return; text = this.addressUser(text); this.duckMusic(); window.speechSynthesis.cancel(); await this.wait(120); let voices = window.speechSynthesis.getVoices(); if (!voices.length) { await new Promise(resolve => { const onVoices = () => { window.speechSynthesis.removeEventListener('voiceschanged', onVoices); resolve(); }; window.speechSynthesis.addEventListener('voiceschanged', onVoices); window.setTimeout(resolve, 1000); }); voices = window.speechSynthesis.getVoices(); } const utterance = new SpeechSynthesisUtterance(text); utterance.rate = .8; utterance.pitch = 1.05; utterance.volume = 1; utterance.voice = voices.find(voice => /en-IN/i.test(voice.lang) && /heera|female|woman|jenny|aria/i.test(voice.name)) || voices.find(voice => /en-IN/i.test(voice.lang)) || voices.find(voice => /^en-/i.test(voice.lang) && /female|woman|zira|samantha|jenny|aria/i.test(voice.name)) || voices.find(voice => /^en-/i.test(voice.lang)) || voices[0]; utterance.lang = utterance.voice?.lang || 'en-IN'; document.getElementById('audio-status').textContent = 'Female voice speaking'; return new Promise(resolve => { let finished = false; const finish = () => { if (finished) return; finished = true; this.restoreMusic(); document.getElementById('audio-status').textContent = 'Voice ready'; resolve(); }; utterance.onstart = () => { document.getElementById('audio-status').textContent = 'Female voice speaking'; }; utterance.onend = finish; utterance.onerror = finish; window.speechSynthesis.speak(utterance); window.setTimeout(finish, Math.max(5000, text.length * 105)); }); }
    playBackgroundMusic() { if (!this.music) return; this.music.volume = .18; this.music.play().catch(() => {}); }
    duckMusic() { if (this.music) this.music.volume = .05; }
    restoreMusic() { if (this.music) this.music.volume = .18; }
    async recordOutcome(transcript, intent, remembered, state) { try { const response = await fetch(`${CONFIG.BACKEND_URL}${CONFIG.ENDPOINTS.recordOutcome}`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ patient_id: CONFIG.PATIENT.id, game_id: 'lakshmi_memory_journey', scene_id: state, option_id: intent, action_id: remembered ? 'positive_recall' : 'memory_cue', is_correct: remembered, hint_level: remembered ? 0 : 1, recall_type: remembered ? 'independent' : 'cue_assisted', response_time: 0, transcript, recognized_intent: intent, remembered, timestamp: new Date().toISOString() }) }); if (response.ok) console.log('Memory outcome recorded'); } catch (error) { console.warn('Outcome recording unavailable', error); } }
    updateMemoryIndicator() { const indicator = document.getElementById('memory-indicator'); const hearts = [...this.moments.slice(0, 5), ...Array(Math.max(0, 5 - this.moments.length)).fill('🤍')].slice(0, 5); indicator.innerHTML = `Memory Moments ${hearts.map(moment => `<span>${moment}</span>`).join('')}`; }
    complete() { this.showScreen('results-screen'); this.speakSequence(ENGLISH_SPEECH.COMPLETE); }
    showScreen(id) { document.querySelectorAll('.screen').forEach(screen => screen.classList.remove('active')); document.getElementById(id).classList.add('active'); }
    showError(message) { document.getElementById('error-message').textContent = message; this.showScreen('error-screen'); }
}

let game = null;
window.addEventListener('DOMContentLoaded', () => { game = new MemoryJourney(); game.init(); });
