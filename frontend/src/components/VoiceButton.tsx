import { useVoice } from "../hooks/useVoice";

interface Props {
  onTranscript: (text: string) => void;
  disabled?: boolean;
}

export function VoiceButton({ onTranscript, disabled }: Props) {
  const { state, startRecording, stopRecording, error } = useVoice(onTranscript);

  const isRecording = state === "recording";
  const isTranscribing = state === "transcribing";
  const isBusy = isRecording || isTranscribing;

  const handleClick = () => {
    if (isRecording) stopRecording();
    else startRecording();
  };

  return (
    <div className="relative">
      <button
        onClick={handleClick}
        disabled={disabled || isTranscribing}
        title={
          isRecording
            ? "Cliquez pour arrêter l'enregistrement"
            : isTranscribing
            ? "Transcription en cours…"
            : "Parler (voix)"
        }
        className={`w-10 h-10 rounded-full flex items-center justify-center transition-all shrink-0
          ${isRecording
            ? "bg-red-500 animate-pulse shadow-lg shadow-red-300"
            : isTranscribing
            ? "bg-yellow-400 cursor-wait"
            : "bg-gray-100 hover:bg-gray-200 text-gray-600"
          } disabled:opacity-40`}
      >
        {isTranscribing ? (
          <span className="text-xs font-bold text-white">…</span>
        ) : (
          <MicIcon active={isRecording} />
        )}
      </button>
      {error && (
        <p className="absolute bottom-full mb-1 left-1/2 -translate-x-1/2 text-xs text-red-500 whitespace-nowrap bg-white px-2 py-1 rounded shadow">
          {error}
        </p>
      )}
    </div>
  );
}

function MicIcon({ active }: { active: boolean }) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      className={`w-5 h-5 ${active ? "text-white" : "text-gray-600"}`}
      viewBox="0 0 24 24"
      fill="currentColor"
    >
      <path d="M12 1a4 4 0 0 1 4 4v6a4 4 0 0 1-8 0V5a4 4 0 0 1 4-4zm-1.5 14.93A7.001 7.001 0 0 1 5 9H3a9 9 0 0 0 8 8.94V21H9v2h6v-2h-2v-2.06A9 9 0 0 0 21 9h-2a7 7 0 0 1-5.5 6.93z"/>
    </svg>
  );
}
