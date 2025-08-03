import { useState } from 'react';
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

  const handleGoogleAuth = async () => {
    setIsLoading(true);
    try {
      // Configurações do Google OAuth
      const clientId = '349138754128-rug3moio7qlfq09cukl5hiie9rjr0ru9.apps.googleusercontent.com';
      const redirectUri = 'http://localhost:5173/auth/callback';
      const scope = 'https://www.googleapis.com/auth/gmail.readonly https://www.googleapis.com/auth/gmail.modify';

      // URL de autorização do Google
      const authUrl = `https://accounts.google.com/o/oauth2/auth?client_id=${clientId}&redirect_uri=${encodeURIComponent(redirectUri)}&scope=${encodeURIComponent(scope)}&response_type=code&access_type=offline`;

      // Abrir popup para autenticação
      const popup = window.open(authUrl, 'googleAuth', 'width=500,height=600');

      // Listener para receber o código de autorização
      window.addEventListener('message', async (event) => {
        if (event.origin !== window.location.origin) return;

        if (event.data.type === 'GOOGLE_AUTH_SUCCESS') {
          const { code } = event.data;

          try {
            // Trocar código por tokens
            const response = await fetch('http://localhost:8000/auth/google', {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
              },
              body: JSON.stringify({
                code,
                client_id: clientId,
                client_secret: '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'
              })
            });

            if (response.ok) {
              const data = await response.json();
              onAuthSuccess(data.access_token);
              toast.success('Conectado ao Gmail com sucesso!');
            } else {
              throw new Error('Falha na autenticação');
            }
          } catch (error) {
            toast.error('Erro ao conectar com Gmail');
            console.error('Erro na autenticação:', error);
          } finally {
            setIsLoading(false);
            popup?.close();
          }
        }
      });

    } catch (error) {
      toast.error('Erro ao conectar com Gmail');
      setIsLoading(false);
    }
  };

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