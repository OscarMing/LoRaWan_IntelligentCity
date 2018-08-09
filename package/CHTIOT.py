import json
import paho.mqtt.client as mqtt
import time
import datetime
import ast

class myCHTIOT():
    def __init__(self, client,PWD):
        self.Broker = "BK IP"
        self.user = "UserName"
        self.password= PWD
        self.client = client
        self.return_dict = {}
        self.flag = False

        
    def on_connect(self,client, userdata, flags, rc):
        if rc==0:
            print("Connection OK")
        else:
            print("Not Connect")     
        print("Connected with result code "+str(rc))


    def on_message(self,client, userdata, msg):
        self.return_dict = msg.payload.decode("utf-8")  # class bytes to string
        self.return_dict = ast.literal_eval(self.return_dict)
        self.flag = True


    def Get_Message(self):
        if self.flag == True:
            self.flag = False
            return self.return_dict
        else:
            return False


    def setCLA(self):
        self.client.username_pw_set(self.user, password=self.password)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect(self.Broker, 1883, 60)
        
        
    def subscribeTopics(self,*topics):
        for topic in topics:
            self.client.subscribe(topic)


    def publishDataString(self,publishTopic,DataString):
        self.client.publish(publishTopic,DataString)


    def startRun(self):
        self.client.loop_start()


    def stopLoop(self):
        self.client.disconnect()
        self.client.loop_stop()
