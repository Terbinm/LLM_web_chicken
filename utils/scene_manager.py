from typing import Dict, List


class SceneManager:
    """Manager for handling scene data and transitions"""

    # Scene metadata
    SCENES = {
        'computer_room': {
            'id': 'computer_room',
            'name': '電腦房',
            'name_en': 'Computer Room',
            'description': '現代化的電腦房，用於控制電腦、檢索網路資訊和進行線上活動',
            'background': '/static/images/background/computer_room.webp',
            'icon': '💻',
            'activities': ['網路搜尋', '資訊查詢', '線上學習', '程式開發']
        },
        'bedroom': {
            'id': 'bedroom',
            'name': '臥室',
            'name_en': 'Bedroom',
            'description': '舒適寧靜的臥室，適合休息、放鬆和睡眠',
            'background': '/static/images/background/bedroom.webp',
            'icon': '🛏️',
            'activities': ['休息', '睡眠', '放鬆', '冥想']
        },
        'mcp_studio': {
            'id': 'mcp_studio',
            'name': 'MCP 工作室',
            'name_en': 'MCP Studio',
            'description': '高科技的開發工作室，專門用於使用 MCP (Model Context Protocol) 工具進行開發工作',
            'background': '/static/images/background/mcp_studio.webp',
            'icon': '🔧',
            'activities': ['使用 MCP 工具', '開發工作', '系統整合', '工具調試']
        },
        'planning_room': {
            'id': 'planning_room',
            'name': '繪圖室',
            'name_en': 'Planning Room',
            'description': '創意規劃空間，用於構思、設計和規劃各種專案',
            'background': '/static/images/background/planning_room.webp',
            'icon': '📋',
            'activities': ['專案規劃', '創意設計', '腦力激盪', '文件撰寫']
        }
    }

    # Default scene
    DEFAULT_SCENE = 'computer_room'

    @classmethod
    def get_scene(cls, scene_id: str) -> Dict:
        """
        Get scene information by ID

        Args:
            scene_id: Scene identifier

        Returns:
            Dict containing scene information
        """
        return cls.SCENES.get(scene_id, cls.SCENES[cls.DEFAULT_SCENE])

    @classmethod
    def get_all_scenes(cls) -> List[Dict]:
        """
        Get all available scenes

        Returns:
            List of all scene dictionaries
        """
        return list(cls.SCENES.values())

    @classmethod
    def validate_scene(cls, scene_id: str) -> bool:
        """
        Validate if scene ID exists

        Args:
            scene_id: Scene identifier to validate

        Returns:
            True if scene exists, False otherwise
        """
        return scene_id in cls.SCENES

    @classmethod
    def get_scene_ids(cls) -> List[str]:
        """
        Get list of all scene IDs

        Returns:
            List of scene ID strings
        """
        return list(cls.SCENES.keys())

    @classmethod
    def suggest_scene(cls, user_message: str, current_scene: str) -> str:
        """
        Suggest appropriate scene based on user message keywords

        Args:
            user_message: User's input message
            current_scene: Current scene ID

        Returns:
            Suggested scene ID
        """
        message_lower = user_message.lower()

        # Keyword mapping for scene suggestions
        scene_keywords = {
            'computer_room': ['電腦', '網路', '搜尋', '查詢', '上網', 'google', '資訊', 'search', 'computer'],
            'bedroom': ['睡覺', '休息', '累', '睡眠', '放鬆', '疲倦', '躺', 'sleep', 'rest', 'tired', 'relax'],
            'mcp_studio': ['mcp', '工具', '開發', '程式', '系統', '整合', 'tool', 'develop', 'code'],
            'planning_room': ['規劃', '計畫', '設計', '構思', '繪圖', '創意', 'plan', 'design', 'idea', 'create']
        }

        # Check keywords for each scene
        for scene_id, keywords in scene_keywords.items():
            for keyword in keywords:
                if keyword in message_lower:
                    return scene_id

        # If no match, stay in current scene
        return current_scene

    @classmethod
    def get_scene_transition_message(cls, from_scene: str, to_scene: str) -> str:
        """
        Generate a transition message when switching scenes

        Args:
            from_scene: Current scene ID
            to_scene: Target scene ID

        Returns:
            Transition message string
        """
        if from_scene == to_scene:
            return f"我們繼續在{cls.SCENES[to_scene]['name']}中。"

        from_name = cls.SCENES.get(from_scene, {}).get('name', '當前位置')
        to_name = cls.SCENES[to_scene]['name']

        return f"讓我們從{from_name}移動到{to_name}吧！"
