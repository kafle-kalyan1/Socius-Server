from channels.generic.websocket import AsyncWebsocketConsumer
import json
from .models import Message, MessageNotification as Notification
from django.contrib.auth.models import User
from channels.db import database_sync_to_async
from UserData.models import Friendship
from django.db.models import Q


class ChatConsumer(AsyncWebsocketConsumer):
    
    @database_sync_to_async
    def get_friendship_uuid(self, username_from, username_to):
        user1 = User.objects.get(username=username_from)
        user2 = User.objects.get(username=username_to)
        friendship = Friendship.objects.get(
            (Q(user1=user1, user2=user2) | Q(user1=user2, user2=user1)),
            status='accepted'
        )

        # Return the UUID of user1 and user2's friendship
        return friendship.uuid
    
    async def connect(self):
        self.username_from = self.scope['url_route']['kwargs']['username_from']
        self.username_to = self.scope['url_route']['kwargs']['username_to']
        self.friendship_uuid = await self.get_friendship_uuid(self.username_from, self.username_to)
        self.room_group_name = f"chat_{self.friendship_uuid}"
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

        self.receiver_room_group_name = f"chat_{self.username_to}"
        
        await self.channel_layer.group_add(self.receiver_room_group_name, self.channel_name)


    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    @database_sync_to_async
    def save_message_to_database(self, sender, receiver, text, timestamp):
        # Save the message to the database
        message = Message.objects.create(
            sender=sender,
            receiver=receiver,
            message=text,
            timestamp=timestamp,
        )
        return message

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_text = text_data_json['message']
        sender = await database_sync_to_async(User.objects.get)(username=self.username_from)
        receiver = await database_sync_to_async(User.objects.get)(username=self.username_to)

        await self.save_message_to_database(sender, receiver, message_text, text_data_json['timestamp'])

        # print group details
        await self.create_notification(sender, receiver, message_text)

        # Broadcast the message to the group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'message',
                'message': message_text,
                'username_from': self.username_from,
                'username_to': self.username_to,
                'timestamp': text_data_json['timestamp'],
            }
        )
        
        await self.channel_layer.group_send(
            f"notifications_{self.username_to}",
            {
                'type': 'notification',
                'message': message_text,
                'sender': self.username_from,
                'timestamp': text_data_json['timestamp'],
            }
        )

    async def message(self, event):
        message = event['message']

        # Send the message to the WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'username_from': event['username_from'],
            'username_to': event['username_to'],
            'timestamp': event['timestamp'],
        }))
        
    @database_sync_to_async
    def create_notification(self, sender, receiver, message_text):
        notification = Notification.objects.create(
            sender=sender,
            receiver=receiver,
            message=message_text,
        )

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['url_route']['kwargs']['user']
        print(f"User {self.user} connected to notifications")
        await self.channel_layer.group_add(
                f"notifications_{self.user}",
                self.channel_name
            )
        await self.accept()
            

    async def disconnect(self, close_code):
        self.user = self.scope['url_route']['kwargs']['user']
        await self.channel_layer.group_discard(
            f"notifications_{self.user}",
            self.channel_name
        )
        
    async def notification(self, event):
        message = event['message']
        timestamp = event['timestamp']
        sender = event['sender']
        

        # Send the notification to the WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'timestamp': timestamp,
            'sender': sender,
        }))