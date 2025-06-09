import { useState, useEffect } from 'react';
import { Globe, Cloud, Sun, CloudRain, Moon } from 'lucide-react';

interface TopBarProps {
  language: 'en' | 'fa';
  setLanguage: (lang: 'en' | 'fa') => void;
}

const TopBar = ({ language, setLanguage }: TopBarProps) => {
  const [currentTime, setCurrentTime] = useState(new Date());
  const [weather] = useState({ temp: 22, condition: 'sunny' });
  const [isDarkMode, setIsDarkMode] = useState(false);

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date());
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  useEffect(() => {
    if (isDarkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [isDarkMode]);

  const formatTime = (date: Date) => {
    if (language === 'fa') {
      return date.toLocaleTimeString('fa-IR', { 
        hour: '2-digit', 
        minute: '2-digit',
        hour12: false 
      });
    }
    return date.toLocaleTimeString('en-US', { 
      hour: '2-digit', 
      minute: '2-digit',
      hour12: true 
    });
  };

  const formatDate = (date: Date) => {
    if (language === 'fa') {
      return date.toLocaleDateString('fa-IR', { 
        weekday: 'long', 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric' 
      });
    }
    return date.toLocaleDateString('en-US', { 
      weekday: 'long', 
      year: 'numeric', 
      month: 'long', 
      day: 'numeric' 
    });
  };

  const getWeatherIcon = () => {
    switch (weather.condition) {
      case 'sunny':
        return <Sun className="w-4 h-4 text-yellow-500" />;
      case 'cloudy':
        return <Cloud className="w-4 h-4 text-gray-500" />;
      case 'rainy':
        return <CloudRain className="w-4 h-4 text-blue-500" />;
      default:
        return <Sun className="w-4 h-4 text-yellow-500" />;
    }
  };

  return (
    <div className="bg-background/80 backdrop-blur-sm border-b border-border shadow-sm">
      <div className="container mx-auto px-4 py-2">
        <div className="flex justify-between items-center">
          {/* Weather */}
          <div className="flex items-center space-x-2 rtl:space-x-reverse">
            {getWeatherIcon()}
            <span className="text-sm font-medium text-foreground">{weather.temp}°C</span>
          </div>

          {/* Time, Date & Controls */}
          <div className="flex items-center space-x-3 rtl:space-x-reverse">
            <div className="text-right rtl:text-left">
              <div className="text-base font-semibold text-foreground">
                {formatTime(currentTime)}
              </div>
              <div className="text-xs text-muted-foreground">
                {formatDate(currentTime)}
              </div>
            </div>
            
            {/* Dark Mode Toggle */}
            <button
              onClick={() => setIsDarkMode(!isDarkMode)}
              className="flex items-center justify-center w-8 h-8 rounded-full bg-secondary hover:bg-secondary/80 transition-colors"
            >
              {isDarkMode ? (
                <Sun className="w-4 h-4 text-foreground" />
              ) : (
                <Moon className="w-4 h-4 text-foreground" />
              )}
            </button>
            
            <button
              onClick={() => setLanguage(language === 'en' ? 'fa' : 'en')}
              className="flex items-center space-x-1 rtl:space-x-reverse px-2 py-1 rounded-full bg-secondary hover:bg-secondary/80 transition-colors"
            >
              <Globe className="w-3 h-3 text-muted-foreground" />
              <span className="text-xs font-medium text-foreground">
                {language === 'en' ? 'EN' : 'فا'}
              </span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TopBar;