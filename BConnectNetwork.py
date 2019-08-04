import zmq,threading,time,traceback,json

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

    def __init__(self,subPort="5559",pubPort="5560",initialFilter=b"all",startThreads=True):
        self.forwarderPubPort = pubPort
        self.forwarderSubPort = subPort
        self.initialFilter = initialFilter
        print("init %s %s" %(initialFilter,startThreads))
        self.initPublisherSocket()
        if startThreads:
            self.start_threads()

    def initPublisherSocket(self):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PUB)
        print("b: %s" % self.forwarderSubPort)
        self.socket.connect("tcp://localhost:%s" % self.forwarderSubPort)

    # send data to the forwarder with a given topic
    def publish(self,topic,meta,messagedata):
        #print("SEND:%s %s" % (topic, messagedata))
        if type(topic) is str:
            topic = str.encode(topic)
        if type(meta) is str:
            meta = str.encode(meta)

        self.socket.send_multipart([topic,meta,messagedata])
        print("Sent....")
        #self.socket.send_string( "%s %s" % (topic, messagedata))

    def add_listener(self,topicName, func):
        if (type(topicName) is bytes):
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
            print ("Collecting updates from server...%s" % self.forwarderSubPort)
            self.subscribeSocket.connect ("tcp://localhost:%s" % self.forwarderPubPort)
            
            self.subscribeSocket.setsockopt(zmq.SUBSCRIBE, self.initialFilter)
            while True:
                info,meta,data = self.subscribeSocket.recv_multipart()
                topic, subtype, datatype = str(info,"utf-8").split()
                print("INCOMING topic:%s subtype:%s datatype:%s" % (topic,subtype,datatype))
                meta = str(meta,"utf-8")
                if meta =="":
                    meta=None
                else:
                    meta = json.loads(meta)

                if showLog:
                    print ("network: Topic:%s Subtype:%s dataType:%s"%(topic, subtype,datatype))
                print("listeners %s" %self.listeners)
                if topic in self.listeners.keys():
                    print("--1")
                    topicListeners = self.listeners[topic]
                    removeList = []
                    for l in topicListeners:
                        print("--2")
                        
                        ## TODO: Find a better sanity test to see if the reference is valid. (What an insane sanity-check ;) )
                        # try:
                        #     check = hasattr(l.__self__,"__blenderconnect_tester")
                        # except ReferenceError:
                        #     removeList.append(l)
                        #     continue
                        # except:
                        #     pass

                        try:
                            if datatype == "text":
                                print("--3")
                                l(topic,subtype,meta,str(data,"utf-8"))
                            elif datatype == "json":
                                jsonAsDict = json.loads(str(data,"utf-8"))
                                l(topic,subtype,meta,jsonAsDict)
                            elif (datatype == "bin"):
                                print("received data-blob length:%s" % len(data))
                                l(topic,subtype,meta,data);
                            else:
                                l(topic,subtype,meta,data)
                        except ReferenceError:
                            print("!!Referror!! removing element: %s" % str(l));
                            removeList.append(l)
                        except Exception:
                            print("Listener error for ")
                            print(traceback.format_exc())
                    if (len(removeList)>0):
                        for removeElement in removeList:
                            topicListeners.remove(removeElement)
                        
                        

        self.forwarderThread = threading.Thread(target=thread_forwarder)
        self.forwarderThread.setName("blender-connect-forwarder")
        self.forwarderThread.setDaemon(True)
        self.forwarderThread.start()
        self.forwarderRunning = True

        self.forwarderSubscriberThread = threading.Thread(target=thread_forwarder_subscriber)
        self.forwarderSubscriberThread.setName("blender-connect-subscriber")
        self.forwarderSubscriberThread.setDaemon(True)
        self.forwarderSubscriberThread.start()
        self.forwarderSubscriberRunning=True


def StartNetwork(subPort="5559",pubPort="5560",initialFilter=b"",startThreads=True):
    print("STARTING BConnect")
    global pubsubNetwork
    if not pubsubNetwork:
        print("ST%s %s" % (startThreads,initialFilter))
        pubsubNetwork = PubSubNetwork(subPort,pubPort,initialFilter,startThreads)

def StopNetwork():
    print("Stop network not supported atm")

def AddListener(topic,func):
    global pubsubNetwork

    if not pubsubNetwork:
        return
    
    pubsubNetwork.add_listener(topic,func)


def Publish(topic,subtype,datatype,data,meta=""):
    full_topic = "%s %s %s" % (topic,subtype,datatype)
    pubsubNetwork.publish(full_topic,meta,data)

def SetShowLog(showIt):
    global showLog
    showLog = showIt

def NetworkRunning():
    return pubsubNetwork and pubsubNetwork.forwarderSubscriberRunning

#StartNetwork()
#while True:
#    a=0
