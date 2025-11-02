export type ChatMessage = { 
  role: "user" | "assistant"; 
  content: string;
};

export type StoredSession = { 
  id: string; 
  title: string; 
  messages: ChatMessage[]; 
  updatedAt: number;
};

