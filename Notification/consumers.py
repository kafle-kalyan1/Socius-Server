from channels.generic.websocket import AsyncWebsocketConsumer
import json

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