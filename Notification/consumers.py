from channels.generic.websocket import AsyncWebsocketConsumer
import json
from UserData.models import UserProfile
from channels.db import database_sync_to_async


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['url_route']['kwargs']['user']
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
    
    async def receive(self, text_data):
        try:
            text_data_json = json.loads(text_data)
            event_type = text_data_json['type']
            data = text_data_json['data']

            if event_type == 'friend_request':
                sender_username = data['sender_username']
                profile_picture, fullname = await self.get_user_profile(sender_username)
                await self.channel_layer.group_send(
                    f"notifications_{sender_username}",
                    {
                        'type': 'friend_request',
                        'message': 'You have a new friend request',
                        'sender': sender_username,
                        'profile_picture': profile_picture,
                        'fullname': fullname,
                    }
                )
                
            elif event_type == 'post_like':
                liker_username = data['liker_username']
                post_id = data['post_id']
                profile_picture, fullname = await self.get_user_profile(liker_username)
                await self.channel_layer.group_send(
                    f"notifications_{liker_username}",
                    {
                        'type': 'post_like',
                        'message': f'Your post {post_id} has a new like',
                        'sender': liker_username,
                        'profile_picture': profile_picture,
                        'fullname': fullname,
                    }
                )
            
            elif event_type == 'message':
                sender_username = data['sender_username']
                profile_picture, fullname = await self.get_user_profile(sender_username)
                await self.channel_layer.group_send(
                    f"notifications_{sender_username}",
                    {
                        'type': 'message',
                        'message': 'You have a new message',
                        'timestamp': data['timestamp'],
                        'sender': sender_username,
                        'profile_picture': profile_picture,
                        'fullname': fullname,
                    }
                )
        except Exception as e:
            print(e)
            
    
    @database_sync_to_async
    def get_user_profile(self, username):
        user_profile = UserProfile.objects.get(user__username=username)
        return user_profile.profile_picture, user_profile.fullname
    
    async def friend_request(self, event):
        message = event['message']
        sender = event['sender']
        profile_picture = event['profile_picture']
        fullname = event['fullname']

        await self.send(text_data=json.dumps({
            'type': 'friend_request',
            'message': message,
            'sender': sender,
            'profile_picture': profile_picture,
            'fullname': fullname,
        }))
        
    async def post_like(self, event):
        message = event['message']
        sender = event['sender']
        profile_picture = event['profile_picture']
        fullname = event['fullname']

        await self.send(text_data=json.dumps({
            'type': 'post_like',
            'message': message,
            'sender': sender,
            'profile_picture': profile_picture,
            'fullname': fullname,
        }))
    
    async def notification(self, event):
        message = event['message']
        timestamp = event['timestamp']
        sender = event['sender']
        profile_picture, fullname = await self.get_user_profile(sender)


        # Send the notification to the WebSocket
        await self.send(text_data=json.dumps({
            'type': "notification",
            'message': message,
            'timestamp': timestamp,
            'sender': sender,
            'profile_picture': profile_picture,
            'fullname': fullname,
        }))
        
    async def message(self, event):
        message = event['message']
        timestamp = event['timestamp']
        sender = event['sender']
        profile_picture = event['profile_picture']
        fullname = event['fullname']

        await self.send(text_data=json.dumps({
            'type': 'message',
            'message': message,
            'timestamp': timestamp,
            'sender': sender,
            'profile_picture': profile_picture,
            'fullname': fullname,
        }))