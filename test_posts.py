from BConnectNetwork import StartNetwork, Publish, AddListener 
import time

StartNetwork(subPort="5559",pubPort="5560",initialFilter=b"",startThreads=True)

def Incoming(topic,subtype,data):
    print("Listener(%s): %s" % (topic,data) )

print("waiting..")
time.sleep(1)
AddListener("forty",Incoming)
AddListener("blender",Incoming)
time.sleep(1)

while True:
    Publish("blender","kick","text",b"f95")
    time.sleep(5)  
