
"""
"""

import SocketServer


class BaseConnectionHandler(SocketServer.BaseRequestHandler):
    """
    """


class BaseConnectionServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    """
    """
    def __init__(self, *args, **kwargs):
        """
        """
        super(BaseConnectionServer, self).__init__(*args, **kwargs)

    def start():
        """
        """
        self.serve_forever()

    def stop():
        """
        """
        self.shutdown()


class KnxConnectionHandler(BaseConnectionHandler):
    """
    """
    def handle(self):
        """
        """

        # self.request is the TCP socket connected to the client
        self.data = self.request.recv(1024).strip()
        print "{} wrote:".format(self.client_address[0])
        print self.data

        # just send back the same data, but upper-cased
        self.request.sendall(self.data.upper())


class KnxConnectionServer(BaseConnectionServer):
    """
    """
    def __init__(self, *args, **kwargs):
        """
        """
        super(KnxConnectionServer, self).__init__(*args, **kwargs)

        #EIBConnection *con_m;
        #bool isRunning_m;
        #pth_event_t stop_m;
        #std::string url_m;
        #TelegramListener *listener_m;

    #void addTelegramListener(TelegramListener *listener);
    #bool removeTelegramListener(TelegramListener *listener);
    #void write(eibaddr_t gad, uint8_t* buf, int len);
    #int checkInput();

#private:

    #void Run(pth_sem_t * stop);
    #static KnxLogger& knxLogger




if __name__ == "__main__":
    HOST, PORT = "localhost", 9999

    # Create the server, binding to localhost on port 9999
    server = SocketServer.TCPServer((HOST, PORT), MyTCPHandler)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C (except if a client is still connected)
    server.serve_forever()
