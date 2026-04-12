"""
AI Chat Routes - Farmer Assistant
- POST /api/chat/message          - Send text message to AI
- POST /api/chat/voice            - Send voice (audio file) to AI
- GET  /api/chat/sessions         - Get user's chat sessions
- GET  /api/chat/sessions/<id>    - Get session messages
- DELETE /api/chat/sessions/<id>  - Delete session
- POST /api/chat/sessions         - Create new session
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db, socketio
from app.models.chat import ChatSession, ChatMessage
from app.services.ai_service import (
    get_ai_response,
    transcribe_audio,
    text_to_speech
)
from app.utils.file_handler import save_audio_file
from flask_socketio import emit, join_room
import os

chat_bp = Blueprint('chat', __name__)


@chat_bp.route('/message', methods=['POST'])
@jwt_required()
def send_message():
    """
    Send a text message to the AI Farmer Assistant.
    Maintains conversation history via session_id.
    """
    user_id = int(get_jwt_identity())
    data = request.get_json()

    if not data or not data.get('message', '').strip():
        return jsonify({'success': False, 'message': 'Message content is required'}), 400

    user_message = data['message'].strip()
    session_id = data.get('session_id')
    language = data.get('language', 'hi')  # hi = Hindi, en = English

    # Get or create session
    session = None
    if session_id:
        session = ChatSession.query.filter_by(id=session_id, user_id=user_id).first()

    if not session:
        session = ChatSession(
            user_id=user_id,
            title=user_message[:50] + '...' if len(user_message) > 50 else user_message
        )
        db.session.add(session)
        db.session.flush()

    # Get conversation history for context
    history = ChatMessage.query\
        .filter_by(session_id=session.id)\
        .order_by(ChatMessage.created_at.asc())\
        .limit(20)\
        .all()

    conversation_history = [
        {'role': msg.role, 'content': msg.content}
        for msg in history
    ]

    # Save user message
    user_msg = ChatMessage(
        session_id=session.id,
        user_id=user_id,
        role='user',
        content=user_message,
        message_type='text'
    )
    db.session.add(user_msg)

    # Get AI response
    ai_response = get_ai_response(
        message=user_message,
        history=conversation_history,
        language=language
    )

    # Save AI response
    ai_msg = ChatMessage(
        session_id=session.id,
        user_id=user_id,
        role='assistant',
        content=ai_response,
        message_type='text'
    )
    db.session.add(ai_msg)
    db.session.commit()

    return jsonify({
        'success': True,
        'session_id': session.id,
        'user_message': user_msg.to_dict(),
        'ai_response': ai_msg.to_dict(),
        'response_text': ai_response
    }), 200


@chat_bp.route('/voice', methods=['POST'])
@jwt_required()
def voice_message():
    """
    Send a voice message to AI Farmer Assistant.
    1. Transcribes audio to text
    2. Gets AI response
    3. Returns text + optionally converts to speech
    """
    user_id = int(get_jwt_identity())

    if 'audio' not in request.files:
        return jsonify({'success': False, 'message': 'No audio file uploaded'}), 400

    audio_file = request.files['audio']
    session_id = request.form.get('session_id')
    language = request.form.get('language', 'hi')
    return_audio = request.form.get('return_audio', 'false').lower() == 'true'

    # Save audio file
    save_result = save_audio_file(audio_file, user_id)
    if not save_result['success']:
        return jsonify(save_result), 400

    audio_path = save_result['path']

    # Transcribe audio
    transcription = transcribe_audio(audio_path, language=language)

    if not transcription:
        return jsonify({
            'success': False,
            'message': 'Could not understand the audio. Please speak clearly and try again.'
        }), 400

    # Get or create session
    session = None
    if session_id:
        session = ChatSession.query.filter_by(id=session_id, user_id=user_id).first()

    if not session:
        session = ChatSession(
            user_id=user_id,
            title=transcription[:50] + '...' if len(transcription) > 50 else transcription
        )
        db.session.add(session)
        db.session.flush()

    # Get conversation history
    history = ChatMessage.query\
        .filter_by(session_id=session.id)\
        .order_by(ChatMessage.created_at.asc())\
        .limit(20)\
        .all()

    conversation_history = [
        {'role': msg.role, 'content': msg.content}
        for msg in history
    ]

    # Save user's voice message (with transcription as content)
    user_msg = ChatMessage(
        session_id=session.id,
        user_id=user_id,
        role='user',
        content=transcription,
        message_type='voice',
        audio_path=audio_path
    )
    db.session.add(user_msg)

    # Get AI response
    ai_response = get_ai_response(
        message=transcription,
        history=conversation_history,
        language=language
    )

    # TTS is handled by browser Web Speech API (free, no API needed)
    response_audio_path = None
    use_browser_tts = False
    if return_audio:
        tts_result = text_to_speech(ai_response, language=language)
        if tts_result.get('use_browser_tts'):
            use_browser_tts = True
        elif tts_result.get('success'):
            response_audio_path = tts_result['path']

    # Save AI response
    ai_msg = ChatMessage(
        session_id=session.id,
        user_id=user_id,
        role='assistant',
        content=ai_response,
        message_type='voice' if return_audio else 'text',
        audio_path=response_audio_path
    )
    db.session.add(ai_msg)
    db.session.commit()

    return jsonify({
        'success': True,
        'session_id': session.id,
        'transcription': transcription,
        'response_text': ai_response,
        'response_audio': response_audio_path,
        'use_browser_tts': use_browser_tts,
        'user_message': user_msg.to_dict(),
        'ai_response': ai_msg.to_dict()
    }), 200


@chat_bp.route('/sessions', methods=['GET'])
@jwt_required()
def get_sessions():
    """Get all chat sessions for user"""
    user_id = int(get_jwt_identity())
    sessions = ChatSession.query\
        .filter_by(user_id=user_id)\
        .order_by(ChatSession.updated_at.desc())\
        .all()

    return jsonify({
        'success': True,
        'sessions': [s.to_dict() for s in sessions]
    }), 200


@chat_bp.route('/sessions', methods=['POST'])
@jwt_required()
def create_session():
    """Create a new chat session"""
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}

    session = ChatSession(
        user_id=user_id,
        title=data.get('title', 'New Conversation')
    )
    db.session.add(session)
    db.session.commit()

    return jsonify({
        'success': True,
        'session': session.to_dict()
    }), 201


@chat_bp.route('/sessions/<int:session_id>', methods=['GET'])
@jwt_required()
def get_session_messages(session_id):
    """Get all messages in a session"""
    user_id = int(get_jwt_identity())
    session = ChatSession.query.filter_by(id=session_id, user_id=user_id).first()
    if not session:
        return jsonify({'success': False, 'message': 'Session not found'}), 404

    messages = ChatMessage.query\
        .filter_by(session_id=session_id)\
        .order_by(ChatMessage.created_at.asc())\
        .all()

    return jsonify({
        'success': True,
        'session': session.to_dict(),
        'messages': [m.to_dict() for m in messages]
    }), 200


@chat_bp.route('/sessions/<int:session_id>', methods=['DELETE'])
@jwt_required()
def delete_session(session_id):
    """Delete a chat session"""
    user_id = int(get_jwt_identity())
    session = ChatSession.query.filter_by(id=session_id, user_id=user_id).first()
    if not session:
        return jsonify({'success': False, 'message': 'Session not found'}), 404

    db.session.delete(session)
    db.session.commit()

    return jsonify({'success': True, 'message': 'Session deleted'}), 200


# ─── WebSocket Events ─────────────────────────────────────────────────────────

@socketio.on('join_chat')
def handle_join_chat(data):
    """Join a private chat room"""
    session_id = data.get('session_id')
    if session_id:
        join_room(f'chat_{session_id}')
        emit('joined', {'message': f'Joined chat session {session_id}'})


@socketio.on('send_message_ws')
def handle_ws_message(data):
    """Handle real-time message via WebSocket"""
    user_id = data.get('user_id')
    session_id = data.get('session_id')
    message = data.get('message', '').strip()
    language = data.get('language', 'hi')

    if not message or not user_id:
        emit('error', {'message': 'Invalid data'})
        return

    # Emit typing indicator
    emit('ai_typing', {'typing': True}, room=f'chat_{session_id}')

    # Get AI response (import here to avoid circular)
    from app.services.ai_service import get_ai_response
    ai_response = get_ai_response(message=message, history=[], language=language)

    # Emit response
    emit('ai_response', {
        'message': ai_response,
        'role': 'assistant'
    }, room=f'chat_{session_id}')

    emit('ai_typing', {'typing': False}, room=f'chat_{session_id}')
