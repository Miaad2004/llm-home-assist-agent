import { useEffect, useRef } from "react";

type WakeSpeechOptions = {
  phrase: string;
  onWake: () => void;
};

export function useWakeSpeech({ phrase, onWake }: WakeSpeechOptions) {
  const recognitionRef = useRef<SpeechRecognition | null>(null);

  useEffect(() => {
    const SpeechRecognition =
      (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;

    if (!SpeechRecognition) {
      console.warn("Web Speech API not supported in this browser.");
      return;
    }

    const recog: SpeechRecognition = new SpeechRecognition();
    recog.continuous = true;
    recog.interimResults = false;
    recog.lang = "en-US";

    recog.onresult = (event: SpeechRecognitionEvent) => {
      for (let i = event.resultIndex; i < event.results.length; i++) {
        if (event.results[i].isFinal) {
          const text = event.results[i][0].transcript.trim().toLowerCase();
          console.log("🗣️ Detected:", text);
          if (text.includes(phrase.toLowerCase())) {
            console.log("🔔 Wake phrase detected:", phrase);
            onWake();
          }
        }
      }
    };

    recog.onerror = (e) => {
      console.error("SpeechRecognition error:", e);
    };

    recog.onend = () => {
      // Restart on end
      recog.start();
    };

    recog.start();
    recognitionRef.current = recog;

    return () => {
      recog.onend = null;
      recog.onresult = null;
      recog.onerror = null;
      recog.stop();
    };
  }, [phrase, onWake]);
}
