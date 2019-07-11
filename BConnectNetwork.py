import zmq,threading,time,traceback

pubsubNetwork = None
showLog = True



class PubSubNetwork:
    forwarderSubPort = "5559"
    forwarderPubPort = "5560"

    forwarderRunning = False
    forwarderThread = None

    forwarderSubscriberRunning = False
    forwarderSubscriberThread = None

    listeners = {}


    subscribeSocket = None

    def __init__(self,subPort="5559",pubPort="5560"):
        self.forwarderPubPort = pubPort
        self.forwarderSubPort = subPort

        self.initPublisherSocket()
        self.start_threads()

    def initPublisherSocket(self):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PUB)
        print("b: %s" % self.forwarderSubPort)
        self.socket.connect("tcp://localhost:%s" % self.forwarderSubPort)

    # send data to the forwarder with a given topic
    def publish(self,topic,messagedata):
        print("SEND:%s %s" % (topic, messagedata))
        self.socket.send_multipart([str.encode(topic),messagedata])
        #self.socket.send_string( "%s %s" % (topic, messagedata))

    def add_listener(self,topicName, func):
        topicName = str(topicName,"utf-8")
        if topicName not in self.listeners:
            self.listeners[topicName]=[]
            self.subscribeSocket.setsockopt(zmq.SUBSCRIBE, str.encode(topicName))

        self.listeners[topicName].append(func)
        


    def start_threads(self):
        ## see: https://learning-0mq-with-pyzmq.readthedocs.io/en/latest/pyzmq/devices/forwarder.html
        def thread_forwarder():
            context = zmq.Context(1)
            # Socket facing clients
            frontend = context.socket(zmq.SUB)
            frontend.bind("tcp://*:%s" % self.forwarderSubPort)

            frontend.setsockopt(zmq.SUBSCRIBE, b"")

            # Socket facing services
            backend = context.socket(zmq.PUB)
            backend.bind("tcp://*:%s" % self.forwarderPubPort)

            zmq.device(zmq.FORWARDER, frontend, backend)
            frontend.close()
            backend.close()
            context.term()

        def thread_forwarder_subscriber():
            # Socket to talk to server
            context = zmq.Context()
            self.subscribeSocket = context.socket(zmq.SUB)
            print ("Collecting updates from server...")
            self.subscribeSocket.connect ("tcp://localhost:%s" % self.forwarderPubPort)
            topicfilter = b"blender"
            self.subscribeSocket.setsockopt(zmq.SUBSCRIBE, topicfilter)
            while True:
                info,data = self.subscribeSocket.recv_multipart()
                print("INCOMING")
                topic, subtype, datatype = str(info,"utf-8").split()
                
                if showLog:
                    print ("network: Topic:%s Subtype:%s dataType:%s"%(topic, subtype,datatype))

                print("listeners %s" %self.listeners)
                if topic in self.listeners.keys():
                    print("--1")
                    for l in self.listeners[topic]:
                        print("--2")
                        try:
                            if (datatype == "text"):
                                print("--3")
                                l(topic,subtype,str(data,"utf-8"))
                            elif (datatype == "bin"):
                                l(topic,subtype,data);
                            else:
                                l(topic,subtype,data)
                        except Exception:
                            print(traceback.format_exc())


        self.forwarderThread = threading.Thread(target=thread_forwarder)
        self.forwarderThread.setDaemon(True)
        self.forwarderThread.start()
        self.forwarderRunning = True

        self.forwarderSubscriberThread = threading.Thread(target=thread_forwarder_subscriber)
        self.forwarderSubscriberThread.setDaemon(True)
        self.forwarderSubscriberThread.start()
        self.forwarderSubscriberRunning=True


def StartNetwork():
    print("STARTING BConnect")
    global pubsubNetwork
    if not pubsubNetwork:
        pubsubNetwork = PubSubNetwork()

def StopNetwork():
    print("Stop network not supported atm")

def AddListener(topic,func):
    global pubsubNetwork

    if not pubsubNetwork:
        return
    
    pubsubNetwork.add_listener(topic,func)


def Publish(topic,data):
    pubsubNetwork.publish(topic,data)

def SetShowLog(showIt):
    global showLog
    showLog = showIt

def NetworkRunning():
    return pubsubNetwork and pubsubNetwork.forwarderSubscriberRunning