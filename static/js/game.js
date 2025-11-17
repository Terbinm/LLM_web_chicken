const { createApp } = Vue;

createApp({
    data() {
        return {
            character: null,
            currentView: 'game',
            inventory: [],
            shopItems: [],
            locations: {},
            currentLocation: null,
            combatState: null,
            activeQuests: [],
            messages: [],
            chatInput: '',
            showItemSelection: false,
            showLocationSelection: false,
            isLoading: false
        };
    },
    computed: {
        consumableItems() {
            return this.inventory.filter(item => item.type === 'consumable');
        }
    },
    methods: {
        async loadCharacter() {
            try {
                const res = await fetch('/api/character', { credentials: 'include' });
                const data = await res.json();
                if (data.success) {
                    this.character = data.character;
                    this.loadLocation();
                }
            } catch (error) {
                console.error('Load character error:', error);
            }
        },
        async loadInventory() {
            try {
                const res = await fetch('/api/inventory', { credentials: 'include' });
                const data = await res.json();
                if (data.success) {
                    this.inventory = data.inventory;
                }
            } catch (error) {
                console.error('Load inventory error:', error);
            }
        },
        async loadShop() {
            try {
                const res = await fetch('/api/shop/items', { credentials: 'include' });
                const data = await res.json();
                if (data.success) {
                    this.shopItems = data.items;
                }
            } catch (error) {
                console.error('Load shop error:', error);
            }
        },
        async loadLocations() {
            try {
                const res = await fetch('/api/game/locations', { credentials: 'include' });
                const data = await res.json();
                if (data.success) {
                    this.locations = data.locations;
                }
            } catch (error) {
                console.error('Load locations error:', error);
            }
        },
        async loadQuests() {
            try {
                const res = await fetch('/api/quests', { credentials: 'include' });
                const data = await res.json();
                if (data.success) {
                    this.activeQuests = data.quests;
                }
            } catch (error) {
                console.error('Load quests error:', error);
            }
        },
        loadLocation() {
            if (this.character && this.locations[this.character.current_location]) {
                this.currentLocation = this.locations[this.character.current_location];
            }
        },
        async explore() {
            this.isLoading = true;
            try {
                const res = await fetch('/api/game/explore', {
                    method: 'POST',
                    credentials: 'include',
                    headers: { 'Content-Type': 'application/json' }
                });
                const data = await res.json();
                if (data.success) {
                    if (data.result.type === 'combat') {
                        this.combatState = data.result.combat_state;
                    } else {
                        alert(data.result.message);
                    }
                }
            } catch (error) {
                console.error('Explore error:', error);
            } finally {
                this.isLoading = false;
            }
        },
        async moveTo(locationId) {
            try {
                const res = await fetch('/api/game/move', {
                    method: 'POST',
                    credentials: 'include',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ location_id: locationId })
                });
                const data = await res.json();
                if (data.success) {
                    this.character.current_location = locationId;
                    this.loadLocation();
                    this.showLocationSelection = false;
                    alert(data.message);
                } else {
                    alert(data.message || '无法前往该地点');
                }
            } catch (error) {
                console.error('Move error:', error);
            }
        },
        async doCombatAction(action) {
            this.isLoading = true;
            try {
                const res = await fetch('/api/combat/action', {
                    method: 'POST',
                    credentials: 'include',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        action: action,
                        combat_state: this.combatState
                    })
                });
                const data = await res.json();
                if (data.success) {
                    this.combatState = data.combat_state;
                    this.character = data.character;
                    
                    if (!this.combatState.active) {
                        setTimeout(() => {
                            alert(this.combatState.victory ? '战斗胜利！' : '战斗失败！');
                            this.combatState = null;
                            this.loadCharacter();
                            this.loadInventory();
                        }, 1000);
                    }
                }
            } catch (error) {
                console.error('Combat action error:', error);
            } finally {
                this.isLoading = false;
            }
        },
        async useItemInCombat(itemId) {
            this.showItemSelection = false;
            await this.doCombatAction('use_item');
            // Note: Would need to pass item_id properly
        },
        async equipItem(item) {
            if (item.type !== 'weapon' && item.type !== 'armor') {
                return;
            }
            try {
                const res = await fetch('/api/inventory/equip', {
                    method: 'POST',
                    credentials: 'include',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ item_id: item.id })
                });
                const data = await res.json();
                if (data.success) {
                    alert(data.message);
                    this.loadCharacter();
                    this.loadInventory();
                }
            } catch (error) {
                console.error('Equip error:', error);
            }
        },
        async buyItem(itemId) {
            try {
                const res = await fetch('/api/shop/buy', {
                    method: 'POST',
                    credentials: 'include',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ item_id: itemId, quantity: 1 })
                });
                const data = await res.json();
                if (data.success) {
                    alert(data.message);
                    this.loadCharacter();
                    this.loadInventory();
                } else {
                    alert(data.error);
                }
            } catch (error) {
                console.error('Buy error:', error);
            }
        },
        async sendChat() {
            if (!this.chatInput.trim()) return;
            
            const userMsg = this.chatInput;
            this.messages.push({ role: 'user', content: userMsg });
            this.chatInput = '';
            
            try {
                const res = await fetch('/api/chat', {
                    method: 'POST',
                    credentials: 'include',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        message: userMsg,
                        conversation_history: this.messages.slice(-10)
                    })
                });
                const data = await res.json();
                if (data.success) {
                    this.messages.push({ role: 'assistant', content: data.data.message });
                }
            } catch (error) {
                console.error('Chat error:', error);
            }
        },
        async logout() {
            try {
                await fetch('/api/auth/logout', {
                    method: 'POST',
                    credentials: 'include'
                });
                window.location.href = '/login.html';
            } catch (error) {
                console.error('Logout error:', error);
            }
        }
    },
    mounted() {
        this.loadCharacter();
        this.loadInventory();
        this.loadShop();
        this.loadLocations();
        this.loadQuests();
    }
}).mount('#app');
