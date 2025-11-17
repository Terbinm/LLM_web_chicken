const { createApp } = Vue;

createApp({
    data() {
        return {
            // Scene data
            scenes: [],
            currentScene: null,
            currentEmoji: '預設.png',

            // Chat data
            messages: [],
            inputMessage: '',
            isLoading: false,
            errorMessage: '',

            // Status values (Tamagotchi-style)
            status: {
                hunger: 80,
                energy: 80,
                happiness: 80,
                health: 90
            },

            // Status update timer
            statusUpdateInterval: null,

            // API base URL
            apiBaseUrl: '',

            // LocalStorage keys
            STORAGE_KEYS: {
                MESSAGES: 'flask_llm_messages',
                CURRENT_SCENE: 'flask_llm_current_scene',
                STATUS: 'flask_llm_status',
                LAST_UPDATE: 'flask_llm_last_update'
            }
        };
    },

    computed: {
        currentSceneBackground() {
            if (!this.currentScene) return '';
            return this.currentScene.background;
        },

        currentEmojiPath() {
            return `/static/images/emoji/${this.currentEmoji}`;
        },

        conversationHistory() {
            // Get last 10 messages for context
            return this.messages.slice(-10).map(msg => ({
                role: msg.role,
                message: msg.content
            }));
        }
    },

    mounted() {
        // Initialize app
        this.initializeApp();
    },

    methods: {
        async initializeApp() {
            console.log('Initializing application...');

            // Load scenes
            await this.loadScenes();

            // Load conversation history from localStorage
            this.loadConversationHistory();

            // Load status values from localStorage
            this.loadStatus();

            // Load last scene from localStorage or use default
            const savedSceneId = localStorage.getItem(this.STORAGE_KEYS.CURRENT_SCENE);
            if (savedSceneId && this.scenes.find(s => s.id === savedSceneId)) {
                this.setScene(savedSceneId);
            } else if (this.scenes.length > 0) {
                this.setScene(this.scenes[0].id);
            }

            // Start status decay timer
            this.startStatusDecay();

            console.log('Application initialized successfully');
        },

        async loadScenes() {
            try {
                const response = await fetch('/api/scenes');
                const data = await response.json();

                if (data.success) {
                    this.scenes = data.scenes;
                    console.log('Scenes loaded:', this.scenes.length);
                } else {
                    this.showError('Failed to load scenes: ' + data.error);
                }
            } catch (error) {
                console.error('Error loading scenes:', error);
                this.showError('Failed to load scenes. Please refresh the page.');
            }
        },

        setScene(sceneId) {
            const scene = this.scenes.find(s => s.id === sceneId);
            if (scene) {
                this.currentScene = scene;
                localStorage.setItem(this.STORAGE_KEYS.CURRENT_SCENE, sceneId);
                console.log('Scene changed to:', scene.name);
            }
        },

        loadConversationHistory() {
            try {
                const saved = localStorage.getItem(this.STORAGE_KEYS.MESSAGES);
                if (saved) {
                    this.messages = JSON.parse(saved);
                    console.log('Loaded conversation history:', this.messages.length, 'messages');

                    // Scroll to bottom after messages are rendered
                    this.$nextTick(() => {
                        this.scrollToBottom();
                    });
                }
            } catch (error) {
                console.error('Error loading conversation history:', error);
            }
        },

        saveConversationHistory() {
            try {
                localStorage.setItem(
                    this.STORAGE_KEYS.MESSAGES,
                    JSON.stringify(this.messages)
                );
            } catch (error) {
                console.error('Error saving conversation history:', error);
            }
        },

        clearHistory() {
            if (confirm('確定要清除所有對話記錄嗎？')) {
                this.messages = [];
                localStorage.removeItem(this.STORAGE_KEYS.MESSAGES);
                console.log('Conversation history cleared');
            }
        },

        async sendMessage() {
            if (!this.inputMessage.trim() || this.isLoading) {
                return;
            }

            const userMessage = this.inputMessage.trim();
            this.inputMessage = '';
            this.isLoading = true;
            this.errorMessage = '';

            // Add user message to chat
            this.addMessage('user', userMessage);

            try {
                // Send to API with status values
                const response = await fetch('/api/chat', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        message: userMessage,
                        current_scene: this.currentScene.id,
                        conversation_history: this.conversationHistory,
                        status: this.status
                    })
                });

                const data = await response.json();

                if (data.success) {
                    const aiResponse = data.data;

                    // Update status values from API
                    if (aiResponse.status) {
                        this.updateStatusFromAPI(aiResponse.status);
                    }

                    // Update emoji
                    if (aiResponse.emoji) {
                        this.currentEmoji = aiResponse.emoji;
                    }

                    // Switch scene if suggested
                    if (aiResponse.scene && aiResponse.scene !== this.currentScene.id) {
                        const newScene = this.scenes.find(s => s.id === aiResponse.scene);
                        if (newScene) {
                            this.setScene(aiResponse.scene);
                        }
                    }

                    // Add AI response to chat
                    this.addMessage('assistant', aiResponse.message, aiResponse.mcp_output);

                } else {
                    this.showError(data.error || 'Failed to get response from AI');
                }

            } catch (error) {
                console.error('Error sending message:', error);
                this.showError('Network error. Please check your connection and try again.');
            } finally {
                this.isLoading = false;
            }
        },

        addMessage(role, content, mcpOutput = null) {
            const message = {
                role,
                content,
                mcpOutput,
                timestamp: new Date().toLocaleTimeString('zh-TW', {
                    hour: '2-digit',
                    minute: '2-digit'
                })
            };

            this.messages.push(message);
            this.saveConversationHistory();

            // Scroll to bottom
            this.$nextTick(() => {
                this.scrollToBottom();
            });
        },

        scrollToBottom() {
            const chatMessages = this.$refs.chatMessages;
            if (chatMessages) {
                chatMessages.scrollTop = chatMessages.scrollHeight;
            }
        },

        showError(message) {
            this.errorMessage = message;
            setTimeout(() => {
                this.errorMessage = '';
            }, 5000);
        },

        handleKeyPress(event) {
            if (event.key === 'Enter' && !event.shiftKey) {
                event.preventDefault();
                this.sendMessage();
            }
        },

        // ===== Status Management Methods =====

        loadStatus() {
            try {
                const saved = localStorage.getItem(this.STORAGE_KEYS.STATUS);
                const lastUpdate = localStorage.getItem(this.STORAGE_KEYS.LAST_UPDATE);

                if (saved) {
                    this.status = JSON.parse(saved);

                    // Apply time decay if time has passed
                    if (lastUpdate) {
                        const minutesElapsed = (Date.now() - parseInt(lastUpdate)) / 60000;
                        if (minutesElapsed > 0) {
                            this.applyTimeDecay(minutesElapsed);
                        }
                    }

                    console.log('Loaded status values:', this.status);
                }
            } catch (error) {
                console.error('Error loading status:', error);
            }
        },

        saveStatus() {
            try {
                localStorage.setItem(this.STORAGE_KEYS.STATUS, JSON.stringify(this.status));
                localStorage.setItem(this.STORAGE_KEYS.LAST_UPDATE, Date.now().toString());
            } catch (error) {
                console.error('Error saving status:', error);
            }
        },

        applyTimeDecay(minutes) {
            // Decay rates per minute (matching backend)
            const decayRates = {
                hunger: 0.8,
                energy: 0.6,
                happiness: 0.5,
                health: 0.3
            };

            for (const [stat, rate] of Object.entries(decayRates)) {
                const decay = rate * minutes;
                this.status[stat] = this.clampValue(this.status[stat] - decay);
            }

            console.log(`Applied ${minutes.toFixed(1)} minutes of decay`);
        },

        startStatusDecay() {
            // Update status every 30 seconds
            this.statusUpdateInterval = setInterval(() => {
                this.applyTimeDecay(0.5); // 30 seconds = 0.5 minutes
                this.saveStatus();
            }, 30000);

            console.log('Status decay timer started');
        },

        updateStatusFromAPI(statusData) {
            if (statusData && statusData.values) {
                this.status = statusData.values;
                this.saveStatus();
                console.log('Status updated from API:', this.status);
            }
        },

        clampValue(value) {
            return Math.max(0, Math.min(100, Math.round(value)));
        }
    }
}).mount('#app');
