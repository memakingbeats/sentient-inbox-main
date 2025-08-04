// Crie um novo arquivo src/pages/AuthCallback.tsx
import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

export const AuthCallback = () => {
  const navigate = useNavigate();

  useEffect(() => {
    console.log('[DEBUG] AuthCallback iniciado'); // ✅
    const params = new URLSearchParams(window.location.search);
    const code = params.get('code');
    console.log('[DEBUG] Código OAuth:', code); // ✅ Verifica se o código está chegando

    if (code) {
      console.log('[DEBUG] Enviando mensagem para window.opener'); // ✅
      window.opener.postMessage({
        type: 'GOOGLE_AUTH_SUCCESS',
        code
      }, window.location.origin);

      window.close();
    } else {
      console.warn('[DEBUG] Nenhum código encontrado na URL'); // ✅
      navigate('/');
    }
  }, [navigate]);

  return <div>Processando autenticação...</div>;
};
export default AuthCallback;