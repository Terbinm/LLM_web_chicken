"""
Game Manager - Handles overall game logic and state
游戏管理器 - 处理整体游戏逻辑和状态
"""

import random
from typing import Dict, List, Optional, Tuple
from .game_data import LOCATIONS, QUESTS, ITEMS, ENEMIES
from .combat_manager import CombatManager


class GameManager:
    """Manages game state and progression"""

    @staticmethod
    def check_random_encounter(location_id: str) -> Optional[str]:
        """
        Check if random encounter occurs

        Args:
            location_id: Current location ID

        Returns:
            Enemy ID if encounter occurs, None otherwise
        """
        location = LOCATIONS.get(location_id)
        if not location:
            return None

        # Check encounter rate
        if random.random() < location['encounter_rate']:
            # Select random enemy from location
            enemies = location['encounters']
            return random.choice(enemies)

        return None

    @staticmethod
    def can_access_location(character, location_id: str) -> Tuple[bool, str]:
        """
        Check if character can access location

        Args:
            character: Character instance
            location_id: Location to check

        Returns:
            Tuple of (can_access, reason_if_not)
        """
        location = LOCATIONS.get(location_id)
        if not location:
            return False, "未知的地点"

        # Check if location requires quest completion
        if 'requires_quest' in location:
            from models import QuestProgress
            quest_id = location['requires_quest']

            quest_progress = QuestProgress.query.filter_by(
                character_id=character.id,
                quest_id=quest_id,
                status='completed'
            ).first()

            if not quest_progress:
                quest_name = QUESTS[quest_id]['name']
                return False, f"需要完成任务: {quest_name}"

        return True, ""

    @staticmethod
    def move_to_location(character, location_id: str) -> Dict:
        """
        Move character to new location

        Args:
            character: Character instance
            location_id: Target location ID

        Returns:
            Result dictionary
        """
        can_access, reason = GameManager.can_access_location(character, location_id)

        if not can_access:
            return {
                'success': False,
                'message': reason
            }

        location = LOCATIONS[location_id]
        character.current_location = location_id

        return {
            'success': True,
            'location': location,
            'message': f"你来到了 {location['icon']} {location['name']}"
        }

    @staticmethod
    def explore_location(character) -> Dict:
        """
        Explore current location (chance of encounter)

        Args:
            character: Character instance

        Returns:
            Exploration result
        """
        location_id = character.current_location
        location = LOCATIONS[location_id]

        # Check for random encounter
        enemy_id = GameManager.check_random_encounter(location_id)

        if enemy_id:
            # Start combat
            combat_state = CombatManager.start_combat(character, enemy_id)
            return {
                'type': 'combat',
                'combat_state': combat_state,
                'message': f"探索时遭遇了 {combat_state['enemy']['icon']} {combat_state['enemy']['name']}！"
            }
        else:
            # Safe exploration
            return {
                'type': 'safe',
                'message': f"你在 {location['name']} 探索，但没有遇到危险"
            }

    @staticmethod
    def add_item_to_inventory(character, item_id: str, quantity: int = 1) -> Dict:
        """
        Add item to character inventory

        Args:
            character: Character instance
            item_id: Item ID to add
            quantity: Quantity to add

        Returns:
            Result dictionary
        """
        from models import InventoryItem, db
        from .game_data import GAME_SETTINGS

        # Check inventory size
        current_items = len(character.inventory)
        if current_items >= GAME_SETTINGS['max_inventory_size']:
            return {
                'success': False,
                'message': '背包已满！'
            }

        item_data = ITEMS.get(item_id)
        if not item_data:
            return {
                'success': False,
                'message': '无效的物品'
            }

        # Check if item already exists (for stackable items)
        if item_data.get('stackable', False):
            existing_item = InventoryItem.query.filter_by(
                character_id=character.id,
                item_id=item_id
            ).first()

            if existing_item:
                existing_item.quantity += quantity
                db.session.commit()
                return {
                    'success': True,
                    'message': f"获得 {item_data['name']} x{quantity}"
                }

        # Add new item
        new_item = InventoryItem(
            character_id=character.id,
            item_id=item_id,
            quantity=quantity
        )
        db.session.add(new_item)
        db.session.commit()

        return {
            'success': True,
            'message': f"获得 {item_data['icon']} {item_data['name']}"
        }

    @staticmethod
    def remove_item_from_inventory(character, item_id: str, quantity: int = 1) -> bool:
        """
        Remove item from inventory

        Args:
            character: Character instance
            item_id: Item ID to remove
            quantity: Quantity to remove

        Returns:
            True if successful, False otherwise
        """
        from models import InventoryItem, db

        item = InventoryItem.query.filter_by(
            character_id=character.id,
            item_id=item_id
        ).first()

        if not item or item.quantity < quantity:
            return False

        item.quantity -= quantity

        if item.quantity <= 0:
            db.session.delete(item)

        db.session.commit()
        return True

    @staticmethod
    def equip_item(character, inventory_item_id: int) -> Dict:
        """
        Equip item from inventory

        Args:
            character: Character instance
            inventory_item_id: Inventory item ID

        Returns:
            Result dictionary
        """
        from models import InventoryItem, db

        item = InventoryItem.query.get(inventory_item_id)
        if not item or item.character_id != character.id:
            return {
                'success': False,
                'message': '物品不存在'
            }

        item_data = ITEMS[item.item_id]
        item_type = item_data['type']

        if item_type == 'weapon':
            # Unequip old weapon
            if character.equipped_weapon_id:
                old_weapon = InventoryItem.query.get(character.equipped_weapon_id)
                if old_weapon:
                    old_weapon.is_equipped = False

            # Equip new weapon
            character.equipped_weapon_id = item.id
            item.is_equipped = True

            # Apply stat changes
            character.attack += item_data.get('attack_bonus', 0)
            if 'mp_bonus' in item_data:
                character.max_mp += item_data['mp_bonus']

            db.session.commit()
            return {
                'success': True,
                'message': f"装备了 {item_data['icon']} {item_data['name']}"
            }

        elif item_type == 'armor':
            # Unequip old armor
            if character.equipped_armor_id:
                old_armor = InventoryItem.query.get(character.equipped_armor_id)
                if old_armor:
                    old_armor.is_equipped = False

            # Equip new armor
            character.equipped_armor_id = item.id
            item.is_equipped = True

            # Apply stat changes
            character.defense += item_data.get('defense_bonus', 0)
            if 'mp_bonus' in item_data:
                character.max_mp += item_data['mp_bonus']

            db.session.commit()
            return {
                'success': True,
                'message': f"装备了 {item_data['icon']} {item_data['name']}"
            }

        return {
            'success': False,
            'message': '该物品无法装备'
        }

    @staticmethod
    def buy_item(character, item_id: str, quantity: int = 1) -> Dict:
        """
        Buy item from shop

        Args:
            character: Character instance
            item_id: Item ID to buy
            quantity: Quantity to buy

        Returns:
            Result dictionary
        """
        from models import db
        from .game_data import GAME_SETTINGS

        # Check if item is available in shop
        if item_id not in GAME_SETTINGS['shop_items']:
            return {
                'success': False,
                'message': '商店没有该物品'
            }

        item_data = ITEMS.get(item_id)
        if not item_data:
            return {
                'success': False,
                'message': '无效的物品'
            }

        # Check if player has enough gold
        total_cost = item_data['price'] * quantity
        if character.gold < total_cost:
            return {
                'success': False,
                'message': f'金币不足！需要 {total_cost} 金币'
            }

        # Deduct gold
        character.gold -= total_cost
        db.session.commit()

        # Add item to inventory
        result = GameManager.add_item_to_inventory(character, item_id, quantity)

        if result['success']:
            result['message'] = f"花费 {total_cost} 金币，购买了 {item_data['name']} x{quantity}"

        return result

    @staticmethod
    def start_quest(character, quest_id: str) -> Dict:
        """
        Start a new quest

        Args:
            character: Character instance
            quest_id: Quest ID to start

        Returns:
            Result dictionary
        """
        from models import QuestProgress, db

        quest_data = QUESTS.get(quest_id)
        if not quest_data:
            return {
                'success': False,
                'message': '无效的任务'
            }

        # Check if quest already active or completed
        existing = QuestProgress.query.filter_by(
            character_id=character.id,
            quest_id=quest_id
        ).first()

        if existing:
            return {
                'success': False,
                'message': '任务已经接取或完成'
            }

        # Create new quest progress
        quest_progress = QuestProgress(
            character_id=character.id,
            quest_id=quest_id,
            status='active'
        )
        db.session.add(quest_progress)
        db.session.commit()

        return {
            'success': True,
            'quest': quest_data,
            'message': f"接取任务: {quest_data['name']}"
        }

    @staticmethod
    def complete_quest(character, quest_id: str) -> Dict:
        """
        Complete a quest and give rewards

        Args:
            character: Character instance
            quest_id: Quest ID to complete

        Returns:
            Result dictionary
        """
        from models import QuestProgress, db

        quest_progress = QuestProgress.query.filter_by(
            character_id=character.id,
            quest_id=quest_id,
            status='active'
        ).first()

        if not quest_progress:
            return {
                'success': False,
                'message': '任务未激活'
            }

        quest_data = QUESTS[quest_id]

        # Award rewards
        rewards = quest_data['rewards']

        # Experience
        if 'experience' in rewards:
            level_ups = character.gain_experience(rewards['experience'])

        # Gold
        if 'gold' in rewards:
            character.gold += rewards['gold']

        # Items
        if 'items' in rewards:
            for item_id in rewards['items']:
                GameManager.add_item_to_inventory(character, item_id)

        # Mark quest as completed
        quest_progress.complete()
        db.session.commit()

        # Start next quest if available
        if 'next_quest' in quest_data:
            GameManager.start_quest(character, quest_data['next_quest'])

        return {
            'success': True,
            'quest': quest_data,
            'rewards': rewards,
            'message': f"完成任务: {quest_data['name']}"
        }

    @staticmethod
    def get_active_quests(character) -> List[Dict]:
        """
        Get character's active quests

        Args:
            character: Character instance

        Returns:
            List of active quest data
        """
        from models import QuestProgress

        active_quests = QuestProgress.query.filter_by(
            character_id=character.id,
            status='active'
        ).all()

        quest_list = []
        for quest_progress in active_quests:
            quest_data = QUESTS.get(quest_progress.quest_id)
            if quest_data:
                quest_list.append({
                    **quest_data,
                    'progress_id': quest_progress.id,
                    'started_at': quest_progress.started_at
                })

        return quest_list
