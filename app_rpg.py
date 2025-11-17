from flask import Flask, request, jsonify, send_from_directory, session, redirect, url_for
from flask_cors import CORS
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from config import Config
from models import db, User, Character, InventoryItem, QuestProgress, GameEvent
from utils import GeminiClient
from utils.combat_manager import CombatManager
from utils.game_manager import GameManager
from utils.game_data import (
    PERSONALITY_TEMPLATES, CHARACTER_CLASSES, ITEMS,
    ENEMIES, LOCATIONS, QUESTS, GAME_SETTINGS
)
import os
import logging
from datetime import datetime

# Initialize Flask app
app = Flask(__name__, static_folder='static')
app.config.from_object(Config)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///game.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Enable CORS
CORS(app, origins=Config.CORS_ORIGINS, supports_credentials=True)

# Initialize extensions
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Gemini client
gemini_client = None

try:
    Config.validate()
    gemini_client = GeminiClient()
    logger.info("Gemini client initialized successfully")
except ValueError as e:
    logger.warning(f"Gemini client initialization failed: {e}")


@login_manager.user_loader
def load_user(user_id):
    """Load user for Flask-Login"""
    return User.query.get(int(user_id))


# ============================================================================
# AUTHENTICATION ROUTES - 认证路由
# ============================================================================

@app.route('/api/auth/register', methods=['POST'])
def register():
    """Register new user"""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        email = data.get('email')

        if not username or not password:
            return jsonify({
                'success': False,
                'error': '用户名和密码不能为空'
            }), 400

        # Check if user exists
        if User.query.filter_by(username=username).first():
            return jsonify({
                'success': False,
                'error': '用户名已存在'
            }), 400

        # Create new user
        user = User(username=username, email=email)
        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        logger.info(f"New user registered: {username}")

        return jsonify({
            'success': True,
            'message': '注册成功！请登录'
        })

    except Exception as e:
        logger.error(f"Registration error: {e}")
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/auth/login', methods=['POST'])
def login():
    """User login"""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        user = User.query.filter_by(username=username).first()

        if not user or not user.check_password(password):
            return jsonify({
                'success': False,
                'error': '用户名或密码错误'
            }), 401

        login_user(user)

        # Check if user has character
        has_character = user.character is not None

        return jsonify({
            'success': True,
            'user': {
                'id': user.id,
                'username': user.username,
                'has_character': has_character
            },
            'message': '登录成功！'
        })

    except Exception as e:
        logger.error(f"Login error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/auth/logout', methods=['POST'])
@login_required
def logout():
    """User logout"""
    logout_user()
    return jsonify({
        'success': True,
        'message': '登出成功'
    })


@app.route('/api/auth/check', methods=['GET'])
def check_auth():
    """Check authentication status"""
    if current_user.is_authenticated:
        has_character = current_user.character is not None
        return jsonify({
            'authenticated': True,
            'user': {
                'id': current_user.id,
                'username': current_user.username,
                'has_character': has_character
            }
        })
    else:
        return jsonify({
            'authenticated': False
        })


# ============================================================================
# CHARACTER ROUTES - 角色路由
# ============================================================================

@app.route('/api/character/templates', methods=['GET'])
@login_required
def get_character_templates():
    """Get character creation templates"""
    return jsonify({
        'success': True,
        'personalities': PERSONALITY_TEMPLATES,
        'classes': CHARACTER_CLASSES
    })


@app.route('/api/character/create', methods=['POST'])
@login_required
def create_character():
    """Create new character"""
    try:
        # Check if user already has character
        if current_user.character:
            return jsonify({
                'success': False,
                'error': '角色已存在'
            }), 400

        data = request.get_json()
        name = data.get('name')
        personality = data.get('personality')
        character_class = data.get('character_class')

        if not all([name, personality, character_class]):
            return jsonify({
                'success': False,
                'error': '请填写所有必需信息'
            }), 400

        # Validate templates
        if personality not in PERSONALITY_TEMPLATES:
            return jsonify({
                'success': False,
                'error': '无效的性格模板'
            }), 400

        if character_class not in CHARACTER_CLASSES:
            return jsonify({
                'success': False,
                'error': '无效的职业'
            }), 400

        # Get base stats from class
        class_data = CHARACTER_CLASSES[character_class]
        base_stats = class_data['base_stats']

        # Get personality bonus
        personality_data = PERSONALITY_TEMPLATES[personality]
        stat_bonus = personality_data.get('stat_bonus', {})

        # Create character
        character = Character(
            user_id=current_user.id,
            name=name,
            personality=personality,
            character_class=character_class,
            hp=base_stats['hp'] + stat_bonus.get('hp', 0),
            max_hp=base_stats['max_hp'] + stat_bonus.get('hp', 0),
            mp=base_stats['mp'] + stat_bonus.get('mp', 0),
            max_mp=base_stats['max_mp'] + stat_bonus.get('mp', 0),
            attack=base_stats['attack'] + stat_bonus.get('attack', 0),
            defense=base_stats['defense'] + stat_bonus.get('defense', 0),
            gold=GAME_SETTINGS['starting_gold']
        )

        db.session.add(character)
        db.session.commit()

        # Start tutorial quest
        GameManager.start_quest(character, 'tutorial')

        # Add starting items
        GameManager.add_item_to_inventory(character, 'health_potion', 3)
        GameManager.add_item_to_inventory(character, 'rusty_sword', 1)
        GameManager.add_item_to_inventory(character, 'cloth_armor', 1)

        logger.info(f"Character created: {name} (User: {current_user.username})")

        return jsonify({
            'success': True,
            'character': character.to_dict(),
            'message': f'角色 {name} 创建成功！'
        })

    except Exception as e:
        logger.error(f"Character creation error: {e}")
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/character', methods=['GET'])
@login_required
def get_character():
    """Get current character info"""
    if not current_user.character:
        return jsonify({
            'success': False,
            'error': '角色不存在'
        }), 404

    character = current_user.character
    character.last_played = datetime.utcnow()
    db.session.commit()

    return jsonify({
        'success': True,
        'character': character.to_dict()
    })


# ============================================================================
# GAME ROUTES - 游戏路由
# ============================================================================

@app.route('/api/game/explore', methods=['POST'])
@login_required
def explore():
    """Explore current location"""
    try:
        if not current_user.character:
            return jsonify({'success': False, 'error': '角色不存在'}), 404

        character = current_user.character
        result = GameManager.explore_location(character)

        db.session.commit()

        return jsonify({
            'success': True,
            'result': result
        })

    except Exception as e:
        logger.error(f"Explore error: {e}")
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/game/move', methods=['POST'])
@login_required
def move_location():
    """Move to new location"""
    try:
        if not current_user.character:
            return jsonify({'success': False, 'error': '角色不存在'}), 404

        data = request.get_json()
        location_id = data.get('location_id')

        character = current_user.character
        result = GameManager.move_to_location(character, location_id)

        db.session.commit()

        return jsonify(result)

    except Exception as e:
        logger.error(f"Move error: {e}")
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/game/locations', methods=['GET'])
@login_required
def get_locations():
    """Get all locations"""
    return jsonify({
        'success': True,
        'locations': LOCATIONS
    })


# ============================================================================
# COMBAT ROUTES - 战斗路由
# ============================================================================

@app.route('/api/combat/action', methods=['POST'])
@login_required
def combat_action():
    """Execute combat action"""
    try:
        if not current_user.character:
            return jsonify({'success': False, 'error': '角色不存在'}), 404

        data = request.get_json()
        action = data.get('action')
        combat_state = data.get('combat_state')

        character = current_user.character

        # Execute action
        if action == 'attack':
            result = CombatManager.player_attack(combat_state, character)
        elif action == 'defend':
            result = CombatManager.player_defend(combat_state, character)
        elif action == 'flee':
            success, result = CombatManager.attempt_flee(combat_state)
        elif action == 'use_item':
            item_id = data.get('item_id')
            if not item_id:
                return jsonify({'success': False, 'error': '请选择物品'}), 400

            # Remove item from inventory
            if GameManager.remove_item_from_inventory(character, item_id):
                result = CombatManager.player_use_item(combat_state, character, item_id)
            else:
                return jsonify({'success': False, 'error': '物品不足'}), 400
        else:
            return jsonify({'success': False, 'error': '无效的行动'}), 400

        # Save changes
        db.session.commit()

        # Add loot if combat ended victoriously
        if not result.get('active') and result.get('victory'):
            if 'loot' in result:
                for item_id in result['loot']:
                    GameManager.add_item_to_inventory(character, item_id)

        return jsonify({
            'success': True,
            'combat_state': result,
            'character': character.to_dict()
        })

    except Exception as e:
        logger.error(f"Combat action error: {e}")
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================================
# INVENTORY ROUTES - 背包路由
# ============================================================================

@app.route('/api/inventory', methods=['GET'])
@login_required
def get_inventory():
    """Get character inventory"""
    if not current_user.character:
        return jsonify({'success': False, 'error': '角色不存在'}), 404

    character = current_user.character
    items = [item.to_dict() for item in character.inventory]

    return jsonify({
        'success': True,
        'inventory': items
    })


@app.route('/api/inventory/equip', methods=['POST'])
@login_required
def equip_item():
    """Equip item"""
    try:
        if not current_user.character:
            return jsonify({'success': False, 'error': '角色不存在'}), 404

        data = request.get_json()
        item_id = data.get('item_id')

        character = current_user.character
        result = GameManager.equip_item(character, item_id)

        db.session.commit()

        return jsonify({
            **result,
            'character': character.to_dict()
        })

    except Exception as e:
        logger.error(f"Equip error: {e}")
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================================
# SHOP ROUTES - 商店路由
# ============================================================================

@app.route('/api/shop/items', methods=['GET'])
@login_required
def get_shop_items():
    """Get shop items"""
    shop_items = []
    for item_id in GAME_SETTINGS['shop_items']:
        item_data = ITEMS[item_id]
        shop_items.append({
            'id': item_id,
            **item_data
        })

    return jsonify({
        'success': True,
        'items': shop_items
    })


@app.route('/api/shop/buy', methods=['POST'])
@login_required
def buy_item():
    """Buy item from shop"""
    try:
        if not current_user.character:
            return jsonify({'success': False, 'error': '角色不存在'}), 404

        data = request.get_json()
        item_id = data.get('item_id')
        quantity = data.get('quantity', 1)

        character = current_user.character
        result = GameManager.buy_item(character, item_id, quantity)

        db.session.commit()

        return jsonify({
            **result,
            'character': character.to_dict()
        })

    except Exception as e:
        logger.error(f"Buy error: {e}")
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================================
# QUEST ROUTES - 任务路由
# ============================================================================

@app.route('/api/quests', methods=['GET'])
@login_required
def get_quests():
    """Get active quests"""
    if not current_user.character:
        return jsonify({'success': False, 'error': '角色不存在'}), 404

    character = current_user.character
    quests = GameManager.get_active_quests(character)

    return jsonify({
        'success': True,
        'quests': quests
    })


# ============================================================================
# CHAT/AI ROUTES - AI对话路由
# ============================================================================

@app.route('/api/chat', methods=['POST'])
@login_required
def chat():
    """
    Handle chat with AI narrator (RPG version)
    AI只负责叙述，不计算数值
    """
    try:
        if not gemini_client:
            return jsonify({
                'success': False,
                'error': 'Gemini API未配置'
            }), 500

        if not current_user.character:
            return jsonify({
                'success': False,
                'error': '请先创建角色'
            }), 400

        data = request.get_json()
        user_message = data.get('message')
        conversation_history = data.get('conversation_history', [])

        character = current_user.character

        # Build context for AI
        context = f"""
你是一个 RPG 游戏的叙述者。你的任务是根据游戏状态生成生动的剧情描述。

**重要规则：**
1. 你只能描述发生的事情，不能决定数值
2. 战斗伤害、经验获得等数值已经由系统计算好
3. 你需要根据提供的数值生成合适的描述
4. 为玩家提供可选择的行动选项，但不要捏造这些选项的效果
5. 保持角色性格：{character.personality}

**当前角色状态：**
- 姓名：{character.name}
- 职业：{character.character_class}
- 等级：{character.level}
- HP：{character.hp}/{character.max_hp}
- MP：{character.mp}/{character.max_mp}
- 位置：{LOCATIONS[character.current_location]['name']}
- 金币：{character.gold}

**当前任务：**
{', '.join([q['name'] for q in GameManager.get_active_quests(character)])}

请根据玩家的输入，生成接下来的剧情描述。保持简洁生动。
"""

        # Generate AI response
        result = gemini_client.generate_response(
            user_message=user_message,
            current_scene=character.current_location,
            conversation_history=conversation_history,
            system_context=context
        )

        if not result['success']:
            return jsonify(result), 500

        return jsonify({
            'success': True,
            'data': result['data']
        })

    except Exception as e:
        logger.error(f"Chat error: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ============================================================================
# BASIC ROUTES - 基础路由
# ============================================================================

@app.route('/')
def index():
    """Serve main page - redirect based on auth status"""
    if current_user.is_authenticated:
        # User is logged in, redirect to appropriate page
        if current_user.character:
            return redirect('/game.html')
        else:
            return redirect('/character.html')
    else:
        # User is not logged in, show login page
        return send_from_directory('static', 'login.html')


@app.route('/game.html')
@login_required
def game_page():
    """Serve game page"""
    return send_from_directory('static', 'game.html')


@app.route('/character.html')
@login_required
def character_page():
    """Serve character creation page"""
    return send_from_directory('static', 'character.html')


@app.route('/login.html')
def login_page():
    """Serve login page"""
    if current_user.is_authenticated:
        return redirect('/')
    return send_from_directory('static', 'login.html')


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check"""
    return jsonify({
        'status': 'ok',
        'gemini_configured': gemini_client is not None
    })


# ============================================================================
# DATABASE INITIALIZATION - 数据库初始化
# ============================================================================

def init_database():
    """Initialize database"""
    with app.app_context():
        db.create_all()
        logger.info("Database initialized")


# ============================================================================
# ERROR HANDLERS - 错误处理
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'success': False, 'error': 'Resource not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({'success': False, 'error': 'Internal server error'}), 500


if __name__ == '__main__':
    # Initialize database
    init_database()

    # Run application
    logger.info(f"Starting RPG Flask application on {Config.HOST}:{Config.PORT}")
    app.run(
        host=Config.HOST,
        port=Config.PORT,
        debug=Config.DEBUG
    )
