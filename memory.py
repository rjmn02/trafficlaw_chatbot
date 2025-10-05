from typing import List


class ConversationMemory:
  def __init__(self, history=None, max_length=10):
    self.history = history if history is not None else []
    self.max_length = max_length

  def add_message(self, role: str, content: str):
    self.history.append({"role": role, "content": content})
    if len(self.history) > self.max_length:
      # dequeue the oldest message
      self.history.pop(0)

  def get_history(self) -> List[dict]:
    return self.history
