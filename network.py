import zmq,threading,time

pubsubNetwork = None

def StartNetwork():
    pubsubNetwork = PubSubNetwork()

class PubSubNetwork:
    forwarderSubPort = "5559"
    forwarderPubPort = "5560"

    forwarderRunning = False
    forwarderThread = None

    forwarderSubscriberRunning = False
    forwarderSubscriberThread = None

    def __init__(self,subPort="5559",pubPort="5560"):
        self.forwarderPubPort = pubPort
        self.forwarderSubPort = subPort

        self.initPublisherSocket()
        self.start_threads()
        
        time.sleep(2)
        self.publish("runtime","{a=b}")

    def initPublisherSocket(self):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PUB)
        print("b: %s" % self.forwarderSubPort)
        self.socket.connect("tcp://localhost:%s" % self.forwarderSubPort)

    # send data to the forwarder with a given topic
    def publish(self,topic,messagedata):
        self.socket.send_string( "%s %s" % (topic, messagedata))

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
            socket = context.socket(zmq.SUB)
            print ("Collecting updates from server...")
            socket.connect ("tcp://localhost:%s" % self.forwarderPubPort)
            topicfilter = b"blender"
            socket.setsockopt(zmq.SUBSCRIBE, topicfilter)
            for update_nbr in range(10):
                string = socket.recv()
                topic, messagedata = string.split()
                print (topic, messagedata)


        self.forwarderThread = threading.Thread(target=thread_forwarder)
        self.forwarderThread.start()
        self.forwarderRunning = True

        self.forwarderSubscriberThread = threading.Thread(target=thread_forwarder_subscriber)
        self.forwarderSubscriberThread.start()
        self.forwarderSubscriberRunning=True


