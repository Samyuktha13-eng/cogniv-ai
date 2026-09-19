/* ========================================================================== */
/* Animation Manager - Handles all animations for characters and assets     */
/* ========================================================================== */

class AnimationManager {
    constructor() {
        this.activeAnimations = new Map();
    }

    /**
     * Play an animation sequence
     * @param {string} elementId - ID of element to animate
     * @param {string} animationName - Name of animation
     * @param {number} duration - Duration in ms (optional, uses CSS default)
     */
    play(elementId, animationName, duration = null) {
        return new Promise((resolve) => {
            const element = document.getElementById(elementId);
            if (!element) {
                console.warn(`Element not found: ${elementId}`);
                resolve();
                return;
            }

            // Remove previous animation
            element.classList.remove(animationName);

            // Trigger reflow to restart animation
            void element.offsetWidth;

            // Add animation
            element.classList.add(animationName);

            // Handle animation end
            const handler = () => {
                element.classList.remove(animationName);
                element.removeEventListener('animationend', handler);
                this.activeAnimations.delete(elementId);
                resolve();
            };

            element.addEventListener('animationend', handler);
            this.activeAnimations.set(elementId, animationName);
        });
    }

    /**
     * Play sequence of animations in order
     * @param {Array} sequence - Array of {elementId, animationName, delay}
     */
    async playSequence(sequence) {
        for (const { elementId, animationName, delay = 0 } of sequence) {
            if (delay > 0) {
                await this.delay(delay);
            }
            await this.play(elementId, animationName);
        }
    }

    /**
     * Delay helper
     */
    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    /**
     * Show/hide element with fade
     */
    fadeIn(elementId, duration = 300) {
        return new Promise((resolve) => {
            const element = document.getElementById(elementId);
            if (!element) {
                resolve();
                return;
            }

            element.style.display = 'flex';
            element.style.opacity = '0';
            
            setTimeout(() => {
                element.style.transition = `opacity ${duration}ms ease`;
                element.style.opacity = '1';
                setTimeout(() => {
                    element.style.transition = '';
                    resolve();
                }, duration);
            }, 10);
        });
    }

    fadeOut(elementId, duration = 300) {
        return new Promise((resolve) => {
            const element = document.getElementById(elementId);
            if (!element) {
                resolve();
                return;
            }

            element.style.transition = `opacity ${duration}ms ease`;
            element.style.opacity = '0';
            
            setTimeout(() => {
                element.style.display = 'none';
                element.style.transition = '';
                resolve();
            }, duration);
        });
    }

    /**
     * Clear all animations
     */
    clearAll() {
        for (const [elementId, animationName] of this.activeAnimations) {
            const element = document.getElementById(elementId);
            if (element) {
                element.classList.remove(animationName);
            }
        }
        this.activeAnimations.clear();
    }

    /**
     * Play semantic action sequence based on action ID
     */
    async playAction(actionId) {
        const actions = {
            // Correct answer animations
            'daughter_recognition_success': async () => {
                await this.playSequence([
                    { elementId: 'character-anu', animationName: 'appear', delay: 0 },
                    { elementId: 'character-anu', animationName: 'smile', delay: 300 },
                    { elementId: 'character-anu', animationName: 'walk-to-mother', delay: 800 },
                    { elementId: 'character-anu', animationName: 'hug', delay: 1000 },
                    { elementId: 'character-anu', animationName: 'celebrate', delay: 1200 },
                ]);
            },

            'food_recognition_success': async () => {
                await this.playSequence([
                    { elementId: 'memory-chapathi', animationName: 'memory-appear', delay: 0 },
                    { elementId: 'memory-chapathi', animationName: 'celebrate', delay: 500 },
                ]);
            },

            'family_recognition_success': async () => {
                await this.playSequence([
                    { elementId: 'character-anu', animationName: 'appear', delay: 0 },
                    { elementId: 'character-rahul', animationName: 'appear', delay: 200 },
                    { elementId: 'character-anu', animationName: 'celebrate', delay: 600 },
                    { elementId: 'character-rahul', animationName: 'celebrate', delay: 600 },
                ]);
            },

            // Wrong answer animations
            'wrong_answer_encouragement': async () => {
                // Gentle shake
                const element = document.querySelector('.narration-box');
                if (element) {
                    element.style.animation = 'shake 0.4s ease';
                    await this.delay(400);
                    element.style.animation = '';
                }
            },

            'show_memory_cue': async () => {
                await this.playSequence([
                    { elementId: 'memory-chapathi', animationName: 'memory-appear', delay: 0 },
                ]);
            },

            'gentle_continue_to_kitchen': async () => {
                const element = document.getElementById('environment');
                if (element) {
                    element.style.opacity = '0.8';
                    await this.delay(400);
                    element.style.opacity = '1';
                }
            },

            'continue_to_kitchen': async () => {
                await this.fadeOut('question-section', 300);
                await this.delay(400);
            },

            // Transition animations
            'house_intro': async () => {
                const bg = document.getElementById('background-image');
                if (bg) {
                    bg.style.animation = 'slideIn 0.8s ease';
                    await this.delay(800);
                    bg.style.animation = '';
                }
            },

            'enter_kitchen': async () => {
                await this.playSequence([
                    { elementId: 'memory-chapathi', animationName: 'memory-appear', delay: 0 },
                ]);
            },

            'positive_feedback': async () => {
                const narrator = document.querySelector('.narration-box');
                if (narrator) {
                    narrator.style.animation = 'correct-pulse 0.6s ease';
                    await this.delay(600);
                    narrator.style.animation = '';
                }
            },

            'final_reward': async () => {
                await this.playSequence([
                    { elementId: 'character-anu', animationName: 'celebrate', delay: 0 },
                    { elementId: 'character-lakshmi', animationName: 'celebrate', delay: 200 },
                ]);
            },

            'reward_celebrate': async () => {
                await this.playSequence([
                    { elementId: 'character-anu', animationName: 'celebrate', delay: 0 },
                ]);
            },
        };

        const action = actions[actionId];
        if (action) {
            await action();
        } else {
            console.warn(`Unknown action: ${actionId}`);
        }
    }
}

// Create global instance
const animationManager = new AnimationManager();
