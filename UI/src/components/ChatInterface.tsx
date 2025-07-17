
import { useState, useEffect, useRef, forwardRef, useImperativeHandle } from 'react';
import { Send, MicIcon, Trash2, Volume2, Mic, Square } from 'lucide-react';
import { cn } from '@/lib/utils';
import { useToast } from '@/hooks/use-toast';
import CopyButton from './CopyButton';
import ReactMarkdown from 'react-markdown';


interface ChatMessage {
  id: string;
  text: string;
  isUser: boolean;
  timestamp: Date;
}

interface HistoryMessage {
  role: string;
  content: string;
}

interface ChatInterfaceProps {
  language: 'en' | 'fa';
  onDeviceRefresh?: () => void;
}

const ChatInterface = forwardRef<{ refreshDevices: () => void }, ChatInterfaceProps>(({ language, onDeviceRefresh }, ref) => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputText, setInputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isLoadingHistory, setIsLoadingHistory] = useState(true);
  const [playingMessageId, setPlayingMessageId] = useState<string | null>(null);
  const [isRecording, setIsRecording] = useState(false);
  const [isTranscribing, setIsTranscribing] = useState(false);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const chatContainerRef = useRef<HTMLDivElement>(null);
  const { toast } = useToast();
  const wakeTriggeredRef = useRef(false);

  useImperativeHandle(ref, () => ({
    refreshDevices: () => {
      if (onDeviceRefresh) {
        onDeviceRefresh();
      }
    }
  }));

  // Auto-scroll to bottom function
  const scrollToBottom = () => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
    }
  };

  // Auto-scroll when messages change
  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading, isRecording, isTranscribing]);

  const text = {
    en: {
      title: 'Assistant Chat',
      placeholder: 'Type your message or use voice...',
      send: 'Send',
      error: 'Sorry, I encountered an error. Please try again.',
      sending: 'Sending...',
      clearHistory: 'Clear Chat History',
      loadingHistory: 'Loading chat history...',
      voiceInput: 'Voice input',
      voiceInputFailed: 'Voice input failed',
      transcribing: 'Transcribing...',
      recording: 'Recording...',
      stopRecording: 'Stop recording',
      microphonePermissionDenied: 'Microphone permission denied',
      microphoneError: 'Microphone access error',
      readMessage: 'Read Message'
    },
    fa: {
      title: 'گفتگو با دستیار',
      placeholder: 'پیام خود را تایپ کنید یا از صدا استفاده کنید...',
      send: 'ارسال',
      error: 'متاسفم، خطایی رخ داد. لطفا دوباره تلاش کنید.',
      sending: 'در حال ارسال...',
      clearHistory: 'پاک کردن تاریخچه گفتگو',
      loadingHistory: 'در حال بارگذاری تاریخچه گفتگو...',
      voiceInput: 'ورودی صوتی',
      voiceInputFailed: 'ورودی صوتی ناموفق بود',
      transcribing: 'در حال تبدیل صدا به متن...',
      recording: 'در حال ضبط...',
      stopRecording: 'توقف ضبط',
      microphonePermissionDenied: 'دسترسی به میکروفون رد شد',
      microphoneError: 'خطا در دسترسی به میکروفون',
      readMessage: 'خواندن پیام'
    }
  };


useEffect(() => {
  const loadHistory = async () => {
    try {
      console.log('Loading chat history from /llm/history...');
      
      const response = await fetch('http://localhost:8000/llm/history', {
        method: 'GET',
        headers: {
          'Accept': 'application/json',
        },
      });

      console.log('History response status:', response.status);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      console.log('History data:', data);

      if (data.history && Array.isArray(data.history)) {
        const chatMessages: ChatMessage[] = data.history
          .filter((msg: HistoryMessage) =>
            (msg.role === 'user' || msg.role === 'assistant') && msg.content && msg.content.trim() !== ''
            )
          .map((msg: HistoryMessage, index: number) => ({
            id: `history-${index}`,
            text: msg.content,
            isUser: msg.role === 'user',
            timestamp: new Date()
          }));
        
        setMessages(chatMessages);
        console.log('Loaded', chatMessages.length, 'messages from history');
      } else {
        console.log('No valid history found, starting with empty chat');
        setMessages([]);
      }
    } catch (error) {
      console.error('Error loading chat history:', error);

      const welcomeMessage: ChatMessage = {
        id: '1',
        text: language === 'en' 
          ? 'Hello! I\'m your smart home assistant. How can I help you today?' 
          : 'سلام! من دستیار خانه هوشمند شما هستم. چطور می‌تونم کمکتون کنم؟',
        isUser: false,
        timestamp: new Date()
      };
      setMessages([welcomeMessage]);
    } finally {
      setIsLoadingHistory(false);
    }
  };

  
  const handleWakeTriggered = () => {
    wakeTriggeredRef.current = true;
    console.log("🔊 Wake word detected: Starting voice input for 8 seconds...");
    startRecording();
  };

  window.addEventListener("wake-word-detected", handleWakeTriggered);

  loadHistory();

  return () => {
    window.removeEventListener("wake-word-detected", handleWakeTriggered);
  };
}, [language]);


  const handleTTS = async (messageText: string, messageId: string) => {
    if (playingMessageId === messageId) return; // Prevent replaying if already processing

    try {
      setPlayingMessageId(messageId);
      console.log('Starting TTS for message:', messageId);

      // Step 1: Synthesize audio
      const synthesizeResponse = await fetch('http://localhost:8000/tts/synthesize', {
        method: 'POST',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text: messageText,
          voice: 'default'
        }),
      });

      console.log('TTS synthesize response status:', synthesizeResponse.status);

      if (!synthesizeResponse.ok) {
        throw new Error(`HTTP error! status: ${synthesizeResponse.status}`);
      }

      const synthesizeData = await synthesizeResponse.json();
      console.log('TTS synthesize response data:', synthesizeData);

      if (synthesizeData.status !== 'success' || !synthesizeData.audio_filename) {
        throw new Error('TTS synthesis failed');
      }

      const audioFilename = synthesizeData.audio_filename;

      // Step 2: Download audio file
      const downloadResponse = await fetch(`http://localhost:8000/files/download?filename=${audioFilename}`, {
        method: 'GET',
      });

      console.log('Audio download response status:', downloadResponse.status);

      if (!downloadResponse.ok) {
        throw new Error(`HTTP error! status: ${downloadResponse.status}`);
      }

      // Convert response to blob and play audio
      const audioBlob = await downloadResponse.blob();
      const audioUrl = URL.createObjectURL(audioBlob);
      const audio = new Audio(audioUrl);

      audio.onended = () => {
        setPlayingMessageId(null);
        URL.revokeObjectURL(audioUrl);
      };

      audio.onerror = () => {
        setPlayingMessageId(null);
        URL.revokeObjectURL(audioUrl);
        throw new Error('Audio playback failed');
      };

      await audio.play();

    } catch (error) {
      console.error('TTS Error:', error);
      setPlayingMessageId(null);
      
      toast({
        title: language === 'en' ? 'TTS Error' : 'خطای تبدیل متن به گفتار',
        description: language === 'en' ? 'Failed to play audio' : 'پخش صدا ناموفق بود',
        variant: 'destructive',
      });
    }
  };

  const handleClearHistory = async () => {
    try {
      console.log('Clearing chat history...');
      
      const response = await fetch('http://localhost:8000/llm/clear-history', {
        method: 'POST',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({}),
      });

      console.log('Clear response status:', response.status);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      console.log('Clear response data:', data);

      // Check if the response indicates success
      if (data.status === 'success') {
        // Show toast notification
        toast({
          title: language === 'en' ? 'Success' : 'موفقیت',
          description: data.message || 'History cleared successfully',
        });

        // Clear messages in UI
        setMessages([]);
      } else {
        throw new Error('Failed to clear history');
      }
    } catch (error) {
      console.error('Error clearing chat history:', error);
      
      toast({
        title: language === 'en' ? 'Error' : 'خطا',
        description: text[language].error,
        variant: 'destructive',
      });
    }
  };

  const startRecording = async () => {
    if (isRecording || isTranscribing) return;

    try {
      console.log('Requesting microphone permission...');
      
      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          sampleRate: 16000,
          channelCount: 1,
          echoCancellation: true,
          noiseSuppression: true
        } 
      });

      console.log('Microphone access granted, starting recording...');

      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: 'audio/webm;codecs=opus'
      });

      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = async () => {
        console.log('Recording stopped, processing audio...');

         setIsRecording(false);
      
        // Stop all tracks to release microphone
        stream.getTracks().forEach(track => track.stop());
        
        if (audioChunksRef.current.length > 0) {
          await processRecording();
        }
      };

      mediaRecorder.start();
      setIsRecording(true);

       if (wakeTriggeredRef.current) {
      console.log("⏱ Timer started for 8 seconds (wake mode)...");
      setTimeout(() => {
        if (mediaRecorder.state === "recording") {
          console.log("⏱ Timer hit: stopping recording (wake word mode)...");
          stopRecording();
        } else {
          console.log("⚠️ Recorder already stopped before timeout.");
        }
      }, 8000);
    }


    } catch (error) {
      console.error('Error accessing microphone:', error);
      
      let errorMessage = text[language].microphoneError;
      if (error instanceof Error && error.name === 'NotAllowedError') {
        errorMessage = text[language].microphonePermissionDenied;
      }
      
      toast({
        title: language === 'en' ? 'Microphone Error' : 'خطای میکروفون',
        description: errorMessage,
        variant: 'destructive',
      });
    }
  };


  const stopRecording = () => {
  if (mediaRecorderRef.current) {
    try {
      console.log('✅ Stopping MediaRecorder...');
      mediaRecorderRef.current.stop();
    } catch (err) {
      console.error('❌ Error stopping recorder:', err);
    }
  }
};


  const processRecording = async () => {
    setIsTranscribing(true);

    try {
      console.log('Converting recorded audio...');
      
      const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
      
      // Convert to WAV format
      const wavBlob = await convertToWav(audioBlob);
      
      console.log('Starting STT transcription...');

      const formData = new FormData();
      formData.append('audio_file', wavBlob, 'recording.wav');

      const response = await fetch('http://localhost:8000/stt/transcribe', {
        method: 'POST',
        headers: {
          'Accept': 'application/json',
        },
        body: formData,
      });

      console.log('STT response status:', response.status);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      console.log('STT response data:', data);

      if (data.status === 'success' && data.transcription) {
        // Insert transcription as user message and trigger send
        setInputText(data.transcription);

          const triggeredByWake = wakeTriggeredRef.current;

          wakeTriggeredRef.current = false;
        
        // Automatically send the transcribed message
        setTimeout(() => {
          handleSendMessage(data.transcription, triggeredByWake);
        }, 100);
      } else {
        throw new Error('Transcription failed');
      }
    } catch (error) {
      console.error('STT Error:', error);
      
      toast({
        title: language === 'en' ? 'Voice Input Error' : 'خطای ورودی صوتی',
        description: text[language].voiceInputFailed,
        variant: 'destructive',
      });
    } finally {
      setIsTranscribing(false);
      audioChunksRef.current = [];
    }
  };

  const convertToWav = async (webmBlob: Blob): Promise<Blob> => {
    // Simple conversion - for better quality, consider using a proper audio conversion library
    return new Promise((resolve) => {
      const audio = new Audio();
      const url = URL.createObjectURL(webmBlob);
      
      audio.onloadeddata = () => {
        const audioContext = new (window.AudioContext || (window as any).webkitAudioContext)();
        const source = audioContext.createMediaElementSource(audio);
        
        // For now, return the original blob as the browser should handle the format
        // In a production environment, you might want to use a proper audio conversion library
        URL.revokeObjectURL(url);
        resolve(webmBlob);
      };
      
      audio.src = url;
    });
  };

  const handleVoiceInput = () => {
    if (isRecording) {
      stopRecording();
    } else if (!isTranscribing) {
      startRecording();
    }
  };

  const handleSendMessage = async (messageText?: string, triggeredByWake = false) => {
    const textToSend = messageText || inputText;
    if (!textToSend.trim() || isLoading) return;

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      text: textToSend,
      isUser: true,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputText('');
    setIsLoading(true);

    try {
      console.log('Sending message to API:', textToSend);
      
      const response = await fetch('http://localhost:8000/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
        body: JSON.stringify({
          message: textToSend,
          use_tools: true
        }),
      });

      console.log('API response status:', response.status);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      console.log('API response data:', data);

      const assistantMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        text: data.response || text[language].error,
        isUser: false,
        timestamp: new Date()
      };

      setMessages(prev => [...prev, assistantMessage]);

          if (triggeredByWake) {
            setTimeout(() => {
              handleTTS(assistantMessage.text, assistantMessage.id);
              wakeTriggeredRef.current = false; 
            }, 300);
          }
        

      // Refresh devices after assistant response
      if (onDeviceRefresh) {
        setTimeout(() => {
          onDeviceRefresh();
        }, 500);
      }
    } catch (error) {
      console.error('Error sending message:', error);
      
      const errorMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        text: text[language].error,
        isUser: false,
        timestamp: new Date()
      };

      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <div className="bg-card rounded-xl shadow-lg border border-border overflow-hidden">
      <div className="bg-gradient-to-r from-blue-500 to-purple-600 dark:from-blue-600 dark:to-purple-700 text-white p-4">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold">{text[language].title}</h2>
          <button
            onClick={handleClearHistory}
            className="flex items-center space-x-1 rtl:space-x-reverse px-3 py-1.5 bg-white/20 hover:bg-white/30 rounded-lg transition-colors text-sm"
          >
            <Trash2 className="w-4 h-4" />
            <span>{text[language].clearHistory}</span>
          </button>
        </div>
      </div>

      <div 
        ref={chatContainerRef}
        className="h-64 overflow-y-auto p-4 space-y-3"
      >
        {isLoadingHistory ? (
          <div className="flex justify-center items-center h-full">
            <div className="flex items-center space-x-2 rtl:space-x-reverse text-muted-foreground">
              <div className="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin"></div>
              <span className="text-sm">{text[language].loadingHistory}</span>
            </div>
          </div>
        ) : (
          <>
            {messages.map((message) => (
              <div
                key={message.id}
                className={cn(
                  "flex",
                  message.isUser ? "justify-end" : "justify-start"
                )}
              >
                <div
                  className={cn(
                    "max-w-xs lg:max-w-md px-4 py-3 rounded-xl relative",
                    message.isUser
                      ? "bg-blue-500 dark:bg-blue-600 text-white"
                      : "bg-muted dark:bg-slate-700 text-foreground"
                  )}
                >
                  <div className="flex items-start justify-between gap-2">
                    <div className="flex-1">
                      <div className="text-sm leading-relaxed">
                        <ReactMarkdown>{message.text}</ReactMarkdown>
                      </div>
                      <p className="text-xs opacity-70 mt-1">
                        {message.timestamp.toLocaleTimeString(language === 'fa' ? 'fa-IR' : 'en-US', {
                          hour: '2-digit',
                          minute: '2-digit'
                        })}
                      </p>
                    </div>
                    
                    {!message.isUser && (
                      <div className="flex gap-1">
                        <button
                          onClick={() => handleTTS(message.text, message.id)}
                          disabled={playingMessageId === message.id}
                          className={cn(
                            "p-1 rounded hover:bg-accent transition-colors flex-shrink-0",
                            playingMessageId === message.id && "opacity-50 cursor-not-allowed"
                          )}
                          title={text[language].readMessage}
                        >
                          <Volume2 
                            className={cn(
                              "w-4 h-4 text-muted-foreground",
                              playingMessageId === message.id && "animate-pulse"
                            )} 
                          />
                        </button>
                        
                        <CopyButton 
                          text={message.text} 
                          language={language}
                        />
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}

            {isRecording && (
              <div className="flex justify-start">
                <div className="bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-400 px-4 py-3 rounded-xl flex items-center space-x-2 rtl:space-x-reverse">
                  <div className="w-3 h-3 bg-red-500 rounded-full animate-pulse"></div>
                  <span className="text-sm">{text[language].recording}</span>
                </div>
              </div>
            )}

            {isTranscribing && (
              <div className="flex justify-start">
                <div className="bg-yellow-100 dark:bg-yellow-900/30 text-yellow-800 dark:text-yellow-400 px-4 py-3 rounded-xl flex items-center space-x-2 rtl:space-x-reverse">
                  <MicIcon className="w-4 h-4 animate-pulse" />
                  <span className="text-sm">{text[language].transcribing}</span>
                </div>
              </div>
            )}

            {isLoading && (
              <div className="flex justify-start">
                <div className="bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-400 px-4 py-3 rounded-xl flex items-center space-x-2 rtl:space-x-reverse">
                  <div className="w-4 h-4 border-2 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
                  <span className="text-sm">{text[language].sending}</span>
                </div>
              </div>
            )}
          </>
        )}
      </div>

      <div className="p-4 border-t border-border">
        <div className="flex space-x-2 rtl:space-x-reverse">
          <input
            type="text"
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder={text[language].placeholder}
            disabled={isLoading || isLoadingHistory || isRecording}
            className="flex-1 px-4 py-2.5 border border-input rounded-full focus:outline-none focus:ring-2 focus:ring-ring focus:border-transparent disabled:opacity-50 bg-background text-sm"
          />
          
          {/* Voice Input Button */}
          <button
            onClick={handleVoiceInput}
            disabled={isTranscribing || isLoading || isLoadingHistory}
            className={cn(
              "p-2.5 rounded-full transition-all duration-200 hover:scale-105 relative",
              isRecording 
                ? "bg-red-500 text-white animate-pulse" 
                : "bg-secondary hover:bg-secondary/80 text-foreground"
            )}
            title={isRecording ? text[language].stopRecording : text[language].voiceInput}
          >
            {isRecording ? (
              <Square className="w-4 h-4" />
            ) : (
              <Mic className="w-4 h-4" />
            )}
            {isRecording && (
              <div className="absolute inset-0 rounded-full border-2 border-red-400 animate-ping"></div>
            )}
          </button>
          
          <button
            onClick={() => handleSendMessage()}
            disabled={!inputText.trim() || isLoading || isLoadingHistory || isRecording}
            className="px-5 py-2.5 bg-blue-500 dark:bg-blue-600 text-white rounded-full hover:bg-blue-600 dark:hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center space-x-2 rtl:space-x-reverse text-sm"
          >
            <Send className="w-4 h-4" />
            <span className="hidden sm:inline">{text[language].send}</span>
          </button>
        </div>
      </div>
    </div>
  );
});

ChatInterface.displayName = 'ChatInterface';

export default ChatInterface;