import requests
import json
import time
import datetime
import paho.mqtt.client as mqtt

DataListIN = ["TS","HS","AS","CS","IS","MS","LS"]
DataListOUT = ["TS","HS","AS","CS","IS","MS","LS","DS","NS"]

CountIN = [0,0,0,0,0,0,0]
CountOUT = [0,0,0,0,0,0,0]

CountIN2 = [0,0,0,0,0,0,0]
CountOUT2 = [0,0,0,0,0,0,0]

DataLimitDict = {
    'TS':35.00,
    'HS':95.50,
    'AS':1000000.0,
    'CS':10.00,
    'IS':600.00,
    'MS':50.00,
    'LS':200.00}

DataLimitDict2 = {
    'TS':40.00,
    'HS':98.50,
    'AS':1200000.0,
    'CS':20.00,
    'IS':800.00,
    'MS':120.00,
    'LS':500.00}

DataTypeDict = {
    'TS':'Temperature',
    'HS':'Humidity',
    'AS':'Atmosphere',
    'CS':'CO',
    'IS':'CO2',
    'MS':'PM',
    'LS':'LPG'}

client = mqtt.Client()


def on_connect(client, userdata, flags, rc):
    if rc==0:
        print("Connection OK")
        global Connected                #Use global variable
        Connected = True                #Signal connection 
    else:
        print("Not Connect")     
    print("Connected with result code "+str(rc))


def on_message(client, userdata, msg):
    Msg= str(msg.payload.decode("utf-8"))
    GetDataInfo(Msg)
    print(Msg)

def GetDataInfo(MSG):
    Place = ''
    DevAddr = ''
    DataType = ''
    Data = ''

    try:
        DataInfoString = json.loads(MSG)  
    except:
        print("NO GET DATA")
        return
    
    if list(DataInfoString.keys())[0] == 'Indoor':
        Place = 'Indoor'
        DevAddr = DataInfoString['Indoor']["macAddr"]
        DataType = list(DataInfoString['Indoor'].keys())[3]
        Data = DataInfoString['Indoor'][DataType]
        
    elif list(DataInfoString.keys())[0] == 'Outdoor':
        Place = 'Outdoor'
        DevAddr = DataInfoString['Outdoor']["macAddr"]
        DataType = list(DataInfoString['Outdoor'].keys())[3]
        Data = DataInfoString['Outdoor'][DataType]
    else:
        pass

    DataInfo = [Place,DevAddr,DataType,Data]
    DataThreshold(DataInfo)
    
def DataThreshold(DataList):
    global DataLimitDict, DataLimitDict2, DataTypeDict
    global DataListIN, DataListOUT
    global CountIN, CountOUT, CountIN2, CountOUT2
    print("C:")
    print(CountIN)
    print(CountOUT)
    print("C2:")
    print(CountIN2)
    print(CountOUT2)
    print(DataList[3])

    if (DataList[2] in DataListIN) or (DataList[2] in DataListOUT):
        if (DataList[3]!=""):
            if float(DataList[3])>= DataLimitDict2[DataList[2]]:
                
                if DataList[0] == 'Indoor':
                    idxi = DataListIN.index(DataList[2])
                    if CountIN2[idxi] >= 2:
                        NotifyList = DataList
                        IFTTTNotify(NotifyList,"EMERGENCY")
                        CountIN2[idxi] = 0
                    else:
                        CountIN2[idxi]+=1

                elif DataList[0] == 'Outdoor':
                    idxo = DataListOUT.index(DataList[2])
                    if CountOUT2[idxo] >= 2:
                        NotifyList = DataList
                        IFTTTNotify(NotifyList,"EMERGENCY")
                        CountOUT2[idxo] = 0
                        print(CountOUT2)
                    else:
                        CountOUT2[idxo]+=1
                        print(CountOUT2)
                else:
                    pass
                    
            
            elif float(DataList[3])>= DataLimitDict[DataList[2]]:
        ##        NotifyList = DataList
        ##        IFTTTNotify(NotifyList)
                if DataList[0] == 'Indoor':
                    idxi = DataListIN.index(DataList[2])
                    if CountIN[idxi] >= 2:
                        NotifyList = DataList
                        IFTTTNotify(NotifyList,"ALERT")
                        CountIN[idxi] = 0
                    else:
                        CountIN[idxi]+=1

                elif DataList[0] == 'Outdoor':
                    idxo = DataListOUT.index(DataList[2])
                    if CountOUT[idxo] >= 2:
                        NotifyList = DataList
                        IFTTTNotify(NotifyList,"ALERT")
                        CountOUT[idxo] = 0
                        print(CountOUT)
                    else:
                        CountOUT[idxo]+=1
                        print(CountOUT)
                else:
                    pass

            else:
                print("No Alert")
                pass
        else:
            pass
    else:
        pass
    
def IFTTTNotify(NotifyInfo,LEVEL):
    global DataTypeDict
    print("Notify")
    URL = 'ifttt trigger url'
    value1 = NotifyInfo[0]+'==>DeviceID:'+NotifyInfo[1]
    value2 = DataTypeDict[NotifyInfo[2]]+':'+NotifyInfo[3]
##    value3 = 'Alert'
    value3 = LEVEL
    payload = {'value1': value1, 'value2': value2, 'value3': value3}
    r = requests.post(URL, data=payload)
    print(r.text)

def MainWork():
    global client
    ##Basic info
    Broker = "BK IP"
    port = "BK PORT"
    user = "UserName"
    password = "UserPWD"
    ##From DashBoard to Node
    subscribeTopicM = "/UplinkCommand"
    
    ##Authentication from LoRa Gateway
    client.username_pw_set(user, password=password)
    print("Connecting to  broker..."+Broker)
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(Broker,port,60)
    client.subscribe(subscribeTopicM)
    client.loop_start()


if __name__ == '__main__':
    MainWork()
