"""
Flask Webhook Controller for LINE Bot SDK v3 (YuedPao Chatbot)
Handles /callback endpoint, X-Line-Signature validation, and dispatches events via TieredRouter.
"""

from flask import Blueprint, request, abort, jsonify
from typing import Dict, Any

try:
    from linebot.v3 import WebhookHandler
    from linebot.v3.exceptions import InvalidSignatureError
    from linebot.v3.messaging import (
        Configuration,
        ApiClient,
        MessagingApi,
        ReplyMessageRequest,
        TextMessage,
        FlexMessage,
        FlexContainer,
        QuickReply,
        QuickReplyItem,
        MessageAction,
    )
    from linebot.v3.webhooks import MessageEvent, TextMessageContent, PostbackEvent
except ImportError:
    WebhookHandler = None

from app.config import LINE_CHANNEL_SECRET, LINE_CHANNEL_ACCESS_TOKEN
from app.services.tiered_router import TieredRouter
from app.views.rich_menu_views import get_rich_menu_postback_query

webhook_bp = Blueprint("webhook", __name__)
router = TieredRouter()

# Initialize LINE Bot SDK v3 Objects
handler = WebhookHandler(LINE_CHANNEL_SECRET) if LINE_CHANNEL_SECRET and WebhookHandler else None
configuration = Configuration(access_token=LINE_CHANNEL_ACCESS_TOKEN) if LINE_CHANNEL_ACCESS_TOKEN else None


def convert_flex_and_quick_replies(res: Dict[str, Any]) -> tuple:
    """Helper to build linebot.v3 Message objects from router dictionary output."""
    messages = []
    
    # 1. Text Message
    reply_text = res.get("reply_text", "")
    
    # 2. Flex Message if available
    flex_json = res.get("flex_payload")
    if flex_json:
        try:
            container = FlexContainer.from_dict(flex_json)
            flex_msg = FlexMessage(
                alt_text=reply_text or "แชตบอตส่งข้อมูลสินค้าให้คุณ",
                contents=container
            )
            messages.append(flex_msg)
        except Exception as e:
            print(f"⚠️ Error constructing FlexMessage: {e}")
            messages.append(TextMessage(text=reply_text))
    else:
        messages.append(TextMessage(text=reply_text or "สวัสดีครับ ยินดีต้อนรับสู่ YuedPao Chatbot!"))

    # 3. Quick Reply items
    qr_data = res.get("quick_replies", {}).get("items", [])
    qr_items = []
    for item in qr_data:
        action = item.get("action", {})
        qr_items.append(
            QuickReplyItem(
                action=MessageAction(
                    label=action.get("label", "กดที่นี่"),
                    text=action.get("text", "ช่วยเหลือ")
                )
            )
        )
    
    if qr_items and messages:
        messages[-1].quick_reply = QuickReply(items=qr_items)
        
    return messages


@webhook_bp.route("/callback", methods=["POST"])
def callback():
    """
    LINE Webhook HTTP POST Endpoint
    Validates X-Line-Signature header and processes incoming events.
    """
    signature = request.headers.get("X-Line-Signature", "")
    body = request.get_data(as_text=True)

    # Mock mode handling for local testing / test suite without real LINE keys
    if not LINE_CHANNEL_SECRET or LINE_CHANNEL_SECRET == "MOCK_SECRET":
        try:
            payload = request.get_json(force=True, silent=True) or {}
            events = payload.get("events", [])
            results = []
            for event in events:
                if event.get("type") == "message" and event.get("message", {}).get("type") == "text":
                    user_text = event["message"]["text"]
                    user_id = event.get("source", {}).get("userId", "default_user")
                    res = router.route_query(user_text, user_id=user_id)
                    results.append(res)
            return jsonify({"status": "success", "mock_results": results}), 200
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 400

    if not handler:
        return jsonify({"status": "error", "message": "WebhookHandler not configured"}), 500

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("❌ Invalid signature. Check your channel secret.")
        abort(400)
    except Exception as e:
        print(f"⚠️ Webhook handle error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

    return "OK", 200


if handler:
    @handler.add(MessageEvent, message=TextMessageContent)
    def handle_message_event(event):
        user_text = event.message.text
        reply_token = event.reply_token
        user_id = getattr(event.source, "user_id", "default_user") if hasattr(event, "source") else "default_user"
        
        # Route query through 4-Tier Router
        res = router.route_query(user_text, user_id=user_id)
        line_messages = convert_flex_and_quick_replies(res)
        
        if configuration and reply_token:
            with ApiClient(configuration) as api_client:
                line_bot_api = MessagingApi(api_client)
                line_bot_api.reply_message(
                    ReplyMessageRequest(
                        reply_token=reply_token,
                        messages=line_messages
                    )
                )


    @handler.add(PostbackEvent)
    def handle_postback_event(event):
        postback_data = event.postback.data
        reply_token = event.reply_token
        user_id = getattr(event.source, "user_id", "default_user") if hasattr(event, "source") else "default_user"
        
        # Map Rich Menu postback action IDs to Thai query text
        query_text = get_rich_menu_postback_query(postback_data)
        res = router.route_query(query_text, user_id=user_id)
        line_messages = convert_flex_and_quick_replies(res)
        
        if configuration and reply_token:
            with ApiClient(configuration) as api_client:
                line_bot_api = MessagingApi(api_client)
                line_bot_api.reply_message(
                    ReplyMessageRequest(
                        reply_token=reply_token,
                        messages=line_messages
                    )
                )
