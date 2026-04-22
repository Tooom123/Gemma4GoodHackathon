import { useState, useCallback, useRef } from "react";

export interface Message {
  role: "user" | "assistant" | "system";
  content: string;
}

interface UseOllamaOptions {
  model?: string;
  temperature?: number;
}

interface UseOllamaReturn {
  messages: Message[];
  isStreaming: boolean;
  error: string | null;
  sendMessage: (userText: string, systemPrompt?: string) => Promise<void>;
  clearMessages: () => void;
  abort: () => void;
}

const API_BASE = "/chat";

export function useOllama(options: UseOllamaOptions = {}): UseOllamaReturn {
  const { model = "gemma4:e4b", temperature = 0.7 } = options;

  const [messages, setMessages] = useState<Message[]>([]);
  const [isStreaming, setIsStreaming] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const abortRef = useRef<AbortController | null>(null);

  const sendMessage = useCallback(
    async (userText: string, systemPrompt?: string) => {
      setError(null);

      const userMessage: Message = { role: "user", content: userText };
      const history: Message[] = systemPrompt
        ? [{ role: "system", content: systemPrompt }, ...messages, userMessage]
        : [...messages, userMessage];

      setMessages((prev) => [...prev, userMessage]);
      setIsStreaming(true);

      abortRef.current = new AbortController();

      try {
        const response = await fetch(`${API_BASE}/stream`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ messages: history, model, temperature }),
          signal: abortRef.current.signal,
        });

        if (!response.ok) {
          const err = await response.json().catch(() => ({}));
          throw new Error(err.detail ?? `HTTP ${response.status}`);
        }

        if (!response.body) throw new Error("No response body");

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let assistantContent = "";

        // Add empty assistant message to fill incrementally
        setMessages((prev) => [
          ...prev,
          { role: "assistant", content: "" },
        ]);

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          const text = decoder.decode(value, { stream: true });
          const lines = text.split("\n");

          for (const line of lines) {
            if (!line.startsWith("data: ")) continue;
            const payload = JSON.parse(line.slice(6));
            if (payload.error) {
              setError(payload.error);
              break;
            }
            if (payload.done) break;
            assistantContent += payload.content;
            setMessages((prev) => {
              const updated = [...prev];
              updated[updated.length - 1] = {
                role: "assistant",
                content: assistantContent,
              };
              return updated;
            });
          }
        }
      } catch (err) {
        if (err instanceof Error && err.name === "AbortError") return;
        setError(err instanceof Error ? err.message : "Unknown error");
        // Remove the empty assistant placeholder on error
        setMessages((prev) =>
          prev[prev.length - 1]?.content === ""
            ? prev.slice(0, -1)
            : prev
        );
      } finally {
        setIsStreaming(false);
        abortRef.current = null;
      }
    },
    [messages, model, temperature]
  );

  const clearMessages = useCallback(() => {
    setMessages([]);
    setError(null);
  }, []);

  const abort = useCallback(() => {
    abortRef.current?.abort();
    setIsStreaming(false);
  }, []);

  return { messages, isStreaming, error, sendMessage, clearMessages, abort };
}
