import { useState, useEffect, useCallback, useRef } from 'react';
import { Button } from '@/components/ui/button';
import { Mail, LogOut } from 'lucide-react';
import { toast } from 'sonner';

interface AuthButtonProps {
  isAuthenticated: boolean;
  onAuthSuccess: (token: string) => void;
  onLogout: () => void;
}

export const AuthButton = ({ isAuthenticated, onAuthSuccess, onLogout }: AuthButtonProps) => {
  const [isLoading, setIsLoading] = useState(false);
  const popupRef = useRef<Window | null>(null);

  const handleGoogleAuth = async () => {
    setIsLoading(true);
    try {
      const clientId = import.meta.env.VITE_GOOGLE_CLIENT_ID;
      const redirectUri = `${window.location.origin}/auth/callback`; // Corrigido para bater com o Google Console

      const authUrl = `https://accounts.google.com/o/oauth2/v2/auth?` +
        `client_id=${clientId}&` +
        `redirect_uri=${encodeURIComponent(redirectUri)}&` +
        `response_type=code&` +
        `scope=email profile https://www.googleapis.com/auth/gmail.readonly&` +
        `access_type=offline`;

      const popup = window.open(authUrl, 'googleAuth', 'width=500,height=600');

      if (!popup) {
        toast.error('Por favor, permita popups para este site');
        setIsLoading(false);
        return;
      }

      // Verificação do popup
      const checkPopup = setInterval(() => {
        if (popup.closed) {
          clearInterval(checkPopup);
          setIsLoading(false);
        }
      }, 1000);

    } catch (error) {
      setIsLoading(false);
      toast.error('Erro ao iniciar autenticação');
    }
  };


  useEffect(() => {
    const handleMessage = (event: MessageEvent) => {
      if (event.origin !== window.location.origin) return;

      if (event.data.type === 'auth_success') {
        onAuthSuccess(event.data.token);
        setIsLoading(false);
      } else if (event.data.type === 'auth_error') {
        toast.error('Falha na autenticação');
        setIsLoading(false);
      }
    };

    window.addEventListener('message', handleMessage);
    return () => {
      window.removeEventListener('message', handleMessage);
    };
  }, [onAuthSuccess]);

  const handleLogout = () => {
    onLogout();
    toast.success('Desconectado do Gmail');
  };

  if (isAuthenticated) {
    return (
      <Button
        onClick={handleLogout}
        variant="outline"
        className="bg-gmail-secondary border-gmail-primary text-foreground hover:bg-gmail-primary hover:text-primary-foreground"
      >
        <LogOut className="w-4 h-4 mr-2" />
        Desconectar
      </Button>
    );
  }

  return (
    <Button
      onClick={handleGoogleAuth}
      disabled={isLoading}
      className="bg-gradient-to-r from-gmail-primary to-red-500 hover:from-gmail-primary hover:to-red-600 text-primary-foreground shadow-lg hover:shadow-glow transition-all duration-300"
    >
      <Mail className="w-4 h-4 mr-2" />
      {isLoading ? 'Conectando...' : 'Conectar ao Gmail'}
    </Button>
  );
};