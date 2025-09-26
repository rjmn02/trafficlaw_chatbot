from collections import defaultdict
from typing import List

class ConversationMemory:
    def __init__(self):
        # {user_id: [msg1, msg2, ...]}
        self.memory = defaultdict(list)

    def add_message(self, user_id: str, role: str, content: str):
        self.memory[user_id].append(f"{role}: {content}")

    def get_history(self, user_id: str) -> List[str]:
        return self.memory[user_id][-10:]  # keep last 10 messages
