import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { AuthButton } from './AuthButton';
import { EmailList } from './EmailList';
import { 
  Mail, 
  Inbox, 
  Star, 
  Archive, 
  Trash2,
  Settings,
  Brain,
  Database
} from 'lucide-react';

export const Dashboard = () => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [token, setToken] = useState<string | null>(null);

  const handleAuthSuccess = (newToken: string) => {
    setToken(newToken);
    setIsAuthenticated(true);
  };

  const handleLogout = () => {
    setToken(null);
    setIsAuthenticated(false);
  };

  const stats = [
    { label: 'Total de Emails', value: '1,234', icon: Mail, color: 'text-gmail-primary' },
    { label: 'Não Lidos', value: '23', icon: Inbox, color: 'text-gmail-unread' },
    { label: 'Importantes', value: '7', icon: Star, color: 'text-gmail-important' },
    { label: 'Arquivados', value: '456', icon: Archive, color: 'text-muted-foreground' },
  ];

  return (
    <div className="min-h-screen bg-background p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-gradient-to-r from-gmail-primary to-red-500 rounded-xl shadow-glow">
              <Mail className="w-8 h-8 text-white" />
            </div>
            <div>
              <h1 className="text-3xl font-bold bg-gradient-to-r from-gmail-primary to-red-400 bg-clip-text text-transparent">
                Gmail Analytics AI
              </h1>
              <p className="text-muted-foreground">
                Análise inteligente de emails com LangChain e ChromaDB
              </p>
            </div>
          </div>
          <div className="flex items-center gap-4">
            <Badge variant="outline" className="border-gmail-primary/30 text-gmail-primary">
              <Brain className="w-3 h-3 mr-1" />
              LangChain
            </Badge>
            <Badge variant="outline" className="border-gmail-primary/30 text-gmail-primary">
              <Database className="w-3 h-3 mr-1" />
              ChromaDB
            </Badge>
            <AuthButton 
              isAuthenticated={isAuthenticated}
              onAuthSuccess={handleAuthSuccess}
              onLogout={handleLogout}
            />
          </div>
        </div>

        {/* Stats Cards */}
        {isAuthenticated && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {stats.map((stat, index) => {
              const Icon = stat.icon;
              return (
                <Card key={index} className="bg-gradient-to-br from-card to-gmail-secondary border-gmail-primary/20 hover:shadow-lg transition-shadow">
                  <CardContent className="p-6">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm font-medium text-muted-foreground">
                          {stat.label}
                        </p>
                        <p className="text-2xl font-bold">
                          {stat.value}
                        </p>
                      </div>
                      <Icon className={`w-8 h-8 ${stat.color}`} />
                    </div>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        )}

        {/* Main Content */}
        {isAuthenticated && token ? (
          <div className="h-[700px]">
            <EmailList token={token} />
          </div>
        ) : (
          <Card className="bg-gradient-to-br from-card to-gmail-secondary border-gmail-primary/20">
            <CardContent className="p-12 text-center">
              <div className="max-w-md mx-auto space-y-6">
                <div className="p-6 bg-gradient-to-r from-gmail-primary/10 to-red-500/10 rounded-full w-fit mx-auto">
                  <Mail className="w-16 h-16 text-gmail-primary" />
                </div>
                <div>
                  <h2 className="text-2xl font-bold mb-2">
                    Conecte ao Gmail para começar
                  </h2>
                  <p className="text-muted-foreground mb-6">
                    Esta aplicação usa IA para analisar seus emails com LangChain e armazena os dados em ChromaDB para consultas semânticas avançadas.
                  </p>
                </div>
                <div className="space-y-4 text-left">
                  <div className="flex items-center gap-3 p-3 bg-gmail-secondary/30 rounded-lg">
                    <Brain className="w-5 h-5 text-gmail-primary" />
                    <span className="text-sm">
                      <strong>LangChain:</strong> Processamento inteligente de texto
                    </span>
                  </div>
                  <div className="flex items-center gap-3 p-3 bg-gmail-secondary/30 rounded-lg">
                    <Database className="w-5 h-5 text-gmail-primary" />
                    <span className="text-sm">
                      <strong>ChromaDB:</strong> Busca semântica avançada
                    </span>
                  </div>
                  <div className="flex items-center gap-3 p-3 bg-gmail-secondary/30 rounded-lg">
                    <Settings className="w-5 h-5 text-gmail-primary" />
                    <span className="text-sm">
                      <strong>Docker:</strong> Deploy containerizado
                    </span>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Footer */}
        <div className="text-center text-sm text-muted-foreground">
          <p>
            Frontend: React + Vite + Tailwind | Backend: Python + LangChain + ChromaDB | Containerização: Docker
          </p>
        </div>
      </div>
    </div>
  );
};