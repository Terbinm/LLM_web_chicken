"""
Game data definitions - All numerical values controlled by backend
游戏数据定义 - 所有数值由后端控制
"""

# ============================================================================
# CHARACTER TEMPLATES - 角色模板
# ============================================================================

PERSONALITY_TEMPLATES = {
    'brave': {
        'id': 'brave',
        'name': '勇敢',
        'name_en': 'Brave',
        'description': '无畏的战士，面对任何危险都勇往直前',
        'stat_bonus': {'attack': 2, 'defense': 1, 'hp': 10}
    },
    'cautious': {
        'id': 'cautious',
        'name': '谨慎',
        'name_en': 'Cautious',
        'description': '小心翼翼的探险者，善于避开危险',
        'stat_bonus': {'defense': 3, 'hp': 5}
    },
    'wise': {
        'id': 'wise',
        'name': '智慧',
        'name_en': 'Wise',
        'description': '博学多才的智者，擅长使用魔法',
        'stat_bonus': {'mp': 20, 'attack': 1}
    },
    'humorous': {
        'id': 'humorous',
        'name': '幽默',
        'name_en': 'Humorous',
        'description': '乐观开朗的冒险家，总能找到快乐',
        'stat_bonus': {'hp': 15, 'mp': 10}
    }
}

CHARACTER_CLASSES = {
    'warrior': {
        'id': 'warrior',
        'name': '战士',
        'name_en': 'Warrior',
        'description': '强壮的近战战士，拥有高生命值和攻击力',
        'base_stats': {
            'hp': 120,
            'max_hp': 120,
            'mp': 30,
            'max_mp': 30,
            'attack': 15,
            'defense': 8
        }
    },
    'mage': {
        'id': 'mage',
        'name': '法师',
        'name_en': 'Mage',
        'description': '精通魔法的施法者，拥有强大的魔法攻击',
        'base_stats': {
            'hp': 80,
            'max_hp': 80,
            'mp': 100,
            'max_mp': 100,
            'attack': 12,
            'defense': 4
        }
    },
    'ranger': {
        'id': 'ranger',
        'name': '游侠',
        'name_en': 'Ranger',
        'description': '灵活的远程战士，攻守平衡',
        'base_stats': {
            'hp': 100,
            'max_hp': 100,
            'mp': 50,
            'max_mp': 50,
            'attack': 13,
            'defense': 6
        }
    }
}


# ============================================================================
# ITEMS - 物品定义（后端控制所有数值）
# ============================================================================

ITEMS = {
    # Weapons - 武器
    'rusty_sword': {
        'id': 'rusty_sword',
        'name': '生锈的剑',
        'type': 'weapon',
        'description': '一把生锈的铁剑，但依然可用',
        'attack_bonus': 5,
        'price': 50,
        'icon': '🗡️'
    },
    'iron_sword': {
        'id': 'iron_sword',
        'name': '铁剑',
        'type': 'weapon',
        'description': '标准的铁制长剑',
        'attack_bonus': 10,
        'price': 150,
        'icon': '⚔️'
    },
    'steel_sword': {
        'id': 'steel_sword',
        'name': '钢剑',
        'type': 'weapon',
        'description': '精钢打造的利剑',
        'attack_bonus': 20,
        'price': 500,
        'icon': '⚔️'
    },
    'magic_staff': {
        'id': 'magic_staff',
        'name': '魔法杖',
        'type': 'weapon',
        'description': '蕴含魔力的法杖',
        'attack_bonus': 15,
        'mp_bonus': 20,
        'price': 300,
        'icon': '🪄'
    },
    'legendary_sword': {
        'id': 'legendary_sword',
        'name': '传说之剑',
        'type': 'weapon',
        'description': '传说中的神器，拥有惊人的力量',
        'attack_bonus': 35,
        'price': 2000,
        'icon': '⚔️✨'
    },

    # Armor - 护甲
    'cloth_armor': {
        'id': 'cloth_armor',
        'name': '布甲',
        'type': 'armor',
        'description': '简单的布制护甲',
        'defense_bonus': 3,
        'price': 40,
        'icon': '🥼'
    },
    'leather_armor': {
        'id': 'leather_armor',
        'name': '皮甲',
        'type': 'armor',
        'description': '轻便的皮革护甲',
        'defense_bonus': 7,
        'price': 120,
        'icon': '🦺'
    },
    'iron_armor': {
        'id': 'iron_armor',
        'name': '铁甲',
        'type': 'armor',
        'description': '坚固的铁制铠甲',
        'defense_bonus': 12,
        'price': 400,
        'icon': '🛡️'
    },
    'magic_robe': {
        'id': 'magic_robe',
        'name': '魔法长袍',
        'type': 'armor',
        'description': '附魔的法师长袍',
        'defense_bonus': 8,
        'mp_bonus': 30,
        'price': 350,
        'icon': '🧙'
    },
    'legendary_armor': {
        'id': 'legendary_armor',
        'name': '传说之铠',
        'type': 'armor',
        'description': '传说中的防具，坚不可摧',
        'defense_bonus': 25,
        'price': 2500,
        'icon': '🛡️✨'
    },

    # Consumables - 消耗品
    'health_potion': {
        'id': 'health_potion',
        'name': '生命药水',
        'type': 'consumable',
        'description': '恢复50点生命值',
        'effect': 'heal',
        'heal_amount': 50,
        'price': 50,
        'icon': '🧪',
        'stackable': True
    },
    'mana_potion': {
        'id': 'mana_potion',
        'name': '魔法药水',
        'type': 'consumable',
        'description': '恢复30点魔法值',
        'effect': 'restore_mp',
        'mp_amount': 30,
        'price': 40,
        'icon': '💙',
        'stackable': True
    },
    'full_potion': {
        'id': 'full_potion',
        'name': '完全恢复药水',
        'type': 'consumable',
        'description': '完全恢复生命值和魔法值',
        'effect': 'full_restore',
        'price': 200,
        'icon': '✨',
        'stackable': True
    },

    # Quest Items - 任务物品
    'village_letter': {
        'id': 'village_letter',
        'name': '村长的信',
        'type': 'quest',
        'description': '村长托付的紧急信件',
        'price': 0,
        'icon': '📜'
    },
    'magic_crystal': {
        'id': 'magic_crystal',
        'name': '魔法水晶',
        'type': 'quest',
        'description': '蕴含强大魔力的水晶',
        'price': 0,
        'icon': '💎'
    }
}


# ============================================================================
# ENEMIES - 敌人定义（后端控制所有数值）
# ============================================================================

ENEMIES = {
    # Early game enemies
    'slime': {
        'id': 'slime',
        'name': '史莱姆',
        'description': '软乎乎的黏液怪物',
        'level': 1,
        'hp': 30,
        'max_hp': 30,
        'attack': 5,
        'defense': 2,
        'experience': 10,
        'gold': 5,
        'loot': [
            {'item_id': 'health_potion', 'chance': 0.3}
        ],
        'icon': '🟢'
    },
    'goblin': {
        'id': 'goblin',
        'name': '哥布林',
        'description': '狡猾的绿皮小怪物',
        'level': 2,
        'hp': 50,
        'max_hp': 50,
        'attack': 8,
        'defense': 3,
        'experience': 20,
        'gold': 15,
        'loot': [
            {'item_id': 'health_potion', 'chance': 0.4},
            {'item_id': 'rusty_sword', 'chance': 0.1}
        ],
        'icon': '👹'
    },
    'wolf': {
        'id': 'wolf',
        'name': '野狼',
        'description': '凶猛的森林野狼',
        'level': 3,
        'hp': 70,
        'max_hp': 70,
        'attack': 12,
        'defense': 4,
        'experience': 35,
        'gold': 20,
        'loot': [
            {'item_id': 'health_potion', 'chance': 0.5},
            {'item_id': 'leather_armor', 'chance': 0.15}
        ],
        'icon': '🐺'
    },

    # Mid game enemies
    'orc': {
        'id': 'orc',
        'name': '兽人战士',
        'description': '强壮的兽人战士',
        'level': 5,
        'hp': 120,
        'max_hp': 120,
        'attack': 18,
        'defense': 8,
        'experience': 80,
        'gold': 50,
        'loot': [
            {'item_id': 'health_potion', 'chance': 0.6},
            {'item_id': 'iron_sword', 'chance': 0.2},
            {'item_id': 'iron_armor', 'chance': 0.15}
        ],
        'icon': '👺'
    },
    'dark_knight': {
        'id': 'dark_knight',
        'name': '黑暗骑士',
        'description': '身穿黑甲的堕落骑士',
        'level': 7,
        'hp': 180,
        'max_hp': 180,
        'attack': 25,
        'defense': 15,
        'experience': 150,
        'gold': 100,
        'loot': [
            {'item_id': 'full_potion', 'chance': 0.4},
            {'item_id': 'steel_sword', 'chance': 0.25},
            {'item_id': 'iron_armor', 'chance': 0.3}
        ],
        'icon': '🗡️💀'
    },

    # Late game enemies
    'dragon': {
        'id': 'dragon',
        'name': '巨龙',
        'description': '传说中的巨龙',
        'level': 10,
        'hp': 300,
        'max_hp': 300,
        'attack': 35,
        'defense': 20,
        'experience': 300,
        'gold': 200,
        'loot': [
            {'item_id': 'full_potion', 'chance': 0.8},
            {'item_id': 'legendary_sword', 'chance': 0.2},
            {'item_id': 'magic_crystal', 'chance': 0.5}
        ],
        'icon': '🐉'
    },

    # FINAL BOSS - 最终魔王
    'demon_lord': {
        'id': 'demon_lord',
        'name': '魔王',
        'description': '统治黑暗的魔王，世界的终极威胁',
        'level': 15,
        'hp': 500,
        'max_hp': 500,
        'attack': 50,
        'defense': 30,
        'experience': 1000,
        'gold': 1000,
        'loot': [
            {'item_id': 'legendary_sword', 'chance': 1.0},
            {'item_id': 'legendary_armor', 'chance': 1.0}
        ],
        'icon': '😈👑',
        'phases': [
            {
                'hp_threshold': 300,
                'message': '魔王开始认真了！攻击力提升！',
                'attack_multiplier': 1.2
            },
            {
                'hp_threshold': 150,
                'message': '魔王进入狂暴状态！',
                'attack_multiplier': 1.5
            }
        ],
        'special_abilities': [
            {
                'name': '黑暗冲击波',
                'damage_multiplier': 2.0,
                'mp_cost': 0,
                'cooldown': 3
            },
            {
                'name': '生命汲取',
                'damage_multiplier': 1.5,
                'heal_percent': 0.3,
                'cooldown': 4
            }
        ]
    }
}


# ============================================================================
# LOCATIONS - 地点定义
# ============================================================================

LOCATIONS = {
    'village': {
        'id': 'village',
        'name': '新手村',
        'description': '宁静的小村庄，你的冒险起点',
        'icon': '🏘️',
        'encounters': ['slime', 'goblin'],
        'encounter_rate': 0.3,
        'shop_available': True
    },
    'forest': {
        'id': 'forest',
        'name': '幽暗森林',
        'description': '危险的森林，充满了野兽',
        'icon': '🌲',
        'encounters': ['wolf', 'goblin', 'orc'],
        'encounter_rate': 0.5,
        'shop_available': False
    },
    'mountain': {
        'id': 'mountain',
        'name': '迷雾山脉',
        'description': '高耸的山脉，强大的怪物出没',
        'icon': '⛰️',
        'encounters': ['orc', 'dark_knight'],
        'encounter_rate': 0.6,
        'shop_available': False
    },
    'cave': {
        'id': 'cave',
        'name': '龙之洞窟',
        'description': '传说中巨龙的巢穴',
        'icon': '🕳️',
        'encounters': ['dragon'],
        'encounter_rate': 0.8,
        'shop_available': False
    },
    'demon_castle': {
        'id': 'demon_castle',
        'name': '魔王城',
        'description': '魔王的居所，最终的战场',
        'icon': '🏰',
        'encounters': ['demon_lord'],
        'encounter_rate': 1.0,
        'shop_available': False,
        'requires_quest': 'defeat_dragon'
    }
}


# ============================================================================
# QUESTS - 任务定义
# ============================================================================

QUESTS = {
    'tutorial': {
        'id': 'tutorial',
        'name': '新手教学',
        'description': '学习基本的战斗和探索',
        'objectives': [
            '击败3只史莱姆',
            '访问商店',
            '装备一件装备'
        ],
        'rewards': {
            'experience': 50,
            'gold': 100,
            'items': ['health_potion']
        },
        'next_quest': 'goblin_threat'
    },
    'goblin_threat': {
        'id': 'goblin_threat',
        'name': '哥布林的威胁',
        'description': '村长请求你清除哥布林',
        'objectives': [
            '击败5只哥布林'
        ],
        'rewards': {
            'experience': 100,
            'gold': 200,
            'items': ['iron_sword']
        },
        'next_quest': 'forest_exploration'
    },
    'forest_exploration': {
        'id': 'forest_exploration',
        'name': '探索幽暗森林',
        'description': '调查森林中的异常活动',
        'objectives': [
            '探索幽暗森林',
            '击败森林中的敌人'
        ],
        'rewards': {
            'experience': 200,
            'gold': 300,
            'items': ['steel_sword', 'iron_armor']
        },
        'next_quest': 'mountain_pass'
    },
    'mountain_pass': {
        'id': 'mountain_pass',
        'name': '穿越山脉',
        'description': '前往迷雾山脉寻找魔法水晶',
        'objectives': [
            '击败3个兽人战士',
            '击败1个黑暗骑士',
            '获得魔法水晶'
        ],
        'rewards': {
            'experience': 400,
            'gold': 500,
            'items': ['magic_crystal', 'full_potion']
        },
        'next_quest': 'defeat_dragon'
    },
    'defeat_dragon': {
        'id': 'defeat_dragon',
        'name': '屠龙勇士',
        'description': '击败巨龙，获得进入魔王城的资格',
        'objectives': [
            '探索龙之洞窟',
            '击败巨龙'
        ],
        'rewards': {
            'experience': 800,
            'gold': 1000,
            'items': ['legendary_sword']
        },
        'next_quest': 'final_battle'
    },
    'final_battle': {
        'id': 'final_battle',
        'name': '最终决战',
        'description': '前往魔王城，击败魔王，拯救世界',
        'objectives': [
            '进入魔王城',
            '击败魔王'
        ],
        'rewards': {
            'experience': 2000,
            'gold': 5000,
            'items': ['legendary_armor']
        },
        'is_final': True
    }
}


# ============================================================================
# GAME SETTINGS - 游戏设置
# ============================================================================

GAME_SETTINGS = {
    'max_inventory_size': 20,
    'starting_gold': 100,
    'death_penalty': {
        'gold_loss_percent': 0.5,
        'respawn_location': 'village',
        'hp_restore_percent': 0.5
    },
    'shop_items': [
        'health_potion',
        'mana_potion',
        'full_potion',
        'rusty_sword',
        'iron_sword',
        'steel_sword',
        'cloth_armor',
        'leather_armor',
        'iron_armor',
        'magic_staff',
        'magic_robe'
    ]
}
