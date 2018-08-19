"""Author: Trinity Core Team 

MIT License

Copyright (c) 2018 Trinity

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE."""

import requests
from wallet.configure import Configure
from common.log import LOG
import json
from wallet.utils import get_wallet_info, get_magic


class GatewayInfo(object):
    Spv_port = None

    @classmethod
    def update_spv_port(cls, port):
        cls.Spv_port = port

    @classmethod
    def get_spv_port(cls):
        return cls.Spv_port


def sync_channel(message_type, channel_name, founder, receiver, balance, asset_type):
    """

    :param message_type:
    :param channel_name:
    :param founder:
    :param receiver:
    :param balance:
    :param asset_type:
    :return:
    """

    message = {"MessageType": message_type,
               "AssetType": asset_type.upper(),
               "NetMagic": get_magic(),
               "MessageBody": {
                   "ChannelName": channel_name,
                   "Founder": founder,
                   "Receiver": receiver,
                   "Balance": balance
                  }
               }

    request = {
        "jsonrpc": "2.0",
        "method": "SyncChannel",
        "params": [message],
        "id": 1
    }
    result = requests.post(Configure["GatewayURL"], json=request)
    return result.json()


def sync_channel_list(channel_list):
    message = {"MessageType":"SyncChannelList",
               "AssetType": 'TNC',
               "NetMagic": get_magic(),
               "MessageBody":{
                   channel_list
               }}
    request = {
        "jsonrpc": "2.0",
        "method": "SyncChannel",
        "params": [message],
        "id": 1
    }
    result = requests.post(Configure["GatewayURL"], json=request)
    return result.json()


def join_gateway(wallet):
    """

    :param wallet:
    :return:
    """

    LOG.info("JoinGateway {}".format(wallet.address))
    messagebody = get_wallet_info(wallet)
    message = {
        "MessageType": "SyncWallet",
        "AssetType": 'TNC',
        "NetMagic": get_magic(),
        "MessageBody": messagebody
    }
    request = {
        "jsonrpc": "2.0",
        "method": "SyncWalletData",
        "params": [message],
        "id": 1
    }
    result = requests.post(Configure["GatewayURL"], json=request)
    return result.json()


def get_gw_bytes_encoding():
    """
    get gateway encoding method
    :return: string
    """
    return "utf-8"

def get_router_info(message):
    request = {
        "jsonrpc": "2.0",
        "method": "GetRouterInfo",
        "params": [message],
        "id": 1
    }
    result = requests.post(Configure["GatewayURL"], json=request)
    return result.json()


def send_message(message, method="TransactionMessage" ):
    LOG.info("GateWay Send Message: {}".format(json.dumps(message)))
    request= {
            "jsonrpc": "2.0",
            "method": method,
            "params": [message],
            "id": 1
    }
    result = requests.post(Configure["GatewayURL"], json=request)
    return result.json()

def close_wallet():
    message = {
        "MessageType": "CloseWallet",
        "NetMagic":get_magic(),
        "Ip": "{}:{}".format(Configure.get("NetAddress"), Configure.get("NetPort"))
    }
    request= {
        "jsonrpc": "2.0",
        "method": "CloseWallet",
        "params": [message],
        "id": 1
    }
    result = requests.post(Configure["GatewayURL"], json=request)
    return result.json()
