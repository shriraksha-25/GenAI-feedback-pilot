import pytest
from backend.services import chat_service

class FakeDb:
    def __init__(self): self.features = self; self.feature_evidence = self; self.feedback = self
    def find(self, query): return self
    def limit(self, n): return self
    def __aiter__(self):
        async def iterator():
            if False: yield {}
        return iterator()

@pytest.mark.asyncio
async def test_chat_calls_ai_service_and_preserves_response(monkeypatch):
    monkeypatch.setattr(chat_service, "get_database", lambda: FakeDb())
    conversations, stored_messages = {}, {}
    async def create_conversation(c):
        conversations[c.conversation_id] = c.model_dump(); return conversations[c.conversation_id]
    async def get_conversation(cid): return conversations.get(cid)
    async def get_messages(cid, limit=30): return list(stored_messages.get(cid, []))
    async def add_message(m):
        assert m.conversation_id in conversations
        stored_messages.setdefault(m.conversation_id, []).append(m.model_dump()); return m.model_dump()
    monkeypatch.setattr(chat_service, "create_conversation", create_conversation)
    monkeypatch.setattr(chat_service, "get_conversation", get_conversation)
    monkeypatch.setattr(chat_service, "get_conversation_messages", get_messages)
    monkeypatch.setattr(chat_service, "add_chat_message", add_message)
    captured = {}
    def fake_ask(question, context):
        captured.update(question=question, context=context)
        return {"status": "completed", "answer": "Customers reported upload failures.", "grounded": True, "referenced_feedback_ids": ["fb-1"], "confidence": 0.8}
    monkeypatch.setattr(chat_service, "ask_assistant", fake_ask)
    result = await chat_service.chat_with_assistant(question="What are the main issues?", workspace_id="ws-1", user_id="u-1")
    assert result["status"] == "completed"
    assert result["answer"] == "Customers reported upload failures."
    assert result["referenced_feedback_ids"] == ["fb-1"]
    assert result["conversation_id"] and len(result["messages"]) == 2
    assert "Current user question" in captured["question"]
    assert captured["context"]["supporting_evidence"] == []

@pytest.mark.asyncio
async def test_chat_returns_graceful_unavailable_context_answer(monkeypatch):
    monkeypatch.setattr(chat_service, "get_database", lambda: FakeDb())
    conversations, stored_messages = {}, {}
    async def create_conversation(c): conversations[c.conversation_id] = c.model_dump(); return conversations[c.conversation_id]
    async def get_conversation(cid): return conversations.get(cid)
    async def get_messages(cid, limit=30): return list(stored_messages.get(cid, []))
    async def add_message(m): stored_messages.setdefault(m.conversation_id, []).append(m.model_dump()); return m.model_dump()
    monkeypatch.setattr(chat_service, "create_conversation", create_conversation)
    monkeypatch.setattr(chat_service, "get_conversation", get_conversation)
    monkeypatch.setattr(chat_service, "get_conversation_messages", get_messages)
    monkeypatch.setattr(chat_service, "add_chat_message", add_message)
    monkeypatch.setattr(chat_service, "ask_assistant", lambda q, c: {"status": "completed", "answer": "This information is not available in the current project context.", "grounded": False, "referenced_feedback_ids": [], "confidence": 0.9})
    result = await chat_service.chat_with_assistant(question="What is our market share?", workspace_id="ws-1", user_id="u-1")
    assert result["status"] == "completed" and result["grounded"] is False
    assert result["referenced_feedback_ids"] == [] and "not available" in result["answer"]
