import { useState, useEffect, useRef } from 'react';
import TopBar from '../components/TopBar';
import DeviceCard from '../components/DeviceCard';
import ChatInterface from '../components/ChatInterface';
import { useToast } from '@/hooks/use-toast';

export interface Device {
  id: string;
  name: string;
  type: 'lamp' | 'tv' | 'ac';
  location: string;
  isOn: boolean;
}

const Index = () => {
  const [language, setLanguage] = useState<'en' | 'fa'>('en');
  const [devices, setDevices] = useState<Device[]>([]);
  const [isLoadingDevices, setIsLoadingDevices] = useState(true);
  const { toast } = useToast();
  const chatInterfaceRef = useRef<{ refreshDevices: () => void }>(null);

  // Load devices from API
  const loadDevices = async () => {
    try {
      console.log('Loading devices from /devices...');
      
      const response = await fetch('http://localhost:8000/devices', {
        method: 'GET',
        headers: {
          'Accept': 'application/json',
        },
      });

      console.log('Devices response status:', response.status);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      console.log('Devices data:', data);

      if (data.devices && Array.isArray(data.devices)) {
        // Map API devices to our Device interface
        const mappedDevices: Device[] = data.devices.map((device: any) => ({
          id: device.id,
          name: device.name,
          type: device.type,
          location: device.location,
          isOn: device.status === 'on'
        }));
        
        setDevices(mappedDevices);
        console.log('Loaded', mappedDevices.length, 'devices from API');
      } else {
        console.log('No valid devices found, using default devices');
        // Fallback to default devices if API doesn't return proper data
        setDevices([
          { id: '1', name: 'Kitchen Lamp', type: 'lamp', location: 'Kitchen', isOn: false },
          { id: '2', name: 'Bathroom Lamp', type: 'lamp', location: 'Bathroom', isOn: true },
          { id: '3', name: 'Room 1 Lamp', type: 'lamp', location: 'Room 1', isOn: false },
          { id: '4', name: 'Room 2 Lamp', type: 'lamp', location: 'Room 2', isOn: true },
          { id: '5', name: 'Kitchen AC', type: 'ac', location: 'Kitchen', isOn: false },
          { id: '6', name: 'Room 1 AC', type: 'ac', location: 'Room 1', isOn: true },
          { id: '7', name: 'Living Room TV', type: 'tv', location: 'Living Room', isOn: false },
        ]);
      }
    } catch (error) {
      console.error('Error loading devices:', error);
      // Use default devices as fallback
      setDevices([
        { id: '1', name: 'Kitchen Lamp', type: 'lamp', location: 'Kitchen', isOn: false },
        { id: '2', name: 'Bathroom Lamp', type: 'lamp', location: 'Bathroom', isOn: true },
        { id: '3', name: 'Room 1 Lamp', type: 'lamp', location: 'Room 1', isOn: false },
        { id: '4', name: 'Room 2 Lamp', type: 'lamp', location: 'Room 2', isOn: true },
        { id: '5', name: 'Kitchen AC', type: 'ac', location: 'Kitchen', isOn: false },
        { id: '6', name: 'Room 1 AC', type: 'ac', location: 'Room 1', isOn: true },
        { id: '7', name: 'Living Room TV', type: 'tv', location: 'Living Room', isOn: false },
      ]);
    } finally {
      setIsLoadingDevices(false);
    }
  };

  useEffect(() => {
    loadDevices();
  }, []);

  const toggleDevice = async (deviceId: string) => {
    const device = devices.find(d => d.id === deviceId);
    if (!device) return;

    const newState = !device.isOn;
    
    // Optimistic update
    setDevices(devices.map(d => 
      d.id === deviceId ? { ...d, isOn: newState } : d
    ));

    try {
      console.log(`Toggling device ${deviceId} to ${newState ? 'on' : 'off'}`);
      
      const response = await fetch('http://localhost:8000/devices/control', {
        method: 'POST',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          device_id: deviceId,
          action: newState ? 'on' : 'off'
        }),
      });

      console.log('Device control response status:', response.status);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      console.log('Device control response data:', data);

      if (data.status === 'success') {
        // Show success toast
        toast({
          title: language === 'en' ? 'Success' : 'موفقیت',
          description: data.message || `Device ${newState ? 'turned on' : 'turned off'}`,
        });
      } else {
        // Revert optimistic update on failure
        setDevices(devices.map(d => 
          d.id === deviceId ? { ...d, isOn: !newState } : d
        ));
        throw new Error('Device control failed');
      }
    } catch (error) {
      console.error('Error controlling device:', error);
      
      // Revert optimistic update
      setDevices(devices.map(d => 
        d.id === deviceId ? { ...d, isOn: !newState } : d
      ));
      
      toast({
        title: language === 'en' ? 'Error' : 'خطا',
        description: language === 'en' ? 'Failed to control device' : 'کنترل دستگاه ناموفق بود',
        variant: 'destructive',
      });
    }
  };

  const text = {
    en: {
      title: 'Smart Home Assistant',
      devices: 'Device Control',
      chat: 'Assistant Chat',
      loadingDevices: 'Loading devices...'
    },
    fa: {
      title: 'دستیار خانه هوشمند',
      devices: 'کنترل دستگاه‌ها',
      chat: 'گفتگو با دستیار',
      loadingDevices: 'در حال بارگذاری دستگاه‌ها...'
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 dark:from-[#0a192f] dark:via-[#112240] dark:to-[#1a365d]" dir={language === 'fa' ? 'rtl' : 'ltr'}>
      <TopBar language={language} setLanguage={setLanguage} />
      
      <div className="container mx-auto px-4 py-6 max-w-6xl">
        {/* Main Title */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-foreground">{text[language].title}</h1>
        </div>

        {/* Device Control Dashboard */}
        <div className="mb-8">
          <h2 className="text-xl font-semibold text-foreground text-center mb-4">{text[language].devices}</h2>
          
          {isLoadingDevices ? (
            <div className="flex justify-center items-center py-8">
              <div className="flex items-center space-x-2 rtl:space-x-reverse text-muted-foreground">
                <div className="w-5 h-5 border-2 border-current border-t-transparent rounded-full animate-spin"></div>
                <span className="text-sm">{text[language].loadingDevices}</span>
              </div>
            </div>
          ) : (
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4 max-w-5xl mx-auto">
              {devices.map((device) => (
                <DeviceCard
                  key={device.id}
                  device={device}
                  onToggle={toggleDevice}
                  language={language}
                />
              ))}
            </div>
          )}
        </div>

        {/* Chat Interface - More Compact */}
        <div className="max-w-4xl mx-auto">
          <ChatInterface 
            ref={chatInterfaceRef}
            language={language} 
            onDeviceRefresh={loadDevices}
          />
        </div>
      </div>
    </div>
  );
};

export default Index;