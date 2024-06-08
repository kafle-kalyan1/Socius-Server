from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import User
import json
from UserData.models import UserProfile
from channels.db import database_sync_to_async
from UserUtils.models import UserSettings


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
            
            if event_type in ['friend_request', 'accept_request']:
                receiver_username = data['receiver_username']
            else:
                receiver_username = data['receiver']
                
            print(receiver_username)
            
            receiver_settings = await self.get_user_settings(receiver_username)
            print(receiver_settings.friend_request_notification)


            if event_type == 'friend_request' and receiver_settings.friend_request_notification != 'none':
                sender_username = data['sender_username']
                receiver_username = data['receiver_username']
                profile_picture, fullname = await self.get_user_profile(sender_username)
                await self.channel_layer.group_send(
                    f"notifications_{receiver_username}",
                    {
                        'type': 'friend_request',
                        'message': 'You have a new friend request',
                        'sender': sender_username,
                        'profile_picture': profile_picture,
                        'fullname': fullname,
                    }
                )
                
            elif event_type == 'post_like' and receiver_settings.post_like_notification != 'none':
                liker_username = data['liker_username']
                receiver = data['receiver']
                post_id = data['post_id']
                profile_picture, fullname = await self.get_user_profile(liker_username)
                await self.channel_layer.group_send(
                    f"notifications_{receiver}",
                    {
                        'type': 'post_like',
                        'message': f'Your post has a new like',
                        'sender': liker_username,
                        'post': post_id,
                        'profile_picture': profile_picture,
                        'fullname': fullname,
                    }
                )
            
            elif event_type == 'message' and receiver_settings.message_notification != 'none':
                print("aayo yesma")
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

            elif event_type == 'accept_request' and receiver_settings.friend_request_notification != 'none':
                sender_username = data['sender_username']
                receiver_username = data['receiver_username']
                profile_picture, fullname = await self.get_user_profile(sender_username)
                await self.channel_layer.group_send(
                    f"notifications_{receiver_username}",
                    {
                        'type': 'accept_request',
                        'message': f'{sender_username} has accepted your friend request',
                        'sender': sender_username,
                        'profile_picture': profile_picture,
                        'fullname': fullname,
                    }
                )
            
            elif event_type == 'post_comment' and receiver_settings.post_comment_notification != 'none':
                commenter_username = data['commenter_username']
                receiver = data['receiver']
                post_id = data['post_id']
                comment = data['comment']
                profile_picture, fullname = await self.get_user_profile(commenter_username)
                await self.channel_layer.group_send(
                    f"notifications_{receiver}",
                    {
                        'type': 'post_comment',
                        'message': f'{fullname} has commented on your post "{comment.strip()[:20] + "..." if len(comment) > 20 else comment}"',
                        'sender': commenter_username,
                        'post': post_id,
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
        post = event['post']

        await self.send(text_data=json.dumps({
            'type': 'post_like',
            'message': message,
            'post':post,
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
        print(event)
        type = event['type']
        message = event['message']
        timestamp = event['timestamp']
        sender = event['sender']
        profile_picture = event['profile_picture']
        fullname = event['fullname']

        await self.send(text_data=json.dumps({
            'type': type,
            'message': message,
            'timestamp': timestamp,
            'sender': sender,
            'profile_picture': profile_picture,
            'fullname': fullname,
        }))
    
    async def accept_request(self, event):
        message = event['message']
        sender = event['sender']
        profile_picture = event['profile_picture']
        fullname = event['fullname']

        await self.send(text_data=json.dumps({
            'type': 'accept_request',
            'message': message,
            'sender': sender,
            'profile_picture': profile_picture,
            'fullname': fullname,
        }))
        
    async def post_comment(self, event):
        message = event['message']
        sender = event['sender']
        profile_picture = event['profile_picture']
        fullname = event['fullname']
        post = event['post']

        await self.send(text_data=json.dumps({
            'type': 'post_comment',
            'message': message,
            'post':post,
            'sender': sender,
            'profile_picture': profile_picture,
            'fullname': fullname,
        }))
        
    @database_sync_to_async
    def get_user_settings(self, username):
        user = User.objects.get(username=username)
        return UserSettings.objects.get(user=user)