import { useState } from 'react';
import { Copy, Check } from 'lucide-react';
import { cn } from '@/lib/utils';
import { useToast } from '@/hooks/use-toast';

interface CopyButtonProps {
  text: string;
  language: 'en' | 'fa';
  className?: string;
}

const CopyButton = ({ text, language, className }: CopyButtonProps) => {
  const [copied, setCopied] = useState(false);
  const { toast } = useToast();

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      
      toast({
        title: language === 'en' ? 'Copied!' : 'کپی شد!',
        description: language === 'en' ? 'Message copied to clipboard' : 'پیام در کلیپ‌بورد کپی شد',
      });

      setTimeout(() => setCopied(false), 2000);
    } catch (error) {
      console.error('Failed to copy text:', error);
      
      toast({
        title: language === 'en' ? 'Copy Failed' : 'کپی ناموفق',
        description: language === 'en' ? 'Failed to copy message' : 'کپی پیام ناموفق بود',
        variant: 'destructive',
      });
    }
  };

  return (
    <button
      onClick={handleCopy}
      className={cn(
        "p-1 rounded hover:bg-accent transition-colors flex-shrink-0",
        className
      )}
      title={language === 'en' ? 'Copy message' : 'کپی پیام'}
    >
      {copied ? (
        <Check className="w-3.5 h-3.5 text-green-600" />
      ) : (
        <Copy className="w-3.5 h-3.5 text-muted-foreground" />
      )}
    </button>
  );
};

export default CopyButton;