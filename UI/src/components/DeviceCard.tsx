import { Lamp, Tv } from 'lucide-react';
import { Device } from '../pages/Index';
import { cn } from '@/lib/utils';

interface DeviceCardProps {
  device: Device;
  onToggle: (deviceId: string) => void;
  language: 'en' | 'fa';
}

const DeviceCard = ({ device, onToggle, language }: DeviceCardProps) => {
  const getDeviceIcon = () => {
    switch (device.type) {
      case 'lamp':
        return <Lamp className={cn("w-5 h-5", device.isOn ? "text-yellow-500" : "text-gray-400")} />;
      case 'tv':
        return <Tv className={cn("w-5 h-5", device.isOn ? "text-blue-500" : "text-gray-400")} />;
      case 'ac':
        return (
          <div className={cn("w-5 h-5 rounded-full flex items-center justify-center", 
            device.isOn ? "bg-cyan-500 text-white" : "bg-gray-400 text-white"
          )}>
            <span className="text-[10px] font-bold">AC</span>
          </div>
        );
      default:
        return <Lamp className="w-5 h-5 text-gray-400" />;
    }
  };

  const text = {
    en: {
      on: 'ON',
      off: 'OFF'
    },
    fa: {
      on: 'روشن',
      off: 'خاموش'
    }
  };

  return (
    <div className={cn(
      "bg-card rounded-lg p-4 shadow-md border transition-all duration-300 hover:shadow-lg hover:scale-105",
      device.isOn ? "border-green-200 bg-green-50/50 dark:bg-green-950/20" : "border-border"
    )}>
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center space-x-2 rtl:space-x-reverse">
          {getDeviceIcon()}
          <div>
            <h3 className="font-semibold text-foreground text-sm">{device.name}</h3>
            <p className="text-xs text-muted-foreground">{device.location}</p>
          </div>
        </div>
        
        <div className={cn(
          "w-2 h-2 rounded-full",
          device.isOn ? "bg-green-500 animate-pulse" : "bg-gray-300"
        )}></div>
      </div>

      <div className="flex items-center justify-between">
        <span className={cn(
          "text-xs font-medium px-2 py-1 rounded-full",
          device.isOn 
            ? "text-green-700 bg-green-100 dark:text-green-400 dark:bg-green-900/30" 
            : "text-muted-foreground bg-muted"
        )}>
          {text[language][device.isOn ? 'on' : 'off']}
        </span>

        <button
          onClick={() => onToggle(device.id)}
          className={cn(
            "relative inline-flex h-5 w-9 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-1",
            device.isOn ? "bg-blue-500 dark:bg-blue-600" : "bg-gray-300"
          )}
        >
          <span
            className={cn(
              "inline-block h-3 w-3 transform rounded-full bg-white transition-transform",
              device.isOn ? "translate-x-5" : "translate-x-1"
            )}
          />
        </button>
      </div>
    </div>
  );
};

export default DeviceCard;