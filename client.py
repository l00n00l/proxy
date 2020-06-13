from twisted.internet.protocol import Protocol, Factory, ClientFactory
from twisted.internet import reactor
from twisted.internet.endpoints import TCP4ServerEndpoint, TCP4ClientEndpoint
import encodings.idna
import argparse
import socks5
import struct
import json
import encryto


server_host = "localhost"
server_port = 8888


def get_options():
    parser = argparse.ArgumentParser(
        description=u"sock5 proxy")
    parser.add_argument("server_host", help="server host")
    parser.add_argument("server_port", help="server port")
    parser.add_argument(
        '-P', "--port", help=u"listen port default:1080", default=1080)
    return parser.parse_args()


class Client(Protocol):
    def __init__(self, s5):
        self.s5 = s5

    def ok(self, args):
        return args["succeed"]

    def dataReceived(self, data):
        data = encryto.decode(self.s5.box_index, data)
        self.s5.transport.write(data)

    def connectionMade(self):
        msg = struct.pack("I", self.s5.box_index)
        self.transport.write(msg)


class CFactory(ClientFactory):
    def __init__(self, s5):
        self.s5 = s5

    def buildProtocol(self, addr):
        return Client(self.s5)


class Sock5Proto(Protocol):
    stage = 0
    client = None
    msg_cache = []

    def __init__(self):
        self.conn = socks5.Connection(our_role="server")
        self.conn.initiate_connection()
        self.connect_sever(server_host, server_port)
        self.box_index = encryto.rand_index()

    def connect_sever(self, host, port):
        endp = TCP4ClientEndpoint(
            reactor=reactor, host=host, port=port)
        ret = endp.connect(CFactory(self))
        ret.addCallback(self.connect_server_call_back)
        ret.addErrback(self.connect_server_err_call_back)

    def connect_server_call_back(self, ret):
        self.client = ret
        for msg in self.msg_cache:
            data = encryto.encode(self.box_index, msg)
            self.client.transport.write(data)
        self.msg_cache = []

    def connect_server_err_call_back(self, ret):
        self.transport.loseConnection()

    def dataReceived(self, data):
        if self.client:
            data = encryto.encode(self.box_index, data)
            self.client.transport.write(data)
        else:
            self.msg_cache.append(data)

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
    server_host = args.server_host
    server_port = int(args.server_port)
    start_server(int((args.port)))
