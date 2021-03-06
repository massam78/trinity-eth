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

import json
from json.decoder import JSONDecodeError
from klein import Klein
from wallet.Interface.rpc_utils import json_response, cors_header
from wallet.channel import get_channel_via_name, query_channel_list
from common.log import LOG
from trinity import Configure
from blockchain.interface import get_balance
from wallet.channel import Channel
from wallet.channel.payment import Payment
from model.statistics_model import APIStatistics

MessageList = []


class CurrentLiveWallet(object):
    Wallet = None

    @classmethod
    def update_current_wallet(cls, wallet):
        cls.Wallet = wallet

    @classmethod
    def wallet_info(cls):
        if not cls.Wallet:
            return None
        balance = {}
        for i in Configure["AssetType"].keys():
            b = cls.Wallet.tnc_balance if i.upper() =="TNC" else get_balance(cls.Wallet.address, i.upper())
            balance[i] = b
        return {
                   "Publickey":cls.Wallet.address,
                   "CommitMinDeposit":Configure["CommitMinDeposit"],
                   "Fee":Configure["Fee"],
                   "alias":Configure["alias"],
                   "AutoCreate":Configure["AutoCreate"],
                   "MaxChannel":Configure["MaxChannel"],
                   "Balance":balance
                   }


class RpcError(Exception):


    message = None
    code = None

    def __init__(self, code, message):
        super(RpcError, self).__init__(message)
        self.code = code
        self.message = message

    @staticmethod
    def parseError(message=None):
        return RpcError(-32700, message or "Parse error")

    @staticmethod
    def methodNotFound(message=None):
        return RpcError(-32601, message or "Method not found")

    @staticmethod
    def invalidRequest(message=None):
        return RpcError(-32600, message or "Invalid Request")

    @staticmethod
    def internalError(message=None):
        return RpcError(-32603, message or "Internal error")


class RpcInteraceApi(object):
    app = Klein()
    port = None

    def __init__(self, port):
        self.port = port

    #
    # JSON-RPC API Route
    #
    @app.route('/')
    @json_response
    @cors_header
    def home(self, request):
        body = None
        request_id = None

        try:
            body = json.loads(request.content.read().decode("utf-8"))
            request_id = body["id"] if body and "id" in body else None

            if "jsonrpc" not in body or body["jsonrpc"] != "2.0":
                raise RpcError.invalidRequest("Invalid value for 'jsonrpc'")

            if "id" not in body:
                raise RpcError.invalidRequest("Field 'id' is missing")

            if "method" not in body:
                raise RpcError.invalidRequest("Field 'method' is missing")

            params = body["params"] if "params" in body else None
            result = self.json_rpc_method_handler(body["method"], params)
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": result
            }

        except JSONDecodeError as e:
            error = RpcError.parseError()
            return self._error_payload(request_id, error.code, error.message)

        except RpcError as e:
            return self._error_payload(request_id, e.code, e.message)

        except Exception as e:
            error = RpcError.internalError(str(e))
            return self._error_payload(request_id, error.code, error.message)

    def _error_payload(self, request_id, code, message):
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": code,
                    "message": message
                }
            }

    def json_rpc_method_handler(self, method, params):

        # if method == "SendRawtransaction":
        #     return transaction.TrinityTransaction.sendrawtransaction(params[0])

        if method == "TransactionMessage":
            LOG.info("<-- {}".format(params))
            return MessageList.append(params)

        # elif method == "FunderTransaction":
        #     return transaction.funder_trans(params)

        # elif method == "FunderCreate":
        #     return transaction.funder_create(params)

        # elif method == "RSMCTransaction":
        #     return transaction.rsmc_trans(params)
        #
        # elif method == "HTLCTransaction":
        #     return transaction.hltc_trans(params)

        elif method == "SyncWallet":
            from wallet import prompt as PR
            wallet_info = PR.CurrentLiveWallet.wallet_info()
            return {"MessageType":"SyncWallet",
               "MessageBody": wallet_info
               }

        elif method == "GetChannelState":
            return {'MessageType': 'GetChannelState',
                    'MessageBody': get_channel_via_name(params)}

        elif method == "GetChannelList":
            LOG.debug("GetChannelList")
            from wallet.utils import get_wallet_info
            if CurrentLiveWallet.Wallet:
                try:
                    channel_list = query_channel_list(CurrentLiveWallet.Wallet.url)
                except Exception as e:
                    channel_list= None
                    LOG.error(e)
                wallet_info = get_wallet_info(CurrentLiveWallet.Wallet)

                return {"MessageType":"GetChannelList",
                        "MessageBody":{"Channel":channel_list,
                                       "Wallet":wallet_info}}
            else:
                return {"MessageType": "GetChannelList",
                        "MessageBody": {"Error":"Wallet No Open"}
                }

        elif method == "GetPayment":
            asset_type = params[0]
            payment = params[1]

            try:
                hash_r, rcode = Payment.create_hr()
                pycode = Payment.generate_payment_code(CurrentLiveWallet.Wallet.url, asset_type, payment, hash_r)
                Channel.add_payment(None, hash_r, rcode, payment)
            except Exception as e:
                LOG.error(e)
                pycode = None

            return{"MessageType":"GetPaymentAck",
            	   "MessageBody": {"pycode":pycode}}


        elif method == "GetWalletStatistics":
            try:
                statistics_data = APIStatistics.query_statistics(params[0])[0]

            except Exception as e:
                LOG.error(e)

                return {"MessageType": "GetWalletStatisticsAck",
                        "MessageBody": {"Error": "data is null"}
                }
            else:

                return {"MessageType": "GetWalletStatisticsAck",
                        "MessageBody": json.loads(statistics_data.__str__())
                }

        # elif method == 'RefoundTrans':
        #     return transaction.refound_trans(params)



