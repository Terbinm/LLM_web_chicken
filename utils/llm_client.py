import json
import requests
from typing import Dict, Optional, List
from config import Config


class GeminiClient:
    """Client for interacting with Google Gemini 2.0 Flash API"""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Gemini client

        Args:
            api_key: Gemini API key (uses Config.GEMINI_API_KEY if not provided)
        """
        self.api_key = api_key or Config.GEMINI_API_KEY
        self.api_url = Config.GEMINI_API_URL
        self.headers = {
            'Content-Type': 'application/json',
            'X-goog-api-key': self.api_key
        }

    def generate_response(
        self,
        user_message: str,
        current_scene: str,
        conversation_history: Optional[List[Dict]] = None,
        system_context: Optional[str] = None
    ) -> Dict:
        """
        Generate AI response using Gemini API

        Args:
            user_message: User's input message
            current_scene: Current scene ID (computer_room, bedroom, mcp_studio, planning_room)
            conversation_history: List of previous messages for context
            system_context: Additional system context (for RPG game state, etc.)

        Returns:
            Dict containing:
                - message: AI response text
                - emoji: Emoji filename
                - scene: Suggested scene ID
                - mcp_command: MCP command if in MCP studio (optional)
        """
        # Build the prompt with scene context
        prompt = self._build_prompt(user_message, current_scene, conversation_history, system_context)

        # Prepare API request
        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": prompt
                        }
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.7,
                "topK": 40,
                "topP": 0.95,
                "maxOutputTokens": 1024,
            }
        }

        try:
            # Make API request
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()

            # Parse response
            result = response.json()
            ai_text = result['candidates'][0]['content']['parts'][0]['text']

            # Extract JSON from response
            parsed_response = self._parse_ai_response(ai_text, current_scene)

            return {
                'success': True,
                'data': parsed_response
            }

        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': f'API request failed: {str(e)}'
            }
        except (KeyError, IndexError, json.JSONDecodeError) as e:
            return {
                'success': False,
                'error': f'Failed to parse API response: {str(e)}'
            }

    def _build_prompt(
        self,
        user_message: str,
        current_scene: str,
        conversation_history: Optional[List[Dict]] = None,
        system_context: Optional[str] = None
    ) -> str:
        """Build structured prompt for Gemini API"""

        # If system_context is provided, use it directly (for RPG mode)
        if system_context:
            return system_context

        # Scene descriptions
        scene_info = {
            'computer_room': {
                'name': '電腦房',
                'description': '一個現代化的電腦房，用於控制電腦、檢索網路資訊和進行線上活動。'
            },
            'bedroom': {
                'name': '臥室',
                'description': '一個舒適寧靜的臥室，適合休息、放鬆和睡眠。'
            },
            'mcp_studio': {
                'name': 'MCP 工作室',
                'description': '一個高科技的開發工作室，專門用於使用 MCP (Model Context Protocol) 工具進行開發工作。'
            },
            'planning_room': {
                'name': '繪圖室',
                'description': '一個創意規劃空間，用於構思、設計和規劃各種專案。'
            }
        }

        # Available emojis
        available_emojis = [
            '預設.png', '開心.png', '大笑.png', '傷心.png', '大哭.png',
            '生氣.png', '喜愛.png', '搞笑.png', '困惑.png', '驚訝.png',
            '震驚.png', '思考.png', '困倦.png', '放鬆.png', '自信.png',
            '酷炫.png', '調皮.png', '尷尬.png', '眨眼.png', '飛吻.png', '美味.png'
        ]

        scene = scene_info.get(current_scene, scene_info['computer_room'])

        # Build conversation context
        context = ""
        if conversation_history and len(conversation_history) > 0:
            context = "\n\n對話歷史（最近3則）:\n"
            for msg in conversation_history[-3:]:
                role = "用戶" if msg.get('role') == 'user' else "AI"
                context += f"{role}: {msg.get('message', '')}\n"

        prompt = f"""你是一個虛擬 AI 助手，正在一棟透天建築中與用戶互動。你需要扮演一個友善、有幫助且富有情感的助手。

當前場景：{scene['name']}
場景描述：{scene['description']}{context}

用戶訊息：{user_message}

請根據用戶的訊息回應，並以 JSON 格式輸出（不要包含markdown代碼塊標記，直接輸出JSON）：
{{
  "message": "你的回應內容（自然、親切、有情感的回應）",
  "emoji": "選擇最合適的表情符號檔名",
  "scene": "建議的場景ID（如果需要切換場景）或保持當前場景",
  "mcp_command": "如果在 MCP 工作室且用戶提到使用工具，提供模擬的 MCP 指令，否則為空字串"
}}

可用表情符號：{', '.join(available_emojis)}

可用場景ID：
- computer_room（電腦房）：適合網路搜尋、查詢資訊、使用電腦相關活動
- bedroom（臥室）：適合休息、睡眠、放鬆
- mcp_studio（MCP工作室）：適合開發、使用工具、技術工作
- planning_room（繪圖室）：適合規劃、設計、創意思考

場景切換規則：
- **重要：每次回應都必須輸出 scene 欄位，即使場景不變**
- 如果當前場景合適且用戶沒有要求切換，使用 "{current_scene}"
- 只在用戶明確表示要進行相關活動時才建議切換場景
- 根據對話內容和用戶意圖智慧推薦最適合的場景
- 絕對不可以省略 scene 欄位，這會導致系統錯誤

表情符號選擇規則：
- 根據你回應的情緒和語氣選擇最合適的表情
- 如果是積極正面的回應，選擇「開心.png」、「自信.png」等
- 如果是思考或分析，選擇「思考.png」
- 如果是幽默或輕鬆，選擇「搞笑.png」、「調皮.png」
- 預設使用「預設.png」

MCP 指令規則：
- 只在 mcp_studio 場景且用戶明確提到使用工具時才提供
- 格式範例："mcp list-tools"、"mcp execute search --query=xxx"
- 如果不適用，返回空字串

請確保輸出是有效的 JSON 格式，不要包含任何額外的文字或markdown標記。"""

        return prompt

    def _parse_ai_response(self, ai_text: str, current_scene: str) -> Dict:
        """Parse AI response to extract structured data"""
        try:
            # Remove markdown code block markers if present
            ai_text = ai_text.strip()
            if ai_text.startswith('```json'):
                ai_text = ai_text[7:]
            if ai_text.startswith('```'):
                ai_text = ai_text[3:]
            if ai_text.endswith('```'):
                ai_text = ai_text[:-3]
            ai_text = ai_text.strip()

            # Parse JSON
            parsed = json.loads(ai_text)

            # Validate and set defaults - use current_scene as fallback
            return {
                'message': parsed.get('message', '抱歉，我無法生成適當的回應。'),
                'emoji': parsed.get('emoji', '預設.png'),
                'scene': parsed.get('scene', current_scene),  # Default to current scene
                'mcp_command': parsed.get('mcp_command', '')
            }

        except json.JSONDecodeError:
            # Fallback: return plain text as message, keep current scene
            return {
                'message': ai_text if ai_text else '抱歉，我無法生成適當的回應。',
                'emoji': '預設.png',
                'scene': current_scene,  # Keep current scene on error
                'mcp_command': ''
            }
