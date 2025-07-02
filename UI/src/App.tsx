
import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Index from "./pages/Index";
import { useEffect } from "react";
import { useWakeSpeech } from "@/hooks/useWakeSpeech";
import { speak } from "@/lib/tts";

const queryClient = new QueryClient();

const App = () => {

  useEffect(() => {
    navigator.mediaDevices.getUserMedia({ audio: true }).catch(console.error);
  }, []);

    useWakeSpeech({
    phrase: "jarvis",
    onWake: async () => {
      console.log("✅ Wake word detected");
      await speak("Hello, I'm your smart home assistant");
      window.dispatchEvent(new Event("wake-word-detected"));
    }
  });

  return (
    <QueryClientProvider client={queryClient}>
      <TooltipProvider>
        <Toaster />
        <Sonner />
        <BrowserRouter>
          <Routes>
            <Route path="/" element={<Index />} />
          </Routes>
        </BrowserRouter>
      </TooltipProvider>
    </QueryClientProvider>
  );
};

export default App;
