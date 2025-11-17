from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import json

db = SQLAlchemy()


class User(UserMixin, db.Model):
    """User account model"""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    character = db.relationship('Character', backref='user', uselist=False, cascade='all, delete-orphan')

    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Check password against hash"""
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'


class Character(db.Model):
    """Player character model"""
    __tablename__ = 'characters'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # Basic info
    name = db.Column(db.String(80), nullable=False)
    personality = db.Column(db.String(50), nullable=False)  # 勇敢, 谨慎, 智慧, 幽默
    character_class = db.Column(db.String(50), nullable=False)  # 战士, 法师, 游侠

    # Stats
    level = db.Column(db.Integer, default=1)
    experience = db.Column(db.Integer, default=0)
    hp = db.Column(db.Integer, default=100)
    max_hp = db.Column(db.Integer, default=100)
    mp = db.Column(db.Integer, default=50)
    max_mp = db.Column(db.Integer, default=50)
    attack = db.Column(db.Integer, default=10)
    defense = db.Column(db.Integer, default=5)
    gold = db.Column(db.Integer, default=100)

    # Equipment slots
    equipped_weapon_id = db.Column(db.Integer, db.ForeignKey('inventory_items.id'), nullable=True)
    equipped_armor_id = db.Column(db.Integer, db.ForeignKey('inventory_items.id'), nullable=True)

    # Game progress
    current_location = db.Column(db.String(100), default='village')
    game_stage = db.Column(db.String(50), default='beginning')  # beginning, mid_game, late_game, final_boss

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_played = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    inventory = db.relationship('InventoryItem',
                               foreign_keys='InventoryItem.character_id',
                               backref='owner',
                               cascade='all, delete-orphan')
    quest_progress = db.relationship('QuestProgress', backref='character', cascade='all, delete-orphan')

    def to_dict(self):
        """Convert character to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'personality': self.personality,
            'character_class': self.character_class,
            'level': self.level,
            'experience': self.experience,
            'hp': self.hp,
            'max_hp': self.max_hp,
            'mp': self.mp,
            'max_mp': self.max_mp,
            'attack': self.attack,
            'defense': self.defense,
            'gold': self.gold,
            'current_location': self.current_location,
            'game_stage': self.game_stage,
            'equipped_weapon': self.get_equipped_weapon(),
            'equipped_armor': self.get_equipped_armor()
        }

    def get_equipped_weapon(self):
        """Get equipped weapon details"""
        if self.equipped_weapon_id:
            weapon = InventoryItem.query.get(self.equipped_weapon_id)
            return weapon.to_dict() if weapon else None
        return None

    def get_equipped_armor(self):
        """Get equipped armor details"""
        if self.equipped_armor_id:
            armor = InventoryItem.query.get(self.equipped_armor_id)
            return armor.to_dict() if armor else None
        return None

    def gain_experience(self, amount):
        """Add experience and handle level ups"""
        self.experience += amount
        level_ups = 0

        while self.experience >= self.experience_needed():
            self.level_up()
            level_ups += 1

        return level_ups

    def experience_needed(self):
        """Calculate experience needed for next level"""
        return self.level * 100

    def level_up(self):
        """Level up character"""
        self.level += 1
        self.experience -= self.experience_needed()

        # Stat increases based on class
        if self.character_class == '战士':
            self.max_hp += 15
            self.max_mp += 3
            self.attack += 3
            self.defense += 2
        elif self.character_class == '法师':
            self.max_hp += 8
            self.max_mp += 10
            self.attack += 2
            self.defense += 1
        elif self.character_class == '游侠':
            self.max_hp += 12
            self.max_mp += 5
            self.attack += 2
            self.defense += 2

        # Restore HP and MP
        self.hp = self.max_hp
        self.mp = self.max_mp

    def take_damage(self, damage):
        """Take damage and return if character died"""
        actual_damage = max(1, damage - self.defense)
        self.hp -= actual_damage

        if self.hp < 0:
            self.hp = 0
            return True  # Character died

        return False

    def heal(self, amount):
        """Heal character"""
        self.hp = min(self.max_hp, self.hp + amount)

    def restore_mp(self, amount):
        """Restore MP"""
        self.mp = min(self.max_mp, self.mp + amount)

    def __repr__(self):
        return f'<Character {self.name} Lv.{self.level}>'


class InventoryItem(db.Model):
    """Player inventory item"""
    __tablename__ = 'inventory_items'

    id = db.Column(db.Integer, primary_key=True)
    character_id = db.Column(db.Integer, db.ForeignKey('characters.id'), nullable=False)

    # Item details
    item_id = db.Column(db.String(50), nullable=False)  # Reference to ITEMS definition
    quantity = db.Column(db.Integer, default=1)
    is_equipped = db.Column(db.Boolean, default=False)

    def to_dict(self):
        """Convert to dictionary with item details"""
        from utils.game_data import ITEMS
        item_data = ITEMS.get(self.item_id, {})

        return {
            'id': self.id,
            'item_id': self.item_id,
            'quantity': self.quantity,
            'is_equipped': self.is_equipped,
            **item_data
        }

    def __repr__(self):
        return f'<InventoryItem {self.item_id} x{self.quantity}>'


class QuestProgress(db.Model):
    """Quest progress tracking"""
    __tablename__ = 'quest_progress'

    id = db.Column(db.Integer, primary_key=True)
    character_id = db.Column(db.Integer, db.ForeignKey('characters.id'), nullable=False)

    quest_id = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), default='active')  # active, completed, failed
    progress_data = db.Column(db.Text, default='{}')  # JSON string for quest-specific data
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)

    def get_progress_data(self):
        """Get progress data as dict"""
        return json.loads(self.progress_data) if self.progress_data else {}

    def set_progress_data(self, data):
        """Set progress data from dict"""
        self.progress_data = json.dumps(data)

    def complete(self):
        """Mark quest as completed"""
        self.status = 'completed'
        self.completed_at = datetime.utcnow()

    def __repr__(self):
        return f'<QuestProgress {self.quest_id} - {self.status}>'


class GameEvent(db.Model):
    """Game event log for story tracking"""
    __tablename__ = 'game_events'

    id = db.Column(db.Integer, primary_key=True)
    character_id = db.Column(db.Integer, db.ForeignKey('characters.id'), nullable=False)

    event_type = db.Column(db.String(50), nullable=False)  # combat, dialogue, item_found, level_up
    event_data = db.Column(db.Text)  # JSON string
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    character = db.relationship('Character', backref='events')

    def get_event_data(self):
        """Get event data as dict"""
        return json.loads(self.event_data) if self.event_data else {}

    def set_event_data(self, data):
        """Set event data from dict"""
        self.event_data = json.dumps(data)

    def __repr__(self):
        return f'<GameEvent {self.event_type}>'
