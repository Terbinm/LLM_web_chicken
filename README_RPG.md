# 🎮 RPG 冒险游戏 - 基于 Gemini AI

## 📝 项目简介

这是一个完全重构的 RPG 冒险游戏系统，使用 **Tailwind CSS** 打造现代化界面，集成了完整的游戏机制，包括：

- 🔐 **用户认证系统** - 登录/注册
- 👤 **角色创建系统** - 性格模板、职业选择
- ⚔️ **战斗系统** - 回合制战斗、技能、物品
- 🎒 **背包系统** - 物品管理、装备系统
- 🏪 **商店系统** - 买卖物品
- 📜 **任务系统** - 主线剧情、支线任务
- 🐉 **BOSS 战** - 最终挑战魔王

### 🎯 核心特点

**后端控制数值，AI 负责叙述**
- ✅ 所有游戏数值（伤害、经验、掉落）由后端计算
- ✅ Gemini AI 只提供剧情描述和对话
- ✅ 避免 AI 随意捏造数值，确保游戏平衡

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

创建 `.env` 文件：

```env
GEMINI_API_KEY=your_gemini_api_key_here
SECRET_KEY=your_secret_key_here
FLASK_DEBUG=True
HOST=127.0.0.1
PORT=5000
```

### 3. 初始化数据库

```bash
python app_rpg.py
```

第一次运行会自动创建数据库。

### 4. 访问游戏

打开浏览器访问：
```
http://127.0.0.1:5000/login.html
```

## 📚 游戏系统说明

### 角色系统

#### 性格模板
- **勇敢** - 攻击+2, 防御+1, HP+10
- **谨慎** - 防御+3, HP+5
- **智慧** - MP+20, 攻击+1
- **幽默** - HP+15, MP+10

#### 职业选择
- **战士** - 高 HP 和攻击力
  - HP: 120, MP: 30, 攻击: 15, 防御: 8
- **法师** - 高 MP 和魔法攻击
  - HP: 80, MP: 100, 攻击: 12, 防御: 4
- **游侠** - 平衡型职业
  - HP: 100, MP: 50, 攻击: 13, 防御: 6

### 战斗系统

#### 战斗行动
- **攻击** - 对敌人造成伤害
- **防御** - 减少受到的伤害（50%）
- **使用物品** - 使用背包中的消耗品
- **逃跑** - 尝试逃离战斗（50% 成功率，BOSS 战无法逃跑）

#### 数值计算（后端控制）
```python
基础伤害 = max(1, 攻击力 - 防御力)
实际伤害 = 基础伤害 × 随机(0.9-1.1) × 倍率
暴击伤害 = 实际伤害 × 1.5  # 15% 暴击率
```

### 物品系统

#### 武器
- 生锈的剑 - 攻击+5 (50金币)
- 铁剑 - 攻击+10 (150金币)
- 钢剑 - 攻击+20 (500金币)
- 传说之剑 - 攻击+35 (2000金币)

#### 护甲
- 布甲 - 防御+3 (40金币)
- 皮甲 - 防御+7 (120金币)
- 铁甲 - 防御+12 (400金币)
- 传说之铠 - 防御+25 (2500金币)

#### 消耗品
- 生命药水 - 恢复50 HP (50金币)
- 魔法药水 - 恢复30 MP (40金币)
- 完全恢复药水 - 完全恢复 (200金币)

### 敌人系统

#### 初期敌人
- **史莱姆** - Lv.1, HP:30, 奖励:10exp+5金
- **哥布林** - Lv.2, HP:50, 奖励:20exp+15金
- **野狼** - Lv.3, HP:70, 奖励:35exp+20金

#### 中期敌人
- **兽人战士** - Lv.5, HP:120, 奖励:80exp+50金
- **黑暗骑士** - Lv.7, HP:180, 奖励:150exp+100金

#### 后期敌人
- **巨龙** - Lv.10, HP:300, 奖励:300exp+200金

#### 最终 BOSS
- **魔王** 😈👑 - Lv.15, HP:500
  - 多阶段战斗
  - 特殊技能：黑暗冲击波、生命汲取
  - 击败后游戏通关

### 地点系统

- **新手村** 🏘️ - 起点，有商店
- **幽暗森林** 🌲 - 危险区域
- **迷雾山脉** ⛰️ - 强敌出没
- **龙之洞窟** 🕳️ - 巨龙巢穴
- **魔王城** 🏰 - 最终战场（需完成屠龙任务）

### 任务系统

1. **新手教学** - 学习基本战斗
2. **哥布林的威胁** - 击败5只哥布林
3. **探索幽暗森林** - 探索森林
4. **穿越山脉** - 获得魔法水晶
5. **屠龙勇士** - 击败巨龙
6. **最终决战** - 击败魔王

## 🏗️ 项目结构

```
LLM_web_chicken/
├── app_rpg.py              # RPG 游戏主应用
├── models.py               # 数据库模型
├── config.py               # 配置文件
├── requirements.txt        # 依赖包
├── utils/
│   ├── llm_client.py      # Gemini API 客户端
│   ├── combat_manager.py  # 战斗系统（后端数值计算）
│   ├── game_manager.py    # 游戏管理器
│   └── game_data.py       # 游戏数据定义
├── static/
│   ├── login.html         # 登录/注册页面
│   ├── character.html     # 角色创建页面
│   ├── game.html          # 主游戏界面
│   └── js/
│       └── game.js        # 游戏前端逻辑
└── game.db                 # SQLite 数据库（自动生成）
```

## 🎨 技术栈

### 后端
- **Flask** - Web 框架
- **Flask-SQLAlchemy** - ORM
- **Flask-Login** - 用户认证
- **SQLite** - 数据库

### 前端
- **Tailwind CSS** - 现代化 UI 框架
- **Vue.js 3** - 响应式前端框架

### AI
- **Google Gemini 2.0 Flash** - AI 叙述生成

## 🔒 安全特性

- 密码哈希加密（Werkzeug）
- Session 管理
- CSRF 保护
- 后端数值验证

## 🎯 核心设计理念

### 数值计算分离

**后端负责：**
```python
# combat_manager.py
def calculate_damage(attacker_attack, defender_defense):
    base_damage = max(1, attacker_attack - defender_defense)
    variance = random.uniform(0.9, 1.1)
    return int(base_damage * variance)
```

**AI 负责：**
```
根据后端计算的结果（伤害38点）生成描述：
"你挥剑斩向哥布林，利刃划过它的胸口，造成了38点伤害！"
```

### Prompt 设计

```python
context = f"""
你是 RPG 游戏叙述者。

**重要规则：**
1. 只描述事件，不计算数值
2. 战斗伤害已由系统计算：{damage}点
3. 根据数值生成合适的描述

当前状态：
- 角色：{character.name} Lv.{character.level}
- HP：{character.hp}/{character.max_hp}
- 位置：{location}

请生成剧情描述。
"""
```

## 📊 数据库结构

### User（用户）
- username, password_hash, email
- 关联 Character (一对一)

### Character（角色）
- name, personality, character_class
- level, experience, hp, mp, attack, defense, gold
- equipped_weapon_id, equipped_armor_id
- current_location, game_stage

### InventoryItem（背包物品）
- character_id, item_id, quantity, is_equipped

### QuestProgress（任务进度）
- character_id, quest_id, status, progress_data

### GameEvent（游戏事件日志）
- character_id, event_type, event_data

## 🎮 游戏流程

1. **注册/登录** → login.html
2. **创建角色** → character.html
   - 选择性格和职业
   - 获得初始装备和任务
3. **开始冒险** → game.html
   - 探索地点
   - 遭遇战斗
   - 完成任务
   - 购买装备
4. **挑战 BOSS** → 最终决战
5. **通关！** 🎉

## 🐛 故障排除

### 数据库错误
```bash
# 删除旧数据库重新初始化
rm game.db
python app_rpg.py
```

### API 错误
- 检查 `.env` 中的 `GEMINI_API_KEY`
- 确认网络连接

### 前端错误
- 清除浏览器缓存
- 检查浏览器控制台错误

## 📝 开发说明

### 添加新敌人

编辑 `utils/game_data.py`:

```python
ENEMIES = {
    'new_enemy': {
        'id': 'new_enemy',
        'name': '新敌人',
        'level': 5,
        'hp': 100,
        'attack': 15,
        'defense': 10,
        'experience': 50,
        'gold': 30,
        'loot': [...]
    }
}
```

### 添加新物品

```python
ITEMS = {
    'new_item': {
        'id': 'new_item',
        'name': '新物品',
        'type': 'weapon',  # weapon, armor, consumable
        'attack_bonus': 15,
        'price': 200,
        'icon': '⚔️'
    }
}
```

## 🚀 未来功能

- [ ] 多人在线
- [ ] 更多职业和技能
- [ ] 装备强化系统
- [ ] 公会系统
- [ ] PvP 对战
- [ ] 宠物系统

## 📄 License

MIT License

## 👏 致谢

- Google Gemini AI
- Flask 社区
- Tailwind CSS 团队

---

**祝您游戏愉快！⚔️🛡️🐉**
