from twisted.internet.protocol import Protocol, Factory, ClientFactory
from twisted.internet import reactor
from twisted.internet.endpoints import TCP4ServerEndpoint, TCP4ClientEndpoint
import argparse
import socks5
import struct
import json
import encryto


def get_options():
    parser = argparse.ArgumentParser(
        description=u"sock5 proxy")
    parser.add_argument(
        '-P', "--port", help=u"listen port default:8888", default=8888)
    return parser.parse_args()


class Client(Protocol):
    def __init__(self, s5):
        self.s5 = s5

    def ok(self, args):
        return args["succeed"]

    def dataReceived(self, data):
        data = encryto.encode(self.s5.box_index, data)
        self.s5.transport.write(data)


class CFactory(ClientFactory):
    def __init__(self, s5):
        self.s5 = s5

    def buildProtocol(self, addr):
        return Client(self.s5)


class Sock5Proto(Protocol):
    stage = 0
    client = None

    def __init__(self):
        self.conn = socks5.Connection(our_role="server")
        self.conn.initiate_connection()

    def connect_sever(self, host, port):
        endp = TCP4ClientEndpoint(
            reactor=reactor, host=host, port=port)
        ret = endp.connect(CFactory(self))
        ret.addCallback(self.connect_server_call_back)
        ret.addErrback(self.connect_server_err_call_back)

    def connect_server_call_back(self, ret):
        self.client = ret
        retmsg = self.conn.send(socks5.Response(
            status=socks5.RESP_STATUS["SUCCESS"],
            atyp=self.request.atyp,
            addr=self.request.addr,
            port=int(self.request.port)
        ))
        retmsg = encryto.encode(self.box_index, retmsg)
        self.transport.write(retmsg)
        self.stage = 2

    def connect_server_err_call_back(self, ret):
        retmsg = self.conn.send(socks5.Response(
            status=socks5.RESP_STATUS["HOST_UNREACHABLE"],
            atyp=self.request.atyp,
            addr=self.request.addr,
            port=int(self.request.port)
        ))
        retmsg = encryto.encode(self.box_index, retmsg)
        self.transport.write(retmsg)
        self.transport.loseConnection()

    def dataReceived(self, data):
        try:
            if self.stage == 0:
                index_data = data[:4]
                self.box_index = struct.unpack("I", index_data)[0]
                data = data[4:]
                data = encryto.decode(self.box_index, data)
                self.conn.recv(data)
                greeting_res = socks5.GreetingResponse(
                    socks5.AUTH_TYPE["NO_AUTH"])
                ret_data = self.conn.send(greeting_res)
                ret_data = encryto.encode(self.box_index, ret_data)
                self.transport.write(ret_data)
                self.stage = 1
            elif self.stage == 1:
                data = encryto.decode(self.box_index, data)
                self.request = self.conn.recv(data)
                self.connect_sever(self.request.addr, int(self.request.port))
            elif self.stage == 2:
                data = encryto.decode(self.box_index, data)
                self.client.transport.write(data)
        except:
            # print(e.with_traceback())
            self.transport.loseConnection()

    def connectionLost(self, reason):
        if self.client:
            self.client.transport.loseConnection()


class Sock5Facotry(Factory):
    def buildProtocol(self, addr):
        return Sock5Proto()


def start_server(port):
    endp = TCP4ServerEndpoint(reactor=reactor, port=port)
    endp.listen(Sock5Facotry())
    reactor.run()


if __name__ == "__main__":
    args = get_options()
    start_server(int((args.port)))
