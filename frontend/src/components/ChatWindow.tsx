import { useEffect, useRef, useState } from "react";
import { useOllama, type Message } from "../hooks/useOllama";
import { VoiceButton } from "./VoiceButton";
import { FeedbackPanel } from "./FeedbackPanel";
import { extractPedagogy, hasFeedback, type PedagogyBlock } from "../utils/pedagogy";

interface Props {
  systemPrompt: string;
  scenarioTitle: string;
  model?: string;
}

interface DisplayMessage {
  role: "user" | "assistant";
  text: string;
  pedagogy?: PedagogyBlock | null;
}

function MessageBubble({ msg }: { msg: DisplayMessage }) {
  const isUser = msg.role === "user";
  return (
    <div className={`flex flex-col ${isUser ? "items-end" : "items-start"} mb-3`}>
      <div
        className={`max-w-[75%] rounded-2xl px-4 py-3 text-sm leading-relaxed whitespace-pre-wrap ${
          isUser
            ? "bg-blue-600 text-white rounded-br-sm"
            : "bg-gray-100 text-gray-900 rounded-bl-sm"
        }`}
      >
        {msg.text || <span className="opacity-50 italic">…</span>}
      </div>
      {!isUser && msg.pedagogy && hasFeedback(msg.pedagogy) && (
        <div className="w-full max-w-[75%] mt-1">
          <FeedbackPanel pedagogy={msg.pedagogy} />
        </div>
      )}
    </div>
  );
}

/** Extract pedagogy from completed assistant messages, leave streaming ones untouched. */
function toDisplayMessages(
  messages: Message[],
  isStreaming: boolean
): DisplayMessage[] {
  return messages
    .filter((m) => m.role !== "system")
    .map((m, i, arr) => {
      const isLastAssistant =
        m.role === "assistant" && i === arr.length - 1 && isStreaming;
      if (m.role === "assistant" && !isLastAssistant) {
        const { cleanText, pedagogy } = extractPedagogy(m.content);
        return { role: "assistant", text: cleanText, pedagogy };
      }
      return { role: m.role as "user" | "assistant", text: m.content };
    });
}

export function ChatWindow({ systemPrompt, scenarioTitle, model }: Props) {
  const { messages, isStreaming, error, sendMessage, clearMessages, abort } =
    useOllama({ model });

  const [input, setInput] = useState("");
  const bottomRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = async () => {
    const text = input.trim();
    if (!text || isStreaming) return;
    setInput("");
    textareaRef.current?.focus();
    await sendMessage(text, messages.length === 0 ? systemPrompt : undefined);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleTranscript = (text: string) => {
    setInput((prev) => (prev ? prev + " " + text : text));
    textareaRef.current?.focus();
  };

  const displayMessages = toDisplayMessages(messages, isStreaming);

  return (
    <div className="flex flex-col h-full bg-white rounded-2xl shadow-lg overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between px-5 py-4 border-b border-gray-200 bg-blue-700 text-white">
        <div>
          <p className="text-xs uppercase tracking-widest opacity-70">Simulation</p>
          <h2 className="font-semibold text-base">{scenarioTitle}</h2>
        </div>
        <button
          onClick={() => { abort(); clearMessages(); }}
          className="text-xs opacity-70 hover:opacity-100 underline"
        >
          Recommencer
        </button>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-4 py-4">
        {displayMessages.length === 0 && (
          <p className="text-center text-gray-400 text-sm mt-10">
            Commencez la conversation — dites bonjour !
          </p>
        )}
        {displayMessages.map((msg, i) => (
          <MessageBubble key={i} msg={msg} />
        ))}
        {error && (
          <p className="text-red-500 text-sm text-center mt-2">{error}</p>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <div className="px-4 py-3 border-t border-gray-200 flex gap-2 items-end">
        <VoiceButton onTranscript={handleTranscript} disabled={isStreaming} />
        <textarea
          ref={textareaRef}
          rows={1}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Écrivez ou parlez… (Entrée pour envoyer)"
          disabled={isStreaming}
          className="flex-1 resize-none rounded-xl border border-gray-300 px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
        />
        {isStreaming ? (
          <button
            onClick={abort}
            className="shrink-0 rounded-xl bg-red-500 text-white px-4 py-2 text-sm font-medium hover:bg-red-600"
          >
            Stop
          </button>
        ) : (
          <button
            onClick={handleSend}
            disabled={!input.trim()}
            className="shrink-0 rounded-xl bg-blue-600 text-white px-4 py-2 text-sm font-medium hover:bg-blue-700 disabled:opacity-40"
          >
            Envoyer
          </button>
        )}
      </div>
    </div>
  );
}
