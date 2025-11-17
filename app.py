from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from config import Config
from utils import GeminiClient, SceneManager, MCPHandler, StatusManager
import os
import logging

# Initialize Flask app
app = Flask(__name__, static_folder='static')
app.config.from_object(Config)

# Enable CORS
CORS(app, origins=Config.CORS_ORIGINS)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize clients
gemini_client = None

try:
    Config.validate()
    gemini_client = GeminiClient()
    logger.info("Gemini client initialized successfully")
except ValueError as e:
    logger.warning(f"Gemini client initialization failed: {e}")
    logger.warning("API endpoints will return errors until GEMINI_API_KEY is set")


@app.route('/')
def index():
    """Serve the main application page"""
    return send_from_directory('static', 'index.html')


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'gemini_configured': gemini_client is not None
    })


@app.route('/api/scenes', methods=['GET'])
def get_scenes():
    """Get all available scenes"""
    try:
        scenes = SceneManager.get_all_scenes()
        return jsonify({
            'success': True,
            'scenes': scenes
        })
    except Exception as e:
        logger.error(f"Error getting scenes: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/scene/<scene_id>', methods=['GET'])
def get_scene(scene_id):
    """Get specific scene information"""
    try:
        if not SceneManager.validate_scene(scene_id):
            return jsonify({
                'success': False,
                'error': f'Invalid scene ID: {scene_id}'
            }), 404

        scene = SceneManager.get_scene(scene_id)
        return jsonify({
            'success': True,
            'scene': scene
        })
    except Exception as e:
        logger.error(f"Error getting scene {scene_id}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/chat', methods=['POST'])
def chat():
    """
    Handle chat messages

    Request JSON:
    {
        "message": "User message",
        "current_scene": "scene_id",
        "conversation_history": [...]  // Optional
    }

    Response JSON:
    {
        "success": true,
        "data": {
            "message": "AI response",
            "emoji": "emoji_filename.png",
            "scene": "suggested_scene_id",
            "mcp_command": "mcp command if applicable",
            "mcp_output": {...}  // If MCP command was executed
        }
    }
    """
    try:
        # Check if Gemini client is initialized
        if not gemini_client:
            return jsonify({
                'success': False,
                'error': 'Gemini API is not configured. Please set GEMINI_API_KEY in .env file.'
            }), 500

        # Parse request
        data = request.get_json()

        if not data or 'message' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing required field: message'
            }), 400

        user_message = data['message']
        current_scene = data.get('current_scene', SceneManager.DEFAULT_SCENE)
        conversation_history = data.get('conversation_history', [])
        status_data = data.get('status', {})

        # Validate scene
        if not SceneManager.validate_scene(current_scene):
            current_scene = SceneManager.DEFAULT_SCENE

        # Initialize status manager
        status_manager = StatusManager.from_dict(status_data)

        # Apply scene effect on status
        status_manager.apply_scene_effect(current_scene)

        # Apply action effects based on user message
        status_manager.apply_action_effect(user_message)

        # Generate AI response
        logger.info(f"Processing message in scene: {current_scene}")
        result = gemini_client.generate_response(
            user_message=user_message,
            current_scene=current_scene,
            conversation_history=conversation_history
        )

        if not result['success']:
            return jsonify(result), 500

        response_data = result['data']

        # Execute MCP command if present
        if response_data.get('mcp_command'):
            logger.info(f"Executing MCP command: {response_data['mcp_command']}")
            mcp_result = MCPHandler.execute_command(response_data['mcp_command'])
            response_data['mcp_output'] = mcp_result

        # Include updated status in response
        response_data['status'] = status_manager.to_dict()

        return jsonify({
            'success': True,
            'data': response_data
        })

    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': f'Internal server error: {str(e)}'
        }), 500


@app.route('/api/mcp/execute', methods=['POST'])
def execute_mcp():
    """
    Execute MCP command directly

    Request JSON:
    {
        "command": "mcp command string"
    }

    Response JSON:
    {
        "success": true,
        "result": {
            "success": true,
            "output": "command output",
            "tool_used": "tool name",
            "timestamp": "timestamp"
        }
    }
    """
    try:
        data = request.get_json()

        if not data or 'command' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing required field: command'
            }), 400

        command = data['command']
        logger.info(f"Executing MCP command: {command}")

        result = MCPHandler.execute_command(command)

        return jsonify({
            'success': True,
            'result': result
        })

    except Exception as e:
        logger.error(f"Error executing MCP command: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/mcp/tools', methods=['GET'])
def get_mcp_tools():
    """Get list of available MCP tools"""
    try:
        tools = MCPHandler.get_available_tools()
        return jsonify({
            'success': True,
            'tools': tools
        })
    except Exception as e:
        logger.error(f"Error getting MCP tools: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/emojis', methods=['GET'])
def get_emojis():
    """Get list of available emoji files"""
    try:
        emoji_dir = os.path.join(app.static_folder, 'images', 'emoji')

        if not os.path.exists(emoji_dir):
            return jsonify({
                'success': False,
                'error': 'Emoji directory not found'
            }), 404

        # Get all image files
        emoji_files = []
        for filename in os.listdir(emoji_dir):
            if filename.lower().endswith(('.png', '.gif', '.jpg', '.webp', '.jpeg')):
                emoji_files.append(filename)

        emoji_files.sort()

        return jsonify({
            'success': True,
            'emojis': emoji_files
        })

    except Exception as e:
        logger.error(f"Error getting emojis: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'success': False,
        'error': 'Resource not found'
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500


if __name__ == '__main__':
    # Check if .env file exists
    if not os.path.exists('.env'):
        logger.warning("No .env file found. Please create one based on .env.example")

    # Run the application
    logger.info(f"Starting Flask application on {Config.HOST}:{Config.PORT}")
    app.run(
        host=Config.HOST,
        port=Config.PORT,
        debug=Config.DEBUG
    )
