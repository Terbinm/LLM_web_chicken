from typing import Dict
from datetime import datetime, timedelta
import random


class StatusManager:
    """Manager for Tamagotchi-style status values"""

    # Status configuration
    MAX_VALUE = 100
    MIN_VALUE = 0

    # Decay rates per minute
    DECAY_RATES = {
        'hunger': 0.8,      # Decreases slowly
        'energy': 0.6,      # Decreases slowly
        'happiness': 0.5,   # Decreases slowly
        'health': 0.3       # Decreases very slowly
    }

    # Scene effects on status values (per interaction)
    SCENE_EFFECTS = {
        'computer_room': {
            'hunger': -2,      # Computer work makes you hungry
            'energy': -3,      # Computer work is tiring
            'happiness': +2,   # Learning new things is fun
            'health': -1       # Sitting is bad for health
        },
        'bedroom': {
            'hunger': -1,      # Resting makes you a bit hungry
            'energy': +8,      # Resting restores energy
            'happiness': +3,   # Resting is relaxing
            'health': +2       # Rest improves health
        },
        'mcp_studio': {
            'hunger': -3,      # Intense work makes you very hungry
            'energy': -5,      # Intense work is very tiring
            'happiness': +5,   # Productive work is satisfying
            'health': -2       # Intense work affects health
        },
        'planning_room': {
            'hunger': -1,      # Creative work makes you a bit hungry
            'energy': -2,      # Creative work uses some energy
            'happiness': +6,   # Creative work is very fulfilling
            'health': +1       # Creative work is good for mental health
        }
    }

    # Action effects (special activities mentioned in conversation)
    ACTION_EFFECTS = {
        '吃': {'hunger': +30, 'happiness': +5},
        '喝': {'hunger': +10, 'happiness': +3},
        '睡': {'energy': +40, 'health': +5},
        '休息': {'energy': +20, 'health': +3},
        '運動': {'energy': -10, 'health': +15, 'happiness': +5},
        '玩': {'happiness': +10, 'energy': -5},
        '工作': {'happiness': -5, 'energy': -8, 'hunger': -5}
    }

    def __init__(self):
        """Initialize status manager with default values"""
        self.status = {
            'hunger': 80,
            'energy': 80,
            'happiness': 80,
            'health': 90
        }
        self.last_update = datetime.now()

    def get_status(self) -> Dict[str, int]:
        """Get current status values"""
        self._apply_time_decay()
        return self.status.copy()

    def update_from_dict(self, status_dict: Dict[str, int]):
        """Update status from dictionary"""
        for key in ['hunger', 'energy', 'happiness', 'health']:
            if key in status_dict:
                self.status[key] = self._clamp(status_dict[key])
        self.last_update = datetime.now()

    def apply_scene_effect(self, scene_id: str):
        """Apply scene effect on status values"""
        if scene_id not in self.SCENE_EFFECTS:
            return

        effects = self.SCENE_EFFECTS[scene_id]
        for stat, change in effects.items():
            self.status[stat] = self._clamp(self.status[stat] + change)

    def apply_action_effect(self, user_message: str):
        """
        Apply action effects based on user message keywords

        Args:
            user_message: User's input message
        """
        for action, effects in self.ACTION_EFFECTS.items():
            if action in user_message:
                for stat, change in effects.items():
                    self.status[stat] = self._clamp(self.status[stat] + change)
                # Only apply first matching action
                break

    def _apply_time_decay(self):
        """Apply time-based decay to status values"""
        now = datetime.now()
        minutes_elapsed = (now - self.last_update).total_seconds() / 60

        if minutes_elapsed > 0:
            for stat, decay_rate in self.DECAY_RATES.items():
                decay = decay_rate * minutes_elapsed
                self.status[stat] = self._clamp(self.status[stat] - decay)

            self.last_update = now

    def _clamp(self, value: float) -> int:
        """Clamp value between MIN_VALUE and MAX_VALUE"""
        return int(max(self.MIN_VALUE, min(self.MAX_VALUE, value)))

    def get_status_level(self, stat: str) -> str:
        """
        Get status level description

        Args:
            stat: Status name

        Returns:
            Level string: 'critical', 'low', 'medium', 'high'
        """
        value = self.status.get(stat, 50)

        if value < 20:
            return 'critical'
        elif value < 40:
            return 'low'
        elif value < 70:
            return 'medium'
        else:
            return 'high'

    def get_overall_condition(self) -> str:
        """
        Get overall condition description

        Returns:
            Condition string: 'excellent', 'good', 'fair', 'poor', 'critical'
        """
        avg = sum(self.status.values()) / len(self.status)

        if avg >= 80:
            return 'excellent'
        elif avg >= 60:
            return 'good'
        elif avg >= 40:
            return 'fair'
        elif avg >= 20:
            return 'poor'
        else:
            return 'critical'

    def get_status_emoji_hint(self) -> str:
        """
        Get emoji hint based on current status

        Returns:
            Suggested emoji filename
        """
        # Check critical conditions first
        if self.status['health'] < 20:
            return '傷心.png'
        if self.status['energy'] < 20:
            return '困倦.png'
        if self.status['hunger'] < 20:
            return '困惑.png'
        if self.status['happiness'] < 20:
            return '大哭.png'

        # Check low conditions
        if self.status['energy'] < 40:
            return '放鬆.png'
        if self.status['happiness'] < 40:
            return '尷尬.png'

        # Good conditions
        if self.status['happiness'] > 80:
            return '開心.png'
        if self.status['health'] > 80 and self.status['energy'] > 80:
            return '自信.png'

        # Default
        return '預設.png'

    def get_status_message(self) -> str:
        """
        Get status summary message for AI context

        Returns:
            Status summary string
        """
        messages = []

        # Check each status
        if self.status['hunger'] < 30:
            messages.append('角色很餓，需要吃東西')
        if self.status['energy'] < 30:
            messages.append('角色很累，需要休息')
        if self.status['happiness'] < 30:
            messages.append('角色不開心，需要做些有趣的事')
        if self.status['health'] < 30:
            messages.append('角色健康狀況不佳，需要照顧')

        if not messages:
            condition = self.get_overall_condition()
            if condition == 'excellent':
                return '角色狀態非常好，充滿活力！'
            elif condition == 'good':
                return '角色狀態良好'
            else:
                return '角色狀態普通'

        return '，'.join(messages)

    def to_dict(self) -> Dict:
        """Convert status to dictionary for API response"""
        return {
            'values': self.status.copy(),
            'levels': {
                stat: self.get_status_level(stat)
                for stat in self.status.keys()
            },
            'overall_condition': self.get_overall_condition(),
            'emoji_hint': self.get_status_emoji_hint(),
            'message': self.get_status_message()
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'StatusManager':
        """Create StatusManager from dictionary"""
        manager = cls()
        if 'values' in data:
            manager.update_from_dict(data['values'])
        elif 'hunger' in data:  # Legacy format
            manager.update_from_dict(data)
        return manager
