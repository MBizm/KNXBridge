"""
"""

import threading


class BaseConnection(threading.Thread):
    """
    """
    def __init__(self, *args, **kwargs):
        """
        """
        super(BaseConnection, self).__init__(*args, **kwargs)

        self._run = False

    def stop():
        """
        """
        self._run = True


class KnxConnection(BaseConnection):
    """
    """
    def __init__(self, telegramListener, url="localhost"):
        """
        """
        super(KnxConnection, self).__init__()

        self._url = url
        self._telegramListener = telegramListener

        self._eibConnection = None
        self._stop = self._run = False

    #def run(self):
        #"""
        #"""
        #while not self._stop:
            #self._eibConnection = EIBConnection.EIBSocketUrl(self._url)
            #if self._eibConnection == 0:
            #{
                #EIBSetEvent (con_m, stop_m);
                #if (EIBOpen_GroupSocket (con_m, 0) != -1)
                #{
                    #logger_m.infoStream() << "KnxConnection: Group socket opened. Waiting for messages." << endlog;
                    #int retval;
                    #while ((retval = checkInput()) > 0)
                    #{
                        #/*        TODO: find another way to check if event occured
                                #struct timeval tv;
                                #tv.tv_sec = 1;
                                #tv.tv_usec = 0;
                                #pth_select_ev(0,0,0,0,&tv,stop);
                        #*/
                    #}
                    #if (retval == -1)
                        #retry = false;
                #}
                #else
                    #logger_m.errorStream() << "Failed to open group socket." << endlog;

                #if (con_m)
                    #EIBClose(con_m);
                #con_m = 0;
            #}
            #else
                #logger_m.errorStream() << "Failed to open knxConnection url." << endlog;
            #if (retry)
            #{
                #struct timeval tv;
                #tv.tv_sec = 60;
                #tv.tv_usec = 0;
                #pth_select_ev(0,0,0,0,&tv,stop_m);
                #if (pth_event_status (stop_m) == PTH_STATUS_OCCURRED)
                    #retry = false;
            #}
        #}
        #logger_m.infoStream() << "Out of KnxConnection loop." << endlog;

        ##pth_event_free (stop_m, PTH_FREE_THIS);  # use Event

        #self._run = False    # use Event

    #def write(gad, buffer_):
        #"""
        #"""
        #if(gad == 0)
            #return;
        #logger_m.infoStream() << "write(gad=" << Object::WriteGroupAddr(gad) << ", buf, len=" << len << ")" << endlog;
        #if (con_m)
        #{
            #len = EIBSendGroup (con_m, gad, len, buf);
            #if (len == -1)
            #{
                #logger_m.errorStream() << "Write request failed (gad=" << Object::WriteGroupAddr(gad) << ", buf, len=" << len << ")" << endlog;
            #}
            #else
            #{
                #logger_m.debugStream() << "Write request sent" << endlog;
            #}
        #}

    #def checkInput(self):
        #"""
        #"""
        #int len;
        #eibaddr_t dest;
        #eibaddr_t src;
        #uint8_t buf[200];
        #if (!con_m)
            #return 0;
        #len = EIBGetGroup_Src (con_m, sizeof (buf), buf, &src, &dest);
        #if (pth_event_status (stop_m) == PTH_STATUS_OCCURRED)
            #return -1;
        #if (len == -1)
        #{
            #logger_m.errorStream() << "Read failed" << endlog;
            #return 0;
        #}
        #if (len < 2)
        #{
            #logger_m.warnStream() << "Invalid Packet (too short)" << endlog;
            #return 0;
        #}
        #if (buf[0] & 0x3 || (buf[1] & 0xC0) == 0xC0)
        #{
            #logger_m.warnStream() << "Unknown APDU from "<< src << " to " << dest << endlog;
        #}
        #else
        #{
            #if (logger_m.isDebugEnabled())
            #{
                #DbgStream dbg = logger_m.debugStream();
                #switch (buf[1] & 0xC0)
                #{
                #case 0x00:
                    #dbg << "Read";
                    #break;
                #case 0x40:
                    #dbg << "Response";
                    #break;
                #case 0x80:
                    #dbg << "Write";
                    #break;
                #}
                #dbg << " from " << Object::WriteAddr(src) << " to " << Object::WriteGroupAddr(dest);
                #if (buf[1] & 0xC0)
                #{
                    #dbg << ": " << std::hex << std::setfill ('0') << std::setw (2);
                    #if (len == 2)
                        #dbg << (int)(buf[1] & 0x3F);
                    #else
                    #{
                        #for (uint8_t *p = buf+2; p < buf+len; p++)
                            #dbg << (int)*p << " ";
                    #}
                #}
                #dbg << std::dec << endlog;
            #}
            #if (listener_m)
            #{
                #switch (buf[1] & 0xC0)
                #{
                #case 0x00:
                    #listener_m->onRead(src, dest, buf, len);
                    #break;
                #case 0x40:
                    #listener_m->onResponse(src, dest, buf, len);
                    #break;
                #case 0x80:
                    #listener_m->onWrite(src, dest, buf, len);
                    #break;
                #}
            #}
        #}
        #return 1;

    def isRunning(self):
        """
        """
        return self._run
