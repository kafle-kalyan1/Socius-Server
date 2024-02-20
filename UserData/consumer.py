from channels.generic.websocket import AsyncWebsocketConsumer
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.contrib.auth import get_user_model
from UserData.models import UserProfile
from Notification.models import Notification
import json


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        self.group_name = f'notification_{self.user.id}'

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        from_user = get_user_model().objects.get(id=text_data_json['from_user_id'])
        to_user = get_user_model().objects.get(id=text_data_json['to_user_id'])
        notification = Notification.objects.create(from_user=from_user, to_user=to_user)

        from_user_profile = UserProfile.objects.get(user=from_user)
        full_name = from_user_profile.fullname
        profile_image = from_user_profile.profile_picture if from_user_profile.profile_picture else None

        # Send message to room group
        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'send_notification',
                'message': text_data_json['message'],
                'full_name': full_name,
                'profile_image': profile_image,
            }
        )

    async def send_notification(self, event):
        message = event['message']
        full_name = event['full_name']
        profile_image = event['profile_image']

        await self.send(text_data=json.dumps({
            'message': message,
            'full_name': full_name,
            'profile_image': profile_image,
        }))