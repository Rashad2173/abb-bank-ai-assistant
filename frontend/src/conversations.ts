// Conversations kept in this browser (like any chatbot's sidebar).
// localStorage is a convenience here: if it is unavailable the chat still works,
// conversations just do not survive a reload.

import { useEffect, useState } from "react";

import type { ChatResponse } from "./types";

export interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  quote?: string;
  response?: ChatResponse;
  error?: string;
}

export interface Conversation {
  id: string;
  title: string;
  updatedAt: string;
  messages: Message[];
}

const KEY = "abb.conversations.v1";
const MAX_CONVERSATIONS = 30;
const TITLE_LENGTH = 60;

function load(): Conversation[] {
  try {
    return JSON.parse(localStorage.getItem(KEY) ?? "[]") as Conversation[];
  } catch {
    return [];
  }
}

export function newConversation(): Conversation {
  return { id: crypto.randomUUID(), title: "", updatedAt: new Date().toISOString(), messages: [] };
}

export function titleOf(question: string): string {
  const text = question.trim().replace(/\s+/g, " ");
  return text.length > TITLE_LENGTH ? `${text.slice(0, TITLE_LENGTH - 1)}…` : text;
}

export function useConversations() {
  const [conversations, setConversations] = useState<Conversation[]>(() => {
    const stored = load();
    return stored.length ? stored : [newConversation()];
  });
  const [activeId, setActiveId] = useState(() => conversations[0].id);

  useEffect(() => {
    try {
      // Empty conversations are not worth keeping.
      const kept = conversations.filter((c) => c.messages.length).slice(0, MAX_CONVERSATIONS);
      localStorage.setItem(KEY, JSON.stringify(kept));
    } catch {
      /* storage full or blocked — conversations stay in memory */
    }
  }, [conversations]);

  const active = conversations.find((c) => c.id === activeId) ?? conversations[0];

  /** Appends a message to a conversation and moves it to the top of the list. */
  function append(conversationId: string, message: Message) {
    setConversations((all) => {
      const target = all.find((c) => c.id === conversationId);
      if (!target) return all;
      const updated: Conversation = {
        ...target,
        title: target.title || (message.role === "user" ? titleOf(message.content) : ""),
        updatedAt: new Date().toISOString(),
        messages: [...target.messages, message],
      };
      return [updated, ...all.filter((c) => c.id !== conversationId)];
    });
  }

  function start() {
    if (!active.messages.length) return; // already on an empty conversation
    const fresh = newConversation();
    setConversations((all) => [fresh, ...all]);
    setActiveId(fresh.id);
  }

  function remove(id: string) {
    setConversations((all) => {
      const rest = all.filter((c) => c.id !== id);
      const next = rest.length ? rest : [newConversation()];
      if (id === activeId) setActiveId(next[0].id);
      return next;
    });
  }

  return { conversations, active, select: setActiveId, append, start, remove };
}
