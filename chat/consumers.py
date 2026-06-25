# chat/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone
from accounts.models import User
from servers.models import Channel, Server
from .models import Message, DirectMessage

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'
        
        # Присоединяемся к комнате
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Уведомляем о присоединении
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_join',
                'username': self.scope['user'].username,
                'user_id': self.scope['user'].id,
            }
        )
    
    async def disconnect(self, close_code):
        # Покидаем комнату
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        
        # Уведомляем о выходе
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_leave',
                'username': self.scope['user'].username,
            }
        )
    
    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data.get('type', 'message')
        
        if message_type == 'message':
            message = data['message']
            channel_id = data.get('channel_id')
            
            # Сохраняем сообщение в БД
            saved_message = await self.save_message(
                user=self.scope['user'],
                channel_id=channel_id,
                content=message
            )
            
            # Отправляем сообщение всем в комнате
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message,
                    'username': self.scope['user'].username,
                    'user_id': self.scope['user'].id,
                    'avatar': self.scope['user'].avatar.url if self.scope['user'].avatar else None,
                    'timestamp': saved_message.timestamp.isoformat() if saved_message else None,
                    'message_id': saved_message.id if saved_message else None,
                }
            )
        
        elif message_type == 'typing':
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'user_typing',
                    'username': self.scope['user'].username,
                }
            )
        
        elif message_type == 'delete_message':
            message_id = data.get('message_id')
            await self.delete_message(message_id)
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'message_deleted',
                    'message_id': message_id,
                }
            )
    
    async def chat_message(self, event):
        # Отправляем сообщение WebSocket
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': event['message'],
            'username': event['username'],
            'user_id': event['user_id'],
            'avatar': event.get('avatar'),
            'timestamp': event.get('timestamp'),
            'message_id': event.get('message_id'),
        }))
    
    async def user_typing(self, event):
        await self.send(text_data=json.dumps({
            'type': 'user_typing',
            'username': event['username'],
        }))
    
    async def user_join(self, event):
        await self.send(text_data=json.dumps({
            'type': 'user_join',
            'username': event['username'],
            'user_id': event['user_id'],
        }))
    
    async def user_leave(self, event):
        await self.send(text_data=json.dumps({
            'type': 'user_leave',
            'username': event['username'],
        }))
    
    async def message_deleted(self, event):
        await self.send(text_data=json.dumps({
            'type': 'message_deleted',
            'message_id': event['message_id'],
        }))
    
    @database_sync_to_async
    def save_message(self, user, channel_id, content):
        try:
            channel = Channel.objects.get(id=channel_id)
            message = Message.objects.create(
                channel=channel,
                author=user,
                content=content
            )
            return message
        except Channel.DoesNotExist:
            return None
    
    @database_sync_to_async
    def delete_message(self, message_id):
        try:
            message = Message.objects.get(id=message_id)
            if message.author == self.scope['user']:
                message.delete()
        except Message.DoesNotExist:
            pass

class DirectMessageConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        self.room_name = f'dm_{min(self.user.id, int(self.scope["url_route"]["kwargs"]["user_id"]))}_{max(self.user.id, int(self.scope["url_route"]["kwargs"]["user_id"]))}'
        self.room_group_name = f'dm_{self.room_name}'
        
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
    
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']
        recipient_id = data['recipient_id']
        
        # Сохраняем личное сообщение
        saved_dm = await self.save_direct_message(
            sender=self.user,
            recipient_id=recipient_id,
            content=message
        )
        
        # Отправляем сообщение в комнату
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'dm_message',
                'message': message,
                'sender_id': self.user.id,
                'sender_username': self.user.username,
                'avatar': self.user.avatar.url if self.user.avatar else None,
                'timestamp': saved_dm.timestamp.isoformat() if saved_dm else None,
            }
        )
    
    async def dm_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'dm_message',
            'message': event['message'],
            'sender_id': event['sender_id'],
            'sender_username': event['sender_username'],
            'avatar': event.get('avatar'),
            'timestamp': event.get('timestamp'),
        }))
    
    @database_sync_to_async
    def save_direct_message(self, sender, recipient_id, content):
        try:
            recipient = User.objects.get(id=recipient_id)
            dm = DirectMessage.objects.create(
                sender=sender,
                recipient=recipient,
                content=content
            )
            return dm
        except User.DoesNotExist:
            return None