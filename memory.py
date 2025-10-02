from typing import List, Optional, TypedDict
from collections import deque

class Message(TypedDict):
    role: str
    context: Optional[List[str]]
    content: str

class ConversationMemory:
    def __init__(self, max_messages: int = 20):
        self.history: deque[Message] = deque(maxlen=max_messages)

    def add_message(self, role: str, content: str, context: Optional[List[str]] = None):
        self.history.append({"role": role, "content": content, "context": context})

    def get_history(self) -> List[Message]:
        return list(self.history)

    def clear(self):
        self.history.clear()