"""
    Copyright (C) 2017, ContraxSuite, LLC

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as
    published by the Free Software Foundation, either version 3 of the
    License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

    You can also be released from the requirements of the license by purchasing
    a commercial license from ContraxSuite, LLC. Buying such a license is
    mandatory as soon as you develop commercial activities involving ContraxSuite
    software without disclosing the source code of your own applications.  These
    activities include: offering paid services to customers as an ASP or "cloud"
    provider, processing documents on the fly in a web application,
    or shipping ContraxSuite within a closed source product.
"""
# -*- coding: utf-8 -*-

import json
from typing import Dict, Set
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
from apps.task.utils.logger import get_django_logger

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2019, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.3.0/LICENSE"
__version__ = "1.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class SubscriptionConsumer(WebsocketConsumer):
    """
    Class SubscriptionConsumer process all WS client connections by URL
    like r"^subscription/$". WS client subscribes / unsubscribes
    from a number of channels.
    Somewhere in BL code sends messages (ChannelMessage) to the channels
    through ChannelBroadcasting class.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.groups_by_channel = {}  # type: Dict[str, Set[str]]
        self.logger = get_django_logger()

    def send_message(self, event):
        self.send(text_data=json.dumps(event['content']))

    def connect(self):
        self.username = "Anonymous"
        self.accept()

    def receive(self, text_data=None, bytes_data=None):
        # expects message like
        # '{"message": "subscribe", "channels":["fields"]}'
        try:
            msg_obj = json.loads(text_data)
        except:
            self.logger.error(f'Malformatted message: "{text_data}"')
            return

        if 'message' not in msg_obj:
            self.logger.error(f'Malformatted message: "{text_data}"'
                              ' - no "message" field declared')
            return

        if msg_obj['message'] == 'subscribe':
            self.process_subscribe_message(text_data, msg_obj)
            return

        if msg_obj['message'] == 'unsubscribe':
            self.process_unsubscribe_message(msg_obj)
            return

    def disconnect(self, message) -> None:
        if self.channel_name not in self.groups_by_channel:
            return
        groups = self.groups_by_channel[self.channel_name]
        for gr in groups:
            async_to_sync(self.channel_layer.group_discard)(
                gr, self.channel_name)
            print(f'Channel {self.channel_name} unsubscribed from "{gr}"')
        self.groups_by_channel.pop(self.channel_name, None)

    def process_subscribe_message(self,
                                  message_text: str, message_obj) -> None:
        if 'channels' not in message_obj:
            self.logger.error(
                f'Malformatted subscribe message: "{message_text}"'
                ' - no "channels" field declared')
            return

        channels = message_obj['channels']
        if len(channels) == 0:
            return
        for channel in channels:
            async_to_sync(self.channel_layer.group_add)(channel,
                                                        self.channel_name)
            print(f'Channel {self.channel_name} subscribed on "{channel}"')
        if self.channel_name in self.groups_by_channel:
            self.groups_by_channel[self.channel_name].update(channels)
        else:
            self.groups_by_channel[self.channel_name] = {c for c in channels}

    def process_unsubscribe_message(self, message_obj) -> None:
        groups = message_obj.get('channels') or list(self.groups_by_channel[self.channel_name])

        for gr in groups:
            async_to_sync(self.channel_layer.group_discard)(gr,
                                                            self.channel_name)
            try:
                self.groups_by_channel[self.channel_name].remove(gr)
            except:
                pass
            print(f'Channel {self.channel_name} unsubscribed from "{gr}"')

        if not self.groups_by_channel[self.channel_name]:
            self.groups_by_channel.pop(self.channel_name, None)
