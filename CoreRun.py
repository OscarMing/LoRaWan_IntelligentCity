##--------------------Publish MSG--------------------##
##  Publish to Dashboard
##  publishTopic = "/UplinkCommand"
##  Publish via GW to Node
##  publishTopic = "GIOT-GW/DL/0000XXXXOOOOYYYY"
##--------------------SubscribeTopic MSG--------------------##
##  From node to GW Data
##  subscribeTopic = "GIOT-GW/UL/XXXXXXXXXXXX"
##  From DashBoard to Node
##  subscribeTopicM = "/DownlinkCommand"
##--------------------UPTOCHTIOT--------------------##

import copy
import datetime
import json
import paho.mqtt.client as mqtt
import threading
import time
import xlsxwriter

from package.CHTIOT import myCHTIOT
from package.Firebase import myFirebase

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore


##Connect Flag
Connected = False
##Node macAddr
nodeMacAddr = []
##Counter
nodeGetCounter = []
nodeSendCounter = []

##Downlink
DLID = []
##Downlink Flag
DownlinkFlag = []

##DataType
nodeData = []
nodeDataType = []
nodeDataTypeData = []

##Time Buffer
tempUplinkTime=[]
lastUplinkTime=[]

## Excel row and col list
Urow = []
Drow = []

##Put GPS DATA
DNList = []

##Place Info
Place = ["Indoor","Outdoor"]
IndoorMacAddr = ['0000000012000008','0000000012000009','0000000012000003']
OutdoorMacAddr = ['0000000012000006','0000000012000007']

##DataListIN = ["TS","HS","AS","CS","IS","MS","LS","FS","RS","WS"]
##DataListOUT = ["TS","HS","AS","IS","MS","RS","WS","DS","NS"]
DataListIN = ["TS","HS","AS","CS","IS","MS","LS"]
DataListOUT = ["TS","HS","AS","CS","IS","MS","LS","DS","NS"]

##CHT ID INFO
##DATATYPEMAP = {"TS":"12000101","HS":"12000102"}
DATATYPEMAP = {"TS":"12000101","HS":"12000102","CS":"12000103","IS":"12000104",
               "MS":"12000105","LS":"12000106","FS":"12000107","RS":"12000108","WS":"12000109","AS":"12000110"}

CONTROLTYPEMAP = {'A':"12000201","B":"12000202",'C':"12000203",'D':"12000204",'E':"12000205"}

MACADDRMAP = {'0000000012000006':'5585390084',
              '0000000012000007':'5585638068',
              '0000000012000008':'5585253905',
              '0000000012000009':'5548556186'}

DEVKEYMAP = {'0000000012000006':'XXXXXXXXXXXXXXXXXX',
              '0000000012000007':'OOOOOOOOOOOOOOOOOO',
              '0000000012000008':'YYYYYYYYYYYYYYYYYY',
              '0000000012000009':'WWWWWWWWWWWWWWWWW'}

##CHTIOTFLAG = False
CHTIOTFLAG = []

##Store to Firestore. collection Name Setting
DataTypeDictIN = {
    'TS':'Temperature',
    'HS':'Humidity',
    'AS':'Atmosphere',
    'CS':'CO',
    'IS':'CO2',
    'MS':'PM',
    'LS':'LPG',
    'FS':'Fire',
    'RS':'Rain',
    'WS':'Wind'}

DataTypeDictOUT = {
    'TS':'Temperature',
    'HS':'Humidity',
    'AS':'Atmosphere',
    'CS':'CO',
    'IS':'CO2',
    'MS':'PM',
    'LS':'LPG',
    'RS':'Rain',
    'WS':'Wind',
    'DNLIST':'DNS'}

Times = time.time()
FTime = datetime.datetime.fromtimestamp(Times).strftime('%Y-%m-%d %H:%M:%S')
FTime = str(FTime)
workbook = xlsxwriter.Workbook('TestPyExceL{}_{}.xlsx'.format(FTime[0:10],'05'))


##MQTT Client
client = mqtt.Client()
##Firebase Object
db = object

##================================================================================================================================================##

##  Firebase Initial(FirestoreDB)
def FirestoreDB():
    global db
    cred = credentials.Certificate("smartcitytestproject-fb938-firebase-adminsdk-775p2-09cbce8a27.json")
    SmartCityTestApp = firebase_admin.initialize_app(cred,name='SmartCityTest')
    db = firestore.client(app = SmartCityTestApp)
    
##================================================================================================================================================##

##  X for which Place(Indoor/Outdoor)
##  PostData for Upload Data
def FirebasePostToRealtimeDB(X,PostData):
    global reference, myfirebase
    myfirebase.Post2Firebase(reference[X],PostData)

##================================================================================================================================================##

def FirebaseStoreToCloudDB(place,datatype,dataString,addr):
    global db
    global DataTypeDictOUT, DataTypeDictIN
    try:
        if place == 'Indoor':
            collection_ref = db.collection(u'InDoor').document(addr).collection(DataTypeDictIN[datatype])
            collection_ref.add(dataString)
        elif place == 'Outdoor':
            collection_ref = db.collection(u'OutDoor').document(addr).collection(DataTypeDictOUT[datatype])
            collection_ref.add(dataString)
        
    except BaseException as err:
        print("Message",+str(err))
        
##================================================================================================================================================##

def CHTIOTOBJECTSET(DevAddrIndex,DevAddr):
    global DEVKEYMAP
    global MACADDRMAP

    globals()['client%s'%DevAddrIndex] = mqtt.Client()
    globals()['CHT%s'%DevAddrIndex] = myCHTIOT(globals()['client%s'%DevAddrIndex],DEVKEYMAP[DevAddr])
    globals()['CHT%s'%DevAddrIndex].setCLA()
    globals()['CHT%s'%DevAddrIndex].startRun()
    
    tpc1 = "/v1/device/{}/sensor/12000201/rawdata".format(MACADDRMAP[DevAddr])
    tpc2 = "/v1/device/{}/sensor/12000202/rawdata".format(MACADDRMAP[DevAddr])
    globals()['CHT%s'%DevAddrIndex].subscribeTopics(tpc1,tpc2)
    CHTIOTFLAG[DevAddrIndex] = True
    
##================================================================================================================================================##

def CHTIOTGETMSG():
    global nodeMacAddr
    global CHTIOTFLAG
    global DownlinkFlag
    global MACADDRMAP

    CHTIOTID = ''
    CHTIOTDEVID = ''
    CHTIOTDEVADDR = ''
    CHTIOTDEVINDEX = ''
    CHTIOTVALUE = ''
    CHTIOTMSGDIC = {}
    DownlinkCommandMap = {'12000201':'A','12000202':'B','12000203':'C'}
   
    if len(nodeMacAddr) != 0:
        for i in range(len(nodeMacAddr)):
            if CHTIOTFLAG[i] == True:
                CHTIOTMSG = globals()['CHT%s'%str(i)].Get_Message()
                CHTIOTMSGDIC = CHTIOTMSG
                if CHTIOTMSG != False:
                    print(CHTIOTMSG)
                    CHTIOTID = CHTIOTMSGDIC['id']
                    CHTIOTDEVID = CHTIOTMSGDIC['deviceId']
                    CHTIOTVALUE = CHTIOTMSGDIC['value'][0]
                    CHTIOTDEVADDR = list(MACADDRMAP.keys())[list(MACADDRMAP.values()).index(CHTIOTDEVID)]
                    CHTIOTDEVINDEX = nodeMacAddr.index(CHTIOTDEVADDR)
                    print([CHTIOTID,CHTIOTDEVID,CHTIOTVALUE])
                    try:
                        DownlinkFlag[CHTIOTDEVINDEX][1] = True
                        SendDownLink(CHTIOTDEVINDEX,'Manual',DownlinkCommandMap[CHTIOTID],CHTIOTVALUE)
##                        DownlinkFlag[DLIndexofNode][1] = True
##                        SendDownLink(DLIndexofNode,'Manual',dataType,dataStatus)
                    except:
                        pass
                    
            else:
                pass
    else:
        pass

##================================================================================================================================================##

def UpTOCHTIOT(DTP,nodeDTPKG):
    ##nodeDTPKG ={"macAddr":macAddr,"time":time,"rssi":rssi,data[0:2]: data[3:]}  
    global nodeMacAddr
    global MACADDRMAP, DATATYPEMAP
   
    DTPKGTIME = ''
    DTPKGIDS = ''
    DTPKGDATA = ''
    CHTINDEX = ''
    DataPostPackage = ''
    
    DTPKGTIME = nodeDTPKG["time"]
    DTPKGTIME = DTPKGTIME.replace(' ','T')
    DTPKGDATA = nodeDTPKG[DTP]
    DTPKGIDS = DATATYPEMAP[DTP]
    CHTINDEX = nodeMacAddr.index(nodeDTPKG["macAddr"])
    
    publishTopic = "/v1/device/{}/rawdata".format(MACADDRMAP[nodeDTPKG["macAddr"]])

    DataPostPackage =[{
        "id":DTPKGIDS,
        "time":DTPKGTIME,
        "value": [str(DTPKGDATA)]
        }]
    DataPostString = json.dumps(DataPostPackage)
    globals()['CHT%s'%CHTINDEX].publishDataString(publishTopic,DataPostString)
##    CHT.publishDataString(publishTopic,DataPostString)
    print(DataPostPackage)
    
##================================================================================================================================================##      

def DownFromCHTIOT(CHTDDATA,CHTDLIndexofNode):
    CHTDLDataString = '';

    try:
        CHTDLDataString = json.loads(CHTDDATA)  
    except:
        print("Non Data CHT")
        return
    print(CHTDLDataString['id'])
    print(CHTDLDataString['value'])
    print(CHTDLDataString['value'][0])
    
##================================================================================================================================================##

##  MQTT Connect Callback Function
def on_connect(client, userdata, flags, rc):
    if rc==0:
        print("Connection OK")
        global Connected                #Use global variable
        Connected = True                #Signal connection 
    else:
        print("Not Connect")     
    print("Connected with result code "+str(rc))   
    
##================================================================================================================================================##

##  MQTT Subscript Callback Function
def on_message(client, userdata, msg):
    Msg= str(msg.payload.decode("utf-8"))
    CheckmacAddr(Msg)
    
##================================================================================================================================================##

def CheckmacAddr(MSG):
    ##Initial Every List
    global nodeMacAddr
    global nodeGetCounter, nodeData, nodeDataType, nodeDataTypeData, nodeSendCounter
    global lastUplinkTime, tempUplinkTime
    global DLID, DownlinkFlag
    global Urow, Drow
    global DNList
    global CHTIOTFLAG
    
    SubscribesDataString = ''
    MacAddr = ''
    ##Check Subscribes String Length    
    SubscribesDataStringLens = len(MSG)
    ##Index of MacAddr in the nodeMacAddr List
    IndexofMacAddr = 0
    ##Downlink Data Type
    ##{"macAddr": "0000000012000008", "dataStatus": 0, "dataType": "A"}

    try:
        ##Transfer Uplink Data to JSON Font String
        SubscribesDataString = json.loads(MSG)
        ##Get MacAddr for DataString
        if SubscribesDataStringLens > 100:
            MacAddr = SubscribesDataString[0]["macAddr"]
        else:
            MacAddr = SubscribesDataString["macAddr"]
        
    except:
        print("No Data! CheckmacAddr ")
        return


    if (MacAddr not in nodeMacAddr):
        ##Create Sheet for each node
        CreateSheet(MacAddr)
        ##Append Node Info into nodeMacAddr List
        nodeMacAddr.append(MacAddr)
        IndexofMacAddr = nodeMacAddr.index(MacAddr)		    ##Get node index from nodeMacAddr List
        nodeGetCounter.append([])                                   ##Add CounterList into List
        nodeData.append([])
        nodeDataType.append([])				            ##Add DataTypeList into List
        nodeDataTypeData.append([])				    ##Add DataTypeDataList into List
        nodeSendCounter.append([0,0])                               ##Add Send Counter[Auto,Manual]

        lastUplinkTime.append([])                          	    ##Add last Uplinktime
        tempUplinkTime.append(0)                            	    ##Add temp Uplinktime
        
        DLID.append(9988776655332200)                               ##Add DLID
        DownlinkFlag.append([False,False])		            ##Add Downlink Flag[Auto,Manual]
##        Urow.append(0)
        Urow.append([])
        Drow.append([0,0])
        DNList.append([0,0])                                        ##Add GPS DATA

        CHTIOTFLAG.append(False)                                    ##For CHTIOT Subscribe Flag

        ##Set CHTIOT MQTT Objcet        
        CHTIOTOBJECTSET(IndexofMacAddr,MacAddr)      
    	
    else:
        IndexofMacAddr = nodeMacAddr.index(MacAddr)


    if SubscribesDataStringLens>100:
        GetUplink(MSG,IndexofMacAddr)
        print("MSG Length:"+str(len(MSG)))
	    
    else:
        GetDownlink(MSG,IndexofMacAddr)
        print("MSG Length:"+str(len(MSG)))

##================================================================================================================================================##
##  Get Downlink Message From DashBoard
##  DDATA => For getting subscribe message
##  DLIndexofNode => For the index of macaddr in the nodeMacAddr list
def GetDownlink(DDATA,DLIndexofNode):
    ##Manual Downlink
    global nodeMacAddr,DownlinkFlag
    DownlinkDataString = ''
    macAddr = ''
    dataType = ''
    dataStatus = ''
    try:
        DownlinkDataString = json.loads(DDATA)  
    except:
        print("Non Data DownDATA01")
        return
    try:
        macAddr = DownlinkDataString["macAddr"]
        dataType = DownlinkDataString["dataType"]
        dataStatus = DownlinkDataString["dataStatus"]
    except:
        print("Non Data DownDATA02")
        return
    try:
        DownlinkFlag[DLIndexofNode][1] = True
        ##Put Downlink Message to Node
        SendDownLink(DLIndexofNode,'Manual',dataType,dataStatus)
    except:
        pass

##================================================================================================================================================##
##  Get Uplink Message From GIOT Gateway
def GetUplink(UDATA,ULIndexofNode):
    ##Initial Variable
    UplinkDataString = ''
    time = ''
    macAddr = ''
    rssi = ''
    data = ''
    RowData = ''

    try:
        UplinkDataString = json.loads(UDATA)
    except:
        print("Non UPData")
        return
    try:
        time = UplinkDataString[0]["time"]
        rssi = UplinkDataString[0]["rssi"]
        macAddr = UplinkDataString[0]["macAddr"]
        data = UplinkDataString[0]["data"]
        RowData = LoRaDataDecode(data)
    except:
        pass
    ##UTC+8  
    time = time.replace('T',' ')
    time = datetime.datetime.strptime(time,'%Y-%m-%d %H:%M:%S')+datetime.timedelta(hours = 8)
    time = time.strftime('%Y-%m-%d %H:%M:%S')

    ##Uplink Data List
    ULDLS = [macAddr,time,rssi,RowData]
    print(ULDLS)

    if(RowData[0:2] in DataListOUT):
        ##Package To JSON and Publish to nodeRED

##        PackageULData(ULDLS)

        ##Thread for Publish
    ##    threadPublish = threading.Thread(target = PackageULData,args=(ULDLS,) , daemon = True)
    ##    threadPublish.start()
        
        ##Check node and save to Excel sheet
        ##Check node Data Count and DownlinkFlag
        CheckNodeData(ULDLS)
    else:
        pass

##================================================================================================================================================##
def CheckNodeData(DataListCK):
##  ULDLS = [macAddr,time,rssi,RowData]
    global nodeMacAddr, nodeGetCounter, nodeSendCounter, nodeData, nodeDataType, nodeDataTypeData
    global tempUplinkTime, lastUplinkTime
    global DownlinkFlag,DLID
    global Urow,Drow

    nodeIndex = ""
    dataIndex = ""
    NowTimes = time.time()
    NowTimeString = datetime.datetime.fromtimestamp(NowTimes).strftime('%Y-%m-%d %H:%M:%S')
    nodeIndex = nodeMacAddr.index(DataListCK[0])
    RealData = ""

    ##EX:DataListCK[3]=="TS:25.55",DataListCK[3][0:2] == "TS"
    ##Check if DataType in the DataTypeList

    
    if(DataListCK[3][0:2] not in nodeDataType[nodeIndex]):
        if(DataListCK[3][3:]!=""):
            RealData = DataListCK[3][3:]
        else:
            RealData = "0"
            DataListCK[3] = str(DataListCK[3][0:2])+str(RealData)
            
        nodeData[nodeIndex].append(DataListCK[3])
        nodeDataType[nodeIndex].append(DataListCK[3][0:2])			        ##Put DataType
##      nodeDataTypeData[nodeIndex].append(DataListCK[3][3:])		        ##Put RealData
        nodeDataTypeData[nodeIndex].append(RealData)		                ##Put RealData
        nodeGetCounter[nodeIndex].append(1)					        ##Put Data Count(First Time)
        lastUplinkTime[nodeIndex].append(DataListCK[1])				##Add Uplink Time
        Urow[nodeIndex].append(1)
##      Urow[nodeIndex]+=1
        

        dataIndex = nodeDataType[nodeIndex].index(DataListCK[3][0:2])           ##Data index in List
##      UplinkToExcel(nodeIndex,dataIndex,DataListCK)				##Log Data in Excel
        threadEXUP01 = threading.Thread(target = UplinkToExcel,args=(nodeIndex,dataIndex,DataListCK,) , daemon = True)
        threadEXUP01.start()
        

        if(DataListCK[3][0:2]=='TS'):
            tempUplinkTime[nodeIndex] = NowTimes
            #PushDownlink(nodeIndex)
            DownlinkFlag[nodeIndex][0] = True
            SendFlag(nodeIndex,'Auto')
        
        PackageULData(DataListCK)
        ##DataType exist in the DataTypeList
        
    else:
        dataIndex = nodeDataType[nodeIndex].index(DataListCK[3][0:2])
        if(lastUplinkTime[nodeIndex][dataIndex] != DataListCK[1]):
            if(DataListCK[3][3:]!=""):
                RealData = DataListCK[3][3:]
            else:
                RealData = nodeDataTypeData[nodeIndex][dataIndex]
                DataListCK[3] = str(DataListCK[3][0:2])+str(RealData)
                print("DataListCK[3]:"+DataListCK[3])
                
            print(lastUplinkTime[nodeIndex][dataIndex])
            print(DataListCK[1])
            nodeGetCounter[nodeIndex][dataIndex]+=1                 		##Add Count
            nodeData[nodeIndex][dataIndex] = DataListCK[3]
##          nodeDataTypeData[nodeIndex][dataIndex] = DataListCK[3][3:]		##Update Data to DataList
            nodeDataTypeData[nodeIndex][dataIndex] = RealData                       ##Update Data to DataList
            lastUplinkTime[nodeIndex][dataIndex] = copy.copy(DataListCK[1])         ##Update uplinl Time
            Urow[nodeIndex][dataIndex]+=1
##          Urow[nodeIndex]+=1
##          UplinkToExcel(nodeIndex,dataIndex,DataListCK)
            threadEXUP02 = threading.Thread(target = UplinkToExcel,args=(nodeIndex,dataIndex,DataListCK,) , daemon = True)
            threadEXUP02.start()
            print(nodeDataTypeData[nodeIndex])
            print(nodeData[nodeIndex])

            if(DataListCK[3][0:2]=='TS'):
                PushDownlink(nodeIndex,DataListCK)
                ##Update to DB
                ##XXX
            PackageULData(DataListCK)
            
        else:
            nodeGetCounter[nodeIndex][dataIndex]+=0

##================================================================================================================================================##

##  Post to NodeRED, Firebase RealtimeDB, FirestoreDB
##  Formate Data Structure 
def PackageULData(DataListPKG):
    global Place
    global DNList
    global nodeMacAddr
    
    nodeDataPackage = ''
    nodeDataPostPackage = ''
    macAddr = ''
    time = ''
    rssi = ''
    data = ''
    idxofaddr = 0
##    DNList = ['','']
    macAddr = DataListPKG[0]
    time = DataListPKG[1]
    rssi = DataListPKG[2]
    data = DataListPKG[3]
    idxofaddr = nodeMacAddr.index(macAddr)

    ##Indoor Case
    if macAddr in IndoorMacAddr:
        nodeDataPackage = {
            "macAddr":macAddr,
            "time":time,
            "rssi":rssi,
            data[0:2]: data[3:]
            }
        nodeDataPostPackage ={
            Place[0]:nodeDataPackage
            }
        nodeDataPostPackageString = json.dumps(nodeDataPostPackage)

        if(data[0:2] == 'DS'or data[0:2] == 'NS'):
            pass
        else:
            ##Post to NodeRED
            PublishULData(nodeDataPostPackageString)
            ##Post to Firebase RealtimeDB
            ##FirebasePostToRealtimeDB(0,nodeDataPostPackageString)
            FirebaseStoreToCloudDB(Place[0],data[0:2],nodeDataPackage,macAddr)
            
            UpTOCHTIOT(data[0:2],nodeDataPackage)
        
    ##Outdoor Case
    elif  macAddr in OutdoorMacAddr:
#        DNList = ['','']
        if(data[0:2] == 'DS'):
            DNList[idxofaddr][0] = data[3:] 
        elif(data[0:2] == 'NS'):
            DNList[idxofaddr][1] = data[3:]

            nodeDataPackage = {
                "macAddr":macAddr,
                "time":time,
                "rssi":rssi,
                "DNLIST": DNList[idxofaddr]
                }
            nodeDataPostPackage ={
                Place[1]:nodeDataPackage
                }
            
            nodeDataPostPackageString = json.dumps(nodeDataPostPackage)

            ##Post to NodeRED
            PublishULData(nodeDataPostPackageString)
            ##Post to Firebase RealtimeDB
##            FirebasePostToRealtimeDB(1,nodeDataPostPackageString)
            FirebaseStoreToCloudDB(Place[1],"DNLIST",nodeDataPackage,macAddr)

        else:
            nodeDataPackage = {
                "macAddr":macAddr,
                "time":time,
                "rssi":rssi,
                data[0:2]: data[3:]
                }
            nodeDataPostPackage ={
                Place[1]:nodeDataPackage
                }

            nodeDataPostPackageString = json.dumps(nodeDataPostPackage)

            ##Post to NodeRED
            PublishULData(nodeDataPostPackageString)
            ##Post to Firebase RealtimeDB
##            FirebasePostToRealtimeDB(1,nodeDataPostPackageString)
            FirebaseStoreToCloudDB(Place[1],data[0:2],nodeDataPackage,macAddr)
            UpTOCHTIOT(data[0:2],nodeDataPackage)

##================================================================================================================================================##

##  Publish To NodeRED
def PublishULData(DataListPSH):

    global client
    ##Uplink Data Update to Dashboard
    publishTopic = "/UplinkCommand"
    client.publish(publishTopic,DataListPSH)

##================================================================================================================================================##

def PushDownlink(macAddrIndex,DataListPD):
    global tempUplinkTime,DownlinkFlag
    DownlinkPeriod = 180
    nt = time.time()
    if(nt>=(tempUplinkTime[macAddrIndex]+DownlinkPeriod)):
        print(nt)
        print(tempUplinkTime[macAddrIndex])
        tempUplinkTime[macAddrIndex] = nt
        DownlinkFlag[macAddrIndex][0] = True
        SendFlag(macAddrIndex,'Auto')

    else:
        print(nt)
        print(tempUplinkTime[macAddrIndex])
        DownlinkFlag[macAddrIndex][0] = False

##================================================================================================================================================##

def SendFlag(i,Mode):
    threadSend = threading.Thread(target = SendDownLink,args=(i,Mode,) , daemon = True)
    threadSend.start()
    
##================================================================================================================================================##

##  Each node Create its Own Sheet
def CreateSheet(nodemacAddr):
    global workbook
    ##Font
    bold = workbook.add_format({'bold':True})
    globals()["%s"%nodemacAddr]=workbook.add_worksheet(nodemacAddr)
##    globals()["%s"%nodemacAddr].title = nodemacAddr
##    DataListTopic = [['A1','nodeMacAddr'],['B1','UpTime'],['C1','RSSI'],['D1','Data'],
##                     ['E1','nodeGetCounter'],['F1','DLDATA'],['G1','DLTIME'],['H1','DLCounter'],
##                     ['I1','DLDATA'],['J1','DLTIME'],['K1','DLCounter']]
    DataListTopic = [['A1','TS'],['B1','UpTime'],['C1','nodeGetCounter'],
                     ['D1','HS'],['E1','UpTime'],['F1','nodeGetCounter'],
                     ['G1','AS'],['H1','UpTime'],['I1','nodeGetCounter'],
                     ['J1','CS'],['K1','UpTime'],['L1','nodeGetCounter'],
                     ['M1','IS'],['N1','UpTime'],['O1','nodeGetCounter'],
                     ['P1','MS'],['Q1','UpTime'],['R1','nodeGetCounter'],
                     ['S1','LS'],['T1','UpTime'],['U1','nodeGetCounter'],
                     ['V1','DS'],['W1','UpTime'],['X1','nodeGetCounter'],
                     ['Y1','NS'],['Z1','UpTime'],['AA1','nodeGetCounter'],
                     ['AB1','DLDATA'],['AC1','DLTIME'],['AD1','DLCounter'],
                     ['AF1','DLDATA'],['AG1','DLTIME'],['AH1','DLCounter']]


    for a,b in DataListTopic:
        globals()["%s"%nodemacAddr].write(a,b,bold)

##================================================================================================================================================##

def UplinkToExcel(nindex,dindex,DataListUEX):
    ##nindex=>node index
    ##dindex=>data index
    global Urow
    global nodeGetCounter
    global CounterToEX
    global DataListOUT

    DataTypeIndex = DataListOUT.index(DataListUEX[3][0:2])

##    Ucol = 0
    Ucol = [0,3,6,9,12,15,18,21,24]
    globals()["%s"%DataListUEX[0]].write(Urow[nindex][dindex],Ucol[DataTypeIndex],DataListUEX[3])
    globals()["%s"%DataListUEX[0]].write(Urow[nindex][dindex],Ucol[DataTypeIndex]+1,DataListUEX[1])
    globals()["%s"%DataListUEX[0]].write(Urow[nindex][dindex],Ucol[DataTypeIndex]+2,nodeGetCounter[nindex][dindex])
    
##    globals()["%s"%DataListUEX[0]].write(Urow[nindex],Ucol,DataListUEX[0])
##    globals()["%s"%DataListUEX[0]].write(Urow[nindex],Ucol+1,DataListUEX[1])
##    globals()["%s"%DataListUEX[0]].write(Urow[nindex],Ucol+2,DataListUEX[2])
##    globals()["%s"%DataListUEX[0]].write(Urow[nindex],Ucol+3,DataListUEX[3])
##    globals()["%s"%DataListUEX[0]].write(Urow[nindex],Ucol+4,nodeGetCounter[nindex][dindex])

##================================================================================================================================================##

def DownlinkToExcel(Data,Times,DataCount,addr,index,flag):
    #DownlinkToExcel(EecodeData,dt,nodeSendCounter[DLINDEX][1],nodeMacAddr[DLINDEX],DLINDEX,DLFLAGS)
    global Drow
##    print("Drow")
##    print(Drow)
    if (flag == 'Auto'):
        Ucol = 27
        globals()["%s"%addr].write(Drow[index][0],Ucol,Data)
        globals()["%s"%addr].write(Drow[index][0],Ucol+1,Times)
        globals()["%s"%addr].write(Drow[index][0],Ucol+2,DataCount)
    	
    elif (flag == 'Manual'):
        Ucol = 30
        globals()["%s"%addr].write(Drow[index][1],Ucol,Data)
        globals()["%s"%addr].write(Drow[index][1],Ucol+1,Times)
        globals()["%s"%addr].write(Drow[index][1],Ucol+2,DataCount)

##================================================================================================================================================## 

##  Decode Data 
def LoRaDataDecode(decodeData):
    tempList = []
    DecodeDataString = ''
    for j in range(0,len(decodeData),2):
        tp01 = ord(decodeData[j:j+1])
        tp02 = ord(decodeData[j+1:j+2])
        tempList = [tp01,tp02]
        #print(tp01,tp02)
        for k in range(0,len(tempList)):
            if(tempList[k]>96):
                tempList[k] = (tempList[k]-96)+9
                #print( tempList[k])
            elif(tempList[k]>47 and tempList[k]<58):
                tempList[k] = tempList[k]-48
                #print( tempList[k])
            else:
                tempList[k]=tempList[k]
                #print( tempList[k])

        tempChar = tempList[0]*16+tempList[1]
        #print(tempChar)
        #print(chr(tempChar))
        DecodeDataString+=chr(tempChar)

    return DecodeDataString

##================================================================================================================================================##

##  Encode Data 
def LoRaDataEncode(encodeDataType,encodeData):
    dataTempString = ''
    EecodeDataString = ''
    dataTempString = encodeDataType + ':' + str(encodeData)
##    print(len(dataTempString))

    for i in range(0,len(dataTempString)):
        s1 = hex(ord(dataTempString[i:i+1]))
##        print(s1)
        EecodeDataString += s1[2:]

##    print(pkgDataString)
    return EecodeDataString

##================================================================================================================================================##

##  Downlink Data Package
def DLDataStringPkg(macAddr,data,dID):
    DLData = [{
        "macAddr":macAddr,
        "data":data,
        "gwid":"XXXXOOOOYYYY0000",
        "id":dID,
        "extra":{
            "port":1,
            "txpara":"6"
            }
        }]
##    print(type(DLDS))
    DLDataString = json.dumps(DLData)
    return DLDataString

##================================================================================================================================================##

##Sending Downlink Data
def SendDownLink(DLINDEX,DLFLAGS,DLDataType = "A",DLDataStatus = 0):
    #DLINDEX=>macAddr index
    global DLID, nodeSendCounter,DownlinkFlag
    global nodeMacAddr,client,Drow
    publishTopic = "GIOT-GW/DL/XXXXOOOOYYYY0000"
    time.sleep(0.5)
    if (DLFLAGS == 'Auto'):
        if DownlinkFlag[DLINDEX][0]:
    	    nodeSendCounter[DLINDEX][0]+=1						##Add Send Count for Auto
    	    DLID[DLINDEX]+=1
    	    Drow[DLINDEX][0]+=1

        if ((nodeSendCounter[DLINDEX][0])%2==0):
            DLDataStatus = 0
        else:
            DLDataStatus = 1
##    	if(nodeSendCounter[DLINDEX][0])%2!=0:
##            DLDataStatus = 1
##        else:
##            DLDataStatus = 0
              

    elif (DLFLAGS == 'Manual'):
        if DownlinkFlag[DLINDEX][1]:
            nodeSendCounter[DLINDEX][1]+=1						##Add Send Count for Manual
            DLID[DLINDEX]+=1
            Drow[DLINDEX][1]+=1
    else:
        pass

    EecodeData = LoRaDataEncode(DLDataType,DLDataStatus)
    sendString = DLDataStringPkg(nodeMacAddr[DLINDEX],EecodeData,str(DLID[DLINDEX]))
    client.publish(publishTopic,sendString)

    print("SendCount %s %s:" %(nodeMacAddr[DLINDEX],DLFLAGS) + str(nodeSendCounter[DLINDEX]))
    ##-------------------------------------------------------------------------------------##    
    t = time.time()
    dt = datetime.datetime.fromtimestamp(t).strftime('%Y-%m-%d %H:%M:%S')
    if (DLFLAGS == 'Auto'):
        threadEXSD01 = threading.Thread(target = DownlinkToExcel,args=(EecodeData,dt,nodeSendCounter[DLINDEX][0],nodeMacAddr[DLINDEX],DLINDEX,DLFLAGS,) , daemon = True)
        threadEXSD01.start()
##    	DownlinkToExcel(EecodeData,dt,nodeSendCounter[DLINDEX][0],nodeMacAddr[DLINDEX],DLINDEX,DLFLAGS)
        DownlinkFlag[DLINDEX][0] = False
    elif (DLFLAGS == 'Manual'):
##    	DownlinkToExcel(EecodeData,dt,nodeSendCounter[DLINDEX][1],nodeMacAddr[DLINDEX],DLINDEX,DLFLAGS)
        threadEXSD02 = threading.Thread(target = DownlinkToExcel,args=(EecodeData,dt,nodeSendCounter[DLINDEX][1],nodeMacAddr[DLINDEX],DLINDEX,DLFLAGS,) , daemon = True)
        threadEXSD02.start()
        DownlinkFlag[DLINDEX][1] = False

##================================================================================================================================================##
            
def MainWork():
    global client
    ##Basic info
    ##Broker ="iot.eclipse.org"
    Broker = "BK IP"
    port = "BK PORT"
    user = "UserName"
    password = "UserPWD"
    ##From node to GW Data
    subscribeTopic = "GIOT-GW/UL/XXXXXXXXXXXX"
    ##From DashBoard to Node
    subscribeTopicM = "/DownlinkCommand"
    
	
    ##Authentication from LoRa Gateway
    client.username_pw_set(user, password=password)
    print("Connecting to  broker..."+Broker)
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(Broker,port,60)
    client.subscribe(subscribeTopic)
    client.subscribe(subscribeTopicM)
    client.loop_start()

	
##================================================================================================================================================##
if __name__ == '__main__':
    MainWork()
##    FirebaseRealtimeDB()
    FirestoreDB()


while Connected != True:
    time.sleep(1)

try:
    while True:
        if(Connected):
##            time.sleep(0.001)
            CHTIOTGETMSG()

except KeyboardInterrupt:
    workbook.close()
    client.disconnect()
    client.loop_stop()

