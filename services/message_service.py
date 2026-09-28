"""
services/message_service.py
Service layer for Direct Messages between classmates and peers.
Enforces strict user authorization, conversation tracking, and unread counters.
"""

from datetime import datetime, timezone
from extensions import db
from models.user import User
from models.message import DirectMessage
from sqlalchemy import or_, and_, func

def get_unread_message_count(user_id):
    """Returns total count of unread messages where user is the recipient."""
    stmt = db.select(func.count(DirectMessage.id)).where(
        DirectMessage.recipient_id == user_id,
        DirectMessage.is_read == False
    )
    return db.session.scalar(stmt) or 0

def get_user_conversations(user_id):
    """
    Returns list of active conversation threads for the user,
    summarizing classmate details, last message, and unread count.
    """
    # 1. Fetch all messages involving the user
    stmt = db.select(DirectMessage).where(
        or_(
            DirectMessage.sender_id == user_id,
            DirectMessage.recipient_id == user_id
        )
    ).order_by(DirectMessage.created_at.desc())
    
    all_msgs = db.session.execute(stmt).scalars().all()
    
    # 2. Group by peer user id
    peer_map = {}
    for msg in all_msgs:
        peer_id = msg.recipient_id if str(msg.sender_id) == str(user_id) else msg.sender_id
        peer_id_str = str(peer_id)
        if peer_id_str not in peer_map:
            peer_map[peer_id_str] = {
                'peer_id': peer_id,
                'last_message': msg,
                'unread_count': 0
            }
        # Count unread if message was sent by peer to current user
        if str(msg.recipient_id) == str(user_id) and not msg.is_read:
            peer_map[peer_id_str]['unread_count'] += 1

    # 3. Fetch peer user objects
    conversations = []
    for peer_id_str, info in peer_map.items():
        peer = db.session.get(User, info['peer_id'])
        if peer:
            last_msg = info['last_message']
            conversations.append({
                'peer': {
                    'id': str(peer.id),
                    'fullname': peer.fullname,
                    'email': peer.email,
                    'avatar_url': peer.avatar_url,
                    'role': peer.role,
                    'education_level': getattr(peer, 'education_level', 'university') or 'university'
                },
                'last_message': {
                    'content': last_msg.content,
                    'created_at': last_msg.created_at.isoformat() if last_msg.created_at else None,
                    'timestamp_formatted': last_msg.created_at.strftime('%b %d, %H:%M') if last_msg.created_at else '',
                    'is_mine': str(last_msg.sender_id) == str(user_id)
                },
                'unread_count': info['unread_count']
            })

    # Sort conversations by last message timestamp descending
    conversations.sort(
        key=lambda x: x['last_message']['created_at'] or '', 
        reverse=True
    )
    return conversations

def get_conversation_thread(user_id, classmate_email_or_id):
    """
    Fetches full message thread between user and a specific classmate.
    Automatically marks incoming messages from that classmate as read.
    """
    query_val = str(classmate_email_or_id).strip()
    
    # Find classmate by email or by ID
    classmate = None
    if '@' in query_val:
        classmate = db.session.execute(
            db.select(User).where(func.lower(User.email) == query_val.lower())
        ).scalar_one_or_none()
    else:
        try:
            classmate = db.session.get(User, query_val)
        except Exception:
            classmate = None

    if not classmate:
        return None, "Classmate not found. Please verify the email address."

    if str(classmate.id) == str(user_id):
        return None, "You cannot chat with yourself."

    # Fetch chronological messages between the two users
    stmt = db.select(DirectMessage).where(
        or_(
            and_(DirectMessage.sender_id == user_id, DirectMessage.recipient_id == classmate.id),
            and_(DirectMessage.sender_id == classmate.id, DirectMessage.recipient_id == user_id)
        )
    ).order_by(DirectMessage.created_at.asc())

    messages = db.session.execute(stmt).scalars().all()

    # Mark incoming unread messages as read
    marked_count = 0
    for msg in messages:
        if str(msg.recipient_id) == str(user_id) and not msg.is_read:
            msg.is_read = True
            marked_count += 1

    if marked_count > 0:
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()

    message_dicts = [m.to_dict(current_user_id=user_id) for m in messages]
    
    classmate_info = {
        'id': str(classmate.id),
        'fullname': classmate.fullname,
        'email': classmate.email,
        'avatar_url': classmate.avatar_url,
        'role': classmate.role,
        'education_level': getattr(classmate, 'education_level', 'university') or 'university'
    }

    return {
        'classmate': classmate_info,
        'peer': classmate_info,
        'messages': message_dicts
    }, None

def send_direct_message(sender_id, recipient_email_or_id, content):
    """
    Creates and commits a new direct message from sender to recipient.
    """
    cleaned_content = (content or '').strip()
    if not cleaned_content:
        return None, "Message content cannot be empty."

    if len(cleaned_content) > 3000:
        return None, "Message is too long (maximum 3000 characters)."

    query_val = str(recipient_email_or_id).strip()
    recipient = None
    if '@' in query_val:
        recipient = db.session.execute(
            db.select(User).where(func.lower(User.email) == query_val.lower())
        ).scalar_one_or_none()
    else:
        try:
            recipient = db.session.get(User, query_val)
        except Exception:
            recipient = None

    if not recipient:
        return None, "Recipient not found. Please verify the email address."

    if str(recipient.id) == str(sender_id):
        return None, "You cannot send messages to yourself."

    try:
        new_msg = DirectMessage(
            sender_id=sender_id,
            recipient_id=recipient.id,
            content=cleaned_content,
            is_read=False,
            created_at=datetime.now(timezone.utc)
        )
        db.session.add(new_msg)
        db.session.commit()
        return new_msg.to_dict(current_user_id=sender_id), None
    except Exception as e:
        db.session.rollback()
        return None, f"Failed to send message: {str(e)}"

def search_classmates(current_user_id, query_str):
    """Searches registered users by email or fullname matching query_str."""
    q = (query_str or '').strip().lower()
    if not q:
        return []

    stmt = db.select(User).where(
        and_(
            User.id != current_user_id,
            or_(
                func.lower(User.email).like(f"%{q}%"),
                func.lower(User.fullname).like(f"%{q}%"),
                func.lower(User.username).like(f"%{q}%")
            )
        )
    ).limit(8)

    users = db.session.execute(stmt).scalars().all()
    return [{
        'id': str(u.id),
        'fullname': u.fullname,
        'email': u.email,
        'avatar_url': u.avatar_url,
        'role': u.role,
        'education_level': getattr(u, 'education_level', 'university') or 'university'
    } for u in users]
