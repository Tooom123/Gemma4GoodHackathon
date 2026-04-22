import { useState, useRef, useCallback } from "react";

type VoiceState = "idle" | "recording" | "transcribing" | "error";

interface UseVoiceReturn {
  state: VoiceState;
  startRecording: () => Promise<void>;
  stopRecording: () => void;
  error: string | null;
}

/**
 * Records audio via MediaRecorder, sends to /whisper/transcribe,
 * and calls onTranscript with the result.
 * Falls back to Web Speech Recognition if whisper backend is unavailable.
 */
export function useVoice(onTranscript: (text: string) => void): UseVoiceReturn {
  const [state, setState] = useState<VoiceState>("idle");
  const [error, setError] = useState<string | null>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);
  const speechRef = useRef<SpeechRecognition | null>(null);

  const startRecording = useCallback(async () => {
    setError(null);
    setState("recording");
    chunksRef.current = [];

    // Try MediaRecorder → whisper backend first
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mimeType = MediaRecorder.isTypeSupported("audio/webm;codecs=opus")
        ? "audio/webm;codecs=opus"
        : "audio/webm";
      const recorder = new MediaRecorder(stream, { mimeType });
      mediaRecorderRef.current = recorder;

      recorder.ondataavailable = (e) => {
        if (e.data.size > 0) chunksRef.current.push(e.data);
      };

      recorder.onstop = async () => {
        stream.getTracks().forEach((t) => t.stop());
        setState("transcribing");
        const blob = new Blob(chunksRef.current, { type: mimeType });
        try {
          const formData = new FormData();
          formData.append("audio", blob, "recording.webm");
          const res = await fetch("/whisper/transcribe", {
            method: "POST",
            body: formData,
          });
          if (!res.ok) throw new Error(`HTTP ${res.status}`);
          const { text } = await res.json();
          onTranscript(text);
          setState("idle");
        } catch (err) {
          // Whisper backend unavailable — fallback to Web Speech API
          _fallbackSpeech(onTranscript, setState, setError, speechRef);
        }
      };

      recorder.start();
    } catch (err) {
      // Microphone access denied or MediaRecorder unsupported
      _fallbackSpeech(onTranscript, setState, setError, speechRef);
    }
  }, [onTranscript]);

  const stopRecording = useCallback(() => {
    mediaRecorderRef.current?.stop();
    speechRef.current?.stop();
  }, []);

  return { state, startRecording, stopRecording, error };
}

function _fallbackSpeech(
  onTranscript: (text: string) => void,
  setState: (s: VoiceState) => void,
  setError: (e: string | null) => void,
  speechRef: React.MutableRefObject<SpeechRecognition | null>
) {
  const SpeechRecognition =
    (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
  if (!SpeechRecognition) {
    setError("Voix non disponible. Installez whisper.cpp ou utilisez Chrome.");
    setState("error");
    return;
  }
  const recognition: SpeechRecognition = new SpeechRecognition();
  recognition.lang = "fr-FR";
  recognition.interimResults = false;
  recognition.maxAlternatives = 1;
  speechRef.current = recognition;

  recognition.onresult = (e: SpeechRecognitionEvent) => {
    const text = e.results[0][0].transcript;
    onTranscript(text);
    setState("idle");
  };
  recognition.onerror = () => {
    setError("Reconnaissance vocale échouée.");
    setState("error");
  };
  recognition.start();
  setState("recording");
}
