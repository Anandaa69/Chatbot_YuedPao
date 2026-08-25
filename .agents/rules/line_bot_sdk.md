# 💬 LINE Messaging API SDK v3 Enforcement Rules - Chatbot Yuedpao

## 1. Mandatory SDK Version Policy
- **Strict Requirement**: Always use **`line-bot-sdk >= 3.0.0`** (Python SDK v3). Legacy versions (v1 / v2) are strictly prohibited.
- **Asynchronous Execution**: Always use `linebot.v3.messaging.AsyncMessagingApi` for sending push/reply messages within FastAPI async routes to guarantee non-blocking sub-second latency.

## 2. Flex Message & UI Validation Rules
- **Pydantic Models**: All Flex Message builders in `app/views/` must construct JSON components using SDK v3 Pydantic models:
  ```python
  from linebot.v3.messaging import (
      FlexMessage,
      FlexContainer,
      FlexBubble,
      FlexCarousel,
      QuickReply,
      QuickReplyItem,
      PostbackAction,
      URIAction
  )
  ```
- **Flex Constraints**:
  - Enforce `aspectRatio: "1:1"` (square) or `"4:3"` (landscape) on image components.
  - Enforce `maxLines: 2` on text elements to prevent card height misalignment.

## 3. Webhook Parsing Rules
- Handlers in `app/controllers/webhook_controller.py` must use `linebot.v3.webhook.WebhookParser` and strongly typed events (`MessageEvent`, `PostbackEvent`, `TextMessageContent`).
