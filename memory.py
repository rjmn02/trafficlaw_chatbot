from typing import List, Optional, TypedDict
from collections import deque


class Message(TypedDict):
    role: str       # "user" or "assistant"
    content: str    # what was said
    context: Optional[str]  # retrieved docs / metadata if any


class ConversationMemory:
    def __init__(self, max_messages: int = 20):
        # Keep only the most recent messages (10 exchanges = 20 messages)
        self.history: deque[Message] = deque(maxlen=max_messages)

    def add_message(self, role: str, content: str, context: Optional[str] = None):
        self.history.append({"role": role, "content": content, "context": context})

    def get_history(self) -> List[Message]:
        return list(self.history)
