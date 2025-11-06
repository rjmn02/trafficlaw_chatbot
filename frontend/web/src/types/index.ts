export type ChatMessage = { 
  role: "user" | "assistant"; 
  content: string;
  timestamp?: number; // Unix timestamp in milliseconds
};

export type StoredSession = { 
  id: string; 
  title: string; 
  messages: ChatMessage[]; 
  updatedAt: number;
};

