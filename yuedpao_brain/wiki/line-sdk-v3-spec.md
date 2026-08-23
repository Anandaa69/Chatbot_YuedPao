---
title: LINE Messaging API SDK v3 Specification
date: 2026-08-23
tags: [line-bot, sdk-v3, python, pydantic, async]
sources: ["sources/ออกแบบฟังก์ชัน LINE Chatbot สำหรับ Yuedpao.md"]
---

# 💬 LINE Messaging API SDK v3 Enforcement Specification

Backlink: [[index]]

---

## 📌 Architectural Decision Rationale (ADR)

Chatbot Yuedpao strictly enforces the use of **LINE Messaging API Python SDK v3 (`line-bot-sdk >= 3.0.0`)**.

Legacy versions (v1/v2) are deprecated by LINE Corporation and lack modern OpenAPI type annotations, async support, and updated Flex Message validation.

---

## ⚙️ Key Technical Enhancements in SDK v3

### 1. Modular API Clients & Async Support
SDK v3 separates monolithic clients into specialized, lightweight API modules:
- `linebot.v3.messaging.MessagingApi`: Core messaging API client (push, reply, broadcast).
- `linebot.v3.messaging.AsyncMessagingApi`: Asynchronous client optimized for **FastAPI async webhooks**.
- `linebot.v3.messaging.MessagingApiBlob`: Media/image/voice attachment retrieval.

### 2. Pydantic-based Flex Message Models
All Flex Message UI components in `app/views/` use strict SDK v3 Pydantic models to prevent malformed JSON errors:

```python
from linebot.v3.messaging import (
    FlexMessage,
    FlexContainer,
    TextMessage,
    QuickReply,
    QuickReplyItem,
    PostbackAction
)
```

### 3. Robust Webhook Parsing
Event handling in `app/controllers/webhook_controller.py` uses `WebhookParser` with strong typing:

```python
from linebot.v3.webhook import WebhookParser
from linebot.v3.webhooks import MessageEvent, PostbackEvent, TextMessageContent
```

---

## 📊 SDK Version Comparison Matrix

| Feature | Legacy SDK (v1 / v2) | **Enforced SDK v3 (`line-bot-sdk >= 3.0.0`)** |
|---|---|---|
| **API Specs** | Deprecated Custom Spec | **Official OpenAPI Specs** |
| **Async Support** | ❌ Sync Only | ⚡ **Async & Sync Supported (`AsyncMessagingApi`)** |
| **Type Hints** | 🔴 Minimal / None | 🟢 **Full Pydantic Type Hints & Autocomplete** |
| **Flex Message Validation** | Runtime Error on LINE Server | **Compile/Type Checking before sending** |
| **Maintenance** | Sunset / EOL | **Actively Maintained by LINE Team** |

---

## 🔗 Related Knowledge Pages
- [[project-architecture]] — Codebase Architecture blueprint.
- [[core-features-rich-menu]] — Rich Menu and Flex Message specifications.
- [[rubric-evaluation-checkpoints]] — Flex Message JSON validation rubrics (15%).
