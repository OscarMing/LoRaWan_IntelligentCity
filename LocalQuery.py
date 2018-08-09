import xlsxwriter
import time
import datetime
import serial

t = time.time()
dt = datetime.datetime.fromtimestamp(t).strftime('%Y-%m-%d %H:%M:%S')
workbook = xlsxwriter.Workbook('/home/pi/Desktop/testData/%s.xlsx'%dt)
worksheet = workbook.add_worksheet()
##ser = serial.Serial('/dev/ttyACM0', 9600,timeout=0.5)
ser = serial.Serial('/dev/ttyUSB0', 9600,timeout=0.5)

row = [0,0,0]
col  = [0,5,9]

##period = 8*60*60
period = 4*60*60

def GetSerialData():
    global ser, row, col
    global worksheet
    global t

    tempList = []
    try:
        SerialData = ser.readline()
        SDS = str(SerialData)
        SD = SerialData.decode('UTF-8','replace').strip('\r\n')

        if len(SerialData)>1:
            print("RowString=>"+SDS)
            print("RealString=>"+SD)

            tempList = SD.split(',')
            ListLens = len(tempList)
            print(tempList)

            if ListLens == 3:
                if(tempList[0][0:2]=='TS'):
                    nowtime = time.time()
                    NT = datetime.datetime.fromtimestamp(nowtime).strftime('%Y-%m-%d %H:%M:%S')
                    worksheet.write(row[0],col[0],NT)
                    worksheet.write(row[0],col[0]+1,tempList[0])
                    worksheet.write(row[0],col[0]+2,tempList[1])
                    worksheet.write(row[0],col[0]+3,tempList[2])
                    row[0]+=1
                elif(tempList[0][0:2]=='HS'):
                    nowtime = time.time()
                    NT = datetime.datetime.fromtimestamp(nowtime).strftime('%Y-%m-%d %H:%M:%S')
                    worksheet.write(row[1],col[1],NT)
                    worksheet.write(row[1],col[1]+1,tempList[0])
                    worksheet.write(row[1],col[1]+2,tempList[1])
                    worksheet.write(row[1],col[1]+3,tempList[2])
                    row[1]+=1

            elif ListLens == 2:
               nowtime = time.time()
               NT = datetime.datetime.fromtimestamp(nowtime).strftime('%Y-%m-%d %H:%M:%S')
               worksheet.write(row[2],col[2],NT)
               worksheet.write(row[2],col[2]+1,tempList[0])
               worksheet.write(row[2],col[2]+2,tempList[1])
               row[2]+=1

    except:
        print("STOP Sampling")


            
try:
    while True:
        GetSerialData()
        tt = time.time()
##        print(t)
##        print(tt)

        if tt>=t+period:
            workbook.close()
            ser.close()
            print("STOP")
            exit()

except KeyboardInterrupt:
    workbook.close()
    ser.close()
    print("Exit")
