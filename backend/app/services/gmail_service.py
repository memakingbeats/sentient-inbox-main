from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import base64
import email
from typing import List, Dict, Any, Optional
import json
import os
from datetime import datetime, timedelta
import httpx

class GmailService:
    
    def __init__(self):
        self.SCOPES = [
            'https://www.googleapis.com/auth/gmail.readonly',
            'https://www.googleapis.com/auth/gmail.modify'
        ]
        self.credentials_path = "credentials/google_credentials.json"
        
    async def exchange_code_for_tokens(self, code: str, redirect_uri: str) -> Dict[str, Any]:
        """
        Troca um código de autorização do Google OAuth por tokens de acesso/refresh
        
        Args:
            code: O código de autorização retornado pelo Google
            redirect_uri: A URI de redirecionamento registrada
            
        Returns:
            Dicionário com tokens (access_token, refresh_token, etc)
        """
        token_url = "https://oauth2.googleapis.com/token"
        data = {
            "code": code,
            "client_id": os.getenv("GOOGLE_CLIENT_ID"),
            "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(token_url, data=data)
            return response.json()
        
    def get_credentials_from_token(self, token_info: Dict[str, Any]) -> Credentials:
        """Cria credenciais a partir do token"""
        return Credentials(
            token=token_info.get('access_token'),
            refresh_token=token_info.get('refresh_token'),
            token_uri="https://oauth2.googleapis.com/token",
            client_id=token_info.get('client_id'),
            client_secret=token_info.get('client_secret'),
            scopes=self.SCOPES
        )
    
    def build_service(self, credentials: Credentials):
        """Constrói serviço Gmail"""
        return build('gmail', 'v1', credentials=credentials)
    
    def get_emails(self, credentials: Credentials, max_results: int = 50) -> List[Dict[str, Any]]:
        """Busca emails da caixa de entrada"""
        try:
            service = self.build_service(credentials)
            
            # Buscar emails
            results = service.users().messages().list(
                userId='me',
                labelIds=['INBOX'],
                maxResults=max_results
            ).execute()
            
            messages = results.get('messages', [])
            emails = []
            
            for message in messages:
                msg = service.users().messages().get(
                    userId='me',
                    id=message['id'],
                    format='full'
                ).execute()
                
                email_data = self._parse_email_message(msg)
                emails.append(email_data)
            
            return emails
            
        except HttpError as error:
            print(f'Erro ao buscar emails: {error}')
            return []
        
    def _parse_email_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Parseia mensagem do Gmail"""
        headers = message['payload']['headers']
        
        # Extrair informações básicas
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'Sem assunto')
        sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Desconhecido')
        date = next((h['value'] for h in headers if h['name'] == 'Date'), '')
        
        # Extrair corpo do email
        body = self._extract_email_body(message['payload'])
        
        # Processar labels
        labels = message.get('labelIds', [])
        
        return {
            'id': message['id'],
            'threadId': message['threadId'],
            'subject': subject,
            'sender': sender,
            'date': date,
            'body': body,
            'labels': labels,
            'snippet': message.get('snippet', ''),
            'isRead': 'UNREAD' not in labels,
            'isImportant': 'IMPORTANT' in labels,
            'hasAttachments': 'ATTACHMENT' in labels
        }
    
    def _extract_email_body(self, payload: Dict[str, Any]) -> str:
        """Extrai corpo do email"""
        if 'body' in payload and payload['body'].get('data'):
            return base64.urlsafe_b64decode(
                payload['body']['data'].encode('ASCII')
            ).decode('utf-8')
        
        if 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    if 'data' in part['body']:
                        return base64.urlsafe_b64decode(
                            part['body']['data'].encode('ASCII')
                        ).decode('utf-8')
        
        return ""
    
    def mark_as_read(self, credentials: Credentials, message_id: str) -> bool:
        """Marca email como lido"""
        try:
            service = self.build_service(credentials)
            service.users().messages().modify(
                userId='me',
                id=message_id,
                body={'removeLabelIds': ['UNREAD']}
            ).execute()
            return True
        except HttpError as error:
            print(f'Erro ao marcar como lido: {error}')
            return False
    
    def get_email_thread(self, credentials: Credentials, thread_id: str) -> List[Dict[str, Any]]:
        """Busca thread completa de emails"""
        try:
            service = self.build_service(credentials)
            thread = service.users().threads().get(
                userId='me',
                id=thread_id
            ).execute()
            
            emails = []
            for message in thread['messages']:
                email_data = self._parse_email_message(message)
                emails.append(email_data)
            
            return emails
            
        except HttpError as error:
            print(f'Erro ao buscar thread: {error}')
            return []