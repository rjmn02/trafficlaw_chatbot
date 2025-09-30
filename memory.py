from typing import List, Dict

class ConversationMemory:
  def __init__(self):
    self.history: List[Dict[str, str, str]] = []

  def add_message(self, role: str, content: str, context: str = None):
    self.history.append({"role": role, "content": content, "context": context})

  def get_history(self):
    return self.history