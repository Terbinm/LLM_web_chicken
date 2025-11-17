"""
Combat Manager - Handles all combat calculations on backend
战斗管理器 - 后端处理所有战斗数值计算

IMPORTANT: All numerical calculations MUST be done here.
Gemini can only provide narrative descriptions, not calculate damage.
重要：所有数值计算必须在此处完成。
Gemini 只能提供叙述描述，不能计算伤害。
"""

import random
from typing import Dict, List, Tuple
from .game_data import ENEMIES, ITEMS


class CombatManager:
    """Manages combat encounters and calculations"""

    @staticmethod
    def start_combat(character, enemy_id: str) -> Dict:
        """
        Start a new combat encounter

        Args:
            character: Character model instance
            enemy_id: Enemy ID from ENEMIES

        Returns:
            Combat state dictionary
        """
        enemy_data = ENEMIES.get(enemy_id)
        if not enemy_data:
            raise ValueError(f"Invalid enemy ID: {enemy_id}")

        # Create enemy instance
        enemy = {
            'id': enemy_id,
            'name': enemy_data['name'],
            'description': enemy_data['description'],
            'level': enemy_data['level'],
            'hp': enemy_data['hp'],
            'max_hp': enemy_data['max_hp'],
            'attack': enemy_data['attack'],
            'defense': enemy_data['defense'],
            'icon': enemy_data['icon'],
            'current_phase': 0,
            'ability_cooldowns': {}
        }

        combat_state = {
            'active': True,
            'turn': 1,
            'enemy': enemy,
            'character': {
                'hp': character.hp,
                'max_hp': character.max_hp,
                'mp': character.mp,
                'max_mp': character.max_mp,
                'attack': character.attack,
                'defense': character.defense
            },
            'log': [f'遭遇了 {enemy["icon"]} {enemy["name"]}！']
        }

        return combat_state

    @staticmethod
    def calculate_damage(attacker_attack: int, defender_defense: int,
                        is_critical: bool = False, multiplier: float = 1.0) -> int:
        """
        Calculate damage (backend controlled)

        Args:
            attacker_attack: Attacker's attack value
            defender_defense: Defender's defense value
            is_critical: Whether this is a critical hit
            multiplier: Damage multiplier

        Returns:
            Final damage amount
        """
        base_damage = max(1, attacker_attack - defender_defense)

        # Add variance (90% - 110%)
        variance = random.uniform(0.9, 1.1)
        damage = int(base_damage * variance * multiplier)

        # Critical hit
        if is_critical:
            damage = int(damage * 1.5)

        return max(1, damage)

    @staticmethod
    def check_critical_hit() -> bool:
        """Check if attack is critical hit (15% chance)"""
        return random.random() < 0.15

    @staticmethod
    def player_attack(combat_state: Dict, character) -> Dict:
        """
        Execute player attack action

        Args:
            combat_state: Current combat state
            character: Character instance

        Returns:
            Updated combat state with results
        """
        enemy = combat_state['enemy']

        # Check critical hit
        is_critical = CombatManager.check_critical_hit()

        # Calculate damage
        damage = CombatManager.calculate_damage(
            character.attack,
            enemy['defense'],
            is_critical
        )

        # Apply damage
        enemy['hp'] -= damage

        # Create log entry
        if is_critical:
            combat_state['log'].append(f"💥 暴击！你对 {enemy['name']} 造成了 {damage} 点伤害！")
        else:
            combat_state['log'].append(f"⚔️ 你攻击 {enemy['name']}，造成了 {damage} 点伤害")

        # Check if enemy defeated
        if enemy['hp'] <= 0:
            enemy['hp'] = 0
            return CombatManager.end_combat(combat_state, character, victory=True)

        # Enemy counter-attack
        return CombatManager.enemy_turn(combat_state, character)

    @staticmethod
    def player_defend(combat_state: Dict, character) -> Dict:
        """
        Execute player defend action (reduce incoming damage next turn)

        Args:
            combat_state: Current combat state
            character: Character instance

        Returns:
            Updated combat state
        """
        combat_state['defending'] = True
        combat_state['log'].append("🛡️ 你进入了防御姿态")

        # Enemy turn with reduced damage
        result = CombatManager.enemy_turn(combat_state, character,
                                         defend_multiplier=0.5)
        combat_state['defending'] = False

        return result

    @staticmethod
    def player_use_item(combat_state: Dict, character, item_id: str) -> Dict:
        """
        Execute player use item action

        Args:
            combat_state: Current combat state
            character: Character instance
            item_id: Item to use

        Returns:
            Updated combat state
        """
        item_data = ITEMS.get(item_id)
        if not item_data or item_data['type'] != 'consumable':
            combat_state['log'].append("❌ 无法使用该物品")
            return combat_state

        # Apply item effect
        if item_data['effect'] == 'heal':
            heal_amount = item_data['heal_amount']
            character.heal(heal_amount)
            combat_state['character']['hp'] = character.hp
            combat_state['log'].append(f"💊 使用 {item_data['name']}，恢复了 {heal_amount} HP")

        elif item_data['effect'] == 'restore_mp':
            mp_amount = item_data['mp_amount']
            character.restore_mp(mp_amount)
            combat_state['character']['mp'] = character.mp
            combat_state['log'].append(f"💙 使用 {item_data['name']}，恢复了 {mp_amount} MP")

        elif item_data['effect'] == 'full_restore':
            character.heal(character.max_hp)
            character.restore_mp(character.max_mp)
            combat_state['character']['hp'] = character.hp
            combat_state['character']['mp'] = character.mp
            combat_state['log'].append(f"✨ 使用 {item_data['name']}，完全恢复！")

        # Enemy turn
        return CombatManager.enemy_turn(combat_state, character)

    @staticmethod
    def enemy_turn(combat_state: Dict, character, defend_multiplier: float = 1.0) -> Dict:
        """
        Execute enemy turn

        Args:
            combat_state: Current combat state
            character: Character instance
            defend_multiplier: Damage multiplier if player is defending

        Returns:
            Updated combat state
        """
        enemy = combat_state['enemy']
        enemy_data = ENEMIES.get(enemy['id'])

        # Check for special abilities (BOSS only)
        if 'special_abilities' in enemy_data and enemy['level'] >= 10:
            ability = CombatManager._check_special_ability(combat_state, enemy_data)
            if ability:
                return CombatManager._execute_special_ability(
                    combat_state, character, ability, defend_multiplier
                )

        # Normal attack
        is_critical = CombatManager.check_critical_hit()
        damage = CombatManager.calculate_damage(
            enemy['attack'],
            character.defense,
            is_critical,
            defend_multiplier
        )

        # Apply damage to character
        character.take_damage(damage)
        combat_state['character']['hp'] = character.hp

        # Log
        if is_critical:
            combat_state['log'].append(f"💥 {enemy['name']} 暴击！对你造成了 {damage} 点伤害！")
        else:
            combat_state['log'].append(f"👹 {enemy['name']} 攻击你，造成了 {damage} 点伤害")

        # Check if player died
        if character.hp <= 0:
            character.hp = 0
            combat_state['character']['hp'] = 0
            return CombatManager.end_combat(combat_state, character, victory=False)

        # Check phase transition for bosses
        if 'phases' in enemy_data:
            CombatManager._check_phase_transition(combat_state, enemy_data)

        combat_state['turn'] += 1
        return combat_state

    @staticmethod
    def _check_special_ability(combat_state: Dict, enemy_data: Dict) -> Dict:
        """Check if enemy should use special ability"""
        abilities = enemy_data.get('special_abilities', [])
        enemy = combat_state['enemy']

        for ability in abilities:
            cooldown = enemy['ability_cooldowns'].get(ability['name'], 0)
            if cooldown == 0 and random.random() < 0.3:  # 30% chance
                return ability

        # Decrement cooldowns
        for ability_name in enemy['ability_cooldowns']:
            if enemy['ability_cooldowns'][ability_name] > 0:
                enemy['ability_cooldowns'][ability_name] -= 1

        return None

    @staticmethod
    def _execute_special_ability(combat_state: Dict, character,
                                ability: Dict, defend_multiplier: float) -> Dict:
        """Execute enemy special ability"""
        enemy = combat_state['enemy']

        # Calculate special damage
        damage = CombatManager.calculate_damage(
            enemy['attack'],
            character.defense,
            multiplier=ability['damage_multiplier'] * defend_multiplier
        )

        # Apply damage
        character.take_damage(damage)
        combat_state['character']['hp'] = character.hp

        # Log special ability
        combat_state['log'].append(
            f"🔥 {enemy['name']} 使用了 {ability['name']}！造成了 {damage} 点伤害！"
        )

        # Heal if applicable
        if 'heal_percent' in ability:
            heal_amount = int(damage * ability['heal_percent'])
            enemy['hp'] = min(enemy['max_hp'], enemy['hp'] + heal_amount)
            combat_state['log'].append(f"💚 {enemy['name']} 吸取了 {heal_amount} 点生命值")

        # Set cooldown
        enemy['ability_cooldowns'][ability['name']] = ability['cooldown']

        # Check if player died
        if character.hp <= 0:
            return CombatManager.end_combat(combat_state, character, victory=False)

        combat_state['turn'] += 1
        return combat_state

    @staticmethod
    def _check_phase_transition(combat_state: Dict, enemy_data: Dict):
        """Check and handle boss phase transitions"""
        enemy = combat_state['enemy']
        phases = enemy_data.get('phases', [])

        current_phase = enemy.get('current_phase', 0)
        if current_phase < len(phases):
            phase = phases[current_phase]
            if enemy['hp'] <= phase['hp_threshold']:
                # Apply phase changes
                if 'attack_multiplier' in phase:
                    enemy['attack'] = int(enemy['attack'] * phase['attack_multiplier'])

                combat_state['log'].append(f"⚠️ {phase['message']}")
                enemy['current_phase'] = current_phase + 1

    @staticmethod
    def attempt_flee(combat_state: Dict) -> Tuple[bool, Dict]:
        """
        Attempt to flee from combat (50% success rate for normal enemies, 0% for bosses)

        Args:
            combat_state: Current combat state

        Returns:
            Tuple of (success, updated_combat_state)
        """
        enemy = combat_state['enemy']
        enemy_data = ENEMIES.get(enemy['id'])

        # Cannot flee from bosses
        if enemy_data['level'] >= 10:
            combat_state['log'].append("❌ 无法逃离！{enemy['name']} 阻止了你的逃跑！")
            # Enemy gets free attack
            return False, combat_state

        # 50% chance to flee
        if random.random() < 0.5:
            combat_state['log'].append("🏃 成功逃离了战斗！")
            combat_state['active'] = False
            combat_state['fled'] = True
            return True, combat_state
        else:
            combat_state['log'].append("❌ 逃跑失败！")
            return False, combat_state

    @staticmethod
    def end_combat(combat_state: Dict, character, victory: bool) -> Dict:
        """
        End combat and distribute rewards/penalties

        Args:
            combat_state: Current combat state
            character: Character instance
            victory: Whether player won

        Returns:
            Final combat state with rewards/penalties
        """
        combat_state['active'] = False
        combat_state['victory'] = victory

        if victory:
            enemy = combat_state['enemy']
            enemy_data = ENEMIES.get(enemy['id'])

            # Award experience
            exp_gained = enemy_data['experience']
            level_ups = character.gain_experience(exp_gained)
            combat_state['exp_gained'] = exp_gained

            # Award gold
            gold_gained = enemy_data['gold']
            character.gold += gold_gained
            combat_state['gold_gained'] = gold_gained

            # Process loot
            loot_items = CombatManager._process_loot(enemy_data['loot'])
            combat_state['loot'] = loot_items

            # Log victory
            combat_state['log'].append(f"🎉 战斗胜利！")
            combat_state['log'].append(f"📈 获得 {exp_gained} 经验值")
            combat_state['log'].append(f"💰 获得 {gold_gained} 金币")

            if level_ups > 0:
                combat_state['log'].append(f"⬆️ 等级提升！当前等级: {character.level}")

            if loot_items:
                items_str = ', '.join([ITEMS[item]['name'] for item in loot_items])
                combat_state['log'].append(f"🎁 获得物品: {items_str}")

            # Check if final boss
            if enemy['id'] == 'demon_lord':
                combat_state['game_complete'] = True
                combat_state['log'].append("👑 恭喜！你击败了魔王，拯救了世界！")

        else:
            # Player died
            combat_state['log'].append("💀 你被击败了...")

            # Apply death penalty
            from .game_data import GAME_SETTINGS
            penalty = GAME_SETTINGS['death_penalty']

            gold_loss = int(character.gold * penalty['gold_loss_percent'])
            character.gold -= gold_loss

            # Restore some HP
            character.hp = int(character.max_hp * penalty['hp_restore_percent'])

            combat_state['gold_lost'] = gold_loss
            combat_state['log'].append(f"💸 失去了 {gold_loss} 金币")
            combat_state['log'].append(f"你在 {penalty['respawn_location']} 醒来")

        return combat_state

    @staticmethod
    def _process_loot(loot_table: List[Dict]) -> List[str]:
        """
        Process loot drops based on drop rates

        Args:
            loot_table: List of loot items with chances

        Returns:
            List of item IDs that dropped
        """
        dropped_items = []

        for loot_entry in loot_table:
            if random.random() < loot_entry['chance']:
                dropped_items.append(loot_entry['item_id'])

        return dropped_items

    @staticmethod
    def get_available_actions(combat_state: Dict, character) -> List[Dict]:
        """
        Get available combat actions (for player to choose)

        Args:
            combat_state: Current combat state
            character: Character instance

        Returns:
            List of available action dictionaries
        """
        actions = [
            {
                'id': 'attack',
                'name': '攻击',
                'description': '对敌人进行攻击',
                'icon': '⚔️'
            },
            {
                'id': 'defend',
                'name': '防御',
                'description': '进入防御姿态，减少受到的伤害',
                'icon': '🛡️'
            }
        ]

        # Add flee option (not for bosses)
        enemy_data = ENEMIES.get(combat_state['enemy']['id'])
        if enemy_data['level'] < 10:
            actions.append({
                'id': 'flee',
                'name': '逃跑',
                'description': '尝试逃离战斗',
                'icon': '🏃'
            })

        # Add item options
        actions.append({
            'id': 'item',
            'name': '使用物品',
            'description': '使用背包中的消耗品',
            'icon': '🎒'
        })

        return actions
