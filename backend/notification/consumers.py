import json
import logging

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from channels.db import database_sync_to_async
from social import models

logger = logging.getLogger(__name__)


class NotificationConsumer(WebsocketConsumer):
    def connect(self):
        self.user_id = self.scope["url_route"]["kwargs"]["user_id"]
        self.token = self.scope["query_string"].decode("utf-8").split("=")[1]
        self.group_name = f"notification_{self.user_id}_{self.token}"
        self.account = models.Account.objects.get(
            id=self.user_id, notification_token=self.token
        )
        if not self.account:
            self.close()
            return

        async_to_sync(self.channel_layer.group_add)(self.group_name, self.channel_name)

        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.group_name, self.channel_name
        )
        self.account.notification_token = None
        self.account.save()

    def send_notification(self, event):
        self.send(text_data=json.dumps({"message": event["message"]}))
