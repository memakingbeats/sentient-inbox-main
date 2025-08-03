import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Separator } from '@/components/ui/separator';
import {
  Mail,
  MailOpen,
  Star,
  Paperclip,
  Clock,
  Search,
  Filter,
  RefreshCw,
  Brain,
  MessageSquare
} from 'lucide-react';
import { Input } from '@/components/ui/input';
import { toast } from 'sonner';

export interface Email {
  id: string;
  subject: string;
  sender: string;
  snippet: string;
  date: string;
  isRead: boolean;
  isImportant: boolean;
  hasAttachments: boolean;
  labels: string[];
  body?: string;
}

interface EmailListProps {
  token: string;
}

export const EmailList = ({ token }: EmailListProps) => {
  const [emails, setEmails] = useState<Email[]>([]);
  const [loading, setLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedEmail, setSelectedEmail] = useState<Email | null>(null);
  const [aiAnalysis, setAiAnalysis] = useState<any>(null);
  const [analyzing, setAnalyzing] = useState(false);

  useEffect(() => {
    loadEmails();
  }, [token]);

  const loadEmails = async () => {
    setLoading(true);
    try {
      const response = await fetch('http://localhost:8000/emails/', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const data = await response.json();
        setEmails(data);
        toast.success(`${data.length} emails carregados`);
      } else {
        throw new Error('Erro ao carregar emails');
      }
    } catch (error) {
      toast.error('Erro ao carregar emails');
      console.error('Erro:', error);
    } finally {
      setLoading(false);
    }
  };

  const markAsRead = async (emailId: string) => {
    try {
      const response = await fetch(`http://localhost:8000/emails/${emailId}/read`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        setEmails(emails.map(email =>
          email.id === emailId ? { ...email, isRead: true } : email
        ));
      }
    } catch (error) {
      console.error('Erro ao marcar como lido:', error);
    }
  };

  const analyzeEmail = async (emailId: string) => {
    setAnalyzing(true);
    try {
      const response = await fetch(`http://localhost:8000/emails/${emailId}/analysis`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const analysis = await response.json();
        setAiAnalysis(analysis);
        toast.success('Análise de IA concluída');
      } else {
        throw new Error('Erro na análise');
      }
    } catch (error) {
      toast.error('Erro na análise de IA');
      console.error('Erro:', error);
    } finally {
      setAnalyzing(false);
    }
  };

  const filteredEmails = emails.filter(email =>
    email.subject.toLowerCase().includes(searchTerm.toLowerCase()) ||
    email.sender.toLowerCase().includes(searchTerm.toLowerCase()) ||
    email.snippet.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="flex h-full gap-4">
      {/* Lista de emails */}
      <div className="w-1/2 flex flex-col">
        <Card className="flex-1 bg-gradient-to-br from-card to-gmail-secondary border-gmail-primary/20">
          <CardHeader className="pb-4">
            <div className="flex items-center justify-between">
              <h2 className="text-2xl font-bold bg-gradient-to-r from-gmail-primary to-red-400 bg-clip-text text-transparent">
                Caixa de Entrada
              </h2>
              <div className="flex gap-2">
                <Button
                  onClick={loadEmails}
                  disabled={loading}
                  size="sm"
                  variant="outline"
                  className="border-gmail-primary/30 hover:border-gmail-primary"
                >
                  <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
                </Button>
                <Button size="sm" variant="outline" className="border-gmail-primary/30 hover:border-gmail-primary">
                  <Filter className="w-4 h-4" />
                </Button>
              </div>
            </div>
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-muted-foreground" />
              <Input
                placeholder="Buscar emails..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10 bg-gmail-secondary border-gmail-primary/30 focus:border-gmail-primary"
              />
            </div>
          </CardHeader>
          <CardContent className="flex-1 p-0">
            <ScrollArea className="h-[500px]">
              {filteredEmails.map((email, index) => (
                <div key={email.id}>
                  <div
                    className={`p-4 hover:bg-gmail-secondary/50 cursor-pointer transition-colors ${selectedEmail?.id === email.id ? 'bg-gmail-primary/10' : ''
                      }`}
                    onClick={() => {
                      setSelectedEmail(email);
                      if (!email.isRead) markAsRead(email.id);
                    }}
                  >
                    <div className="flex items-start gap-3">
                      <div className="mt-1">
                        {email.isRead ? (
                          <MailOpen className="w-4 h-4 text-gmail-read" />
                        ) : (
                          <Mail className="w-4 h-4 text-gmail-unread" />
                        )}
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-1">
                          <span className={`font-medium truncate ${email.isRead ? 'text-gmail-read' : 'text-foreground'
                            }`}>
                            {email.sender}
                          </span>
                          {email.isImportant && (
                            <Star className="w-3 h-3 text-gmail-important fill-current" />
                          )}
                          {email.hasAttachments && (
                            <Paperclip className="w-3 h-3 text-gmail-attachment" />
                          )}
                        </div>
                        <h3 className={`text-sm mb-1 truncate ${email.isRead ? 'text-gmail-read' : 'text-foreground font-medium'
                          }`}>
                          {email.subject}
                        </h3>
                        <p className="text-xs text-muted-foreground truncate mb-2">
                          {email.snippet}
                        </p>
                        <div className="flex items-center justify-between">
                          <div className="flex gap-1">
                            {email.labels.map(label => (
                              <Badge
                                key={label}
                                variant="secondary"
                                className="text-xs bg-gmail-primary/20 text-gmail-primary"
                              >
                                {label}
                              </Badge>
                            ))}
                          </div>
                          <div className="flex items-center gap-1 text-xs text-muted-foreground">
                            <Clock className="w-3 h-3" />
                            {email.date}
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                  {index < filteredEmails.length - 1 && <Separator className="bg-border/30" />}
                </div>
              ))}
            </ScrollArea>
          </CardContent>
        </Card>
      </div>

      {/* Visualizador de email */}
      <div className="w-1/2">
        <Card className="h-full bg-gradient-to-br from-card to-gmail-secondary border-gmail-primary/20">
          {selectedEmail ? (
            <>
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <h2 className="text-xl font-bold mb-2">{selectedEmail.subject}</h2>
                    <div className="flex items-center gap-2 text-sm text-muted-foreground">
                      <span>De: {selectedEmail.sender}</span>
                      <span>•</span>
                      <span>{selectedEmail.date}</span>
                    </div>
                  </div>
                  <div className="flex gap-1">
                    {selectedEmail.isImportant && (
                      <Star className="w-4 h-4 text-gmail-important fill-current" />
                    )}
                    {selectedEmail.hasAttachments && (
                      <Paperclip className="w-4 h-4 text-gmail-attachment" />
                    )}
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => analyzeEmail(selectedEmail.id)}
                      disabled={analyzing}
                      className="border-gmail-primary/30 hover:border-gmail-primary"
                    >
                      <Brain className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <ScrollArea className="h-[400px]">
                  <div className="prose prose-sm dark:prose-invert max-w-none">
                    <p className="whitespace-pre-wrap">{selectedEmail.body || selectedEmail.snippet}</p>

                    {/* Análise de IA */}
                    {aiAnalysis && (
                      <div className="mt-6 p-4 bg-gmail-secondary/30 rounded-lg border border-gmail-primary/20">
                        <div className="flex items-center gap-2 mb-3">
                          <Brain className="w-4 h-4 text-gmail-primary" />
                          <h3 className="font-semibold">Análise de IA</h3>
                        </div>
                        <div className="space-y-2 text-sm">
                          <div>
                            <strong>Resumo:</strong> {aiAnalysis.resumo}
                          </div>
                          <div className="flex gap-4">
                            <Badge variant="outline" className="text-xs">
                              Sentimento: {aiAnalysis.sentimento}
                            </Badge>
                            <Badge variant="outline" className="text-xs">
                              Urgência: {aiAnalysis.urgencia}
                            </Badge>
                            <Badge variant="outline" className="text-xs">
                              Categoria: {aiAnalysis.categoria}
                            </Badge>
                          </div>
                          {aiAnalysis.acoes_recomendadas && aiAnalysis.acoes_recomendadas.length > 0 && (
                            <div>
                              <strong>Ações recomendadas:</strong>
                              <ul className="list-disc list-inside mt-1">
                                {aiAnalysis.acoes_recomendadas.map((acao: string, index: number) => (
                                  <li key={index}>{acao}</li>
                                ))}
                              </ul>
                            </div>
                          )}
                        </div>
                      </div>
                    )}
                  </div>
                </ScrollArea>
              </CardContent>
            </>
          ) : (
            <CardContent className="flex items-center justify-center h-full">
              <div className="text-center text-muted-foreground">
                <Mail className="w-12 h-12 mx-auto mb-4 opacity-50" />
                <p>Selecione um email para visualizar</p>
              </div>
            </CardContent>
          )}
        </Card>
      </div>
    </div>
  );
};