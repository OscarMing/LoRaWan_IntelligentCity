/*=====================================================//
#2018/03/30
#NCYU BME BCELAB LoRaWAN Project
#Gateway uesd GIOT Indoor Gateway
#LoRa Node used Acsip s76 module
#Support Class A & C Mode
#Design by Hugo Lin and ref from Acsip sourse
#Add Log Data to Excel 
#Version 1.1.9
//=====================================================*/
#include <Timer.h>
#include <SoftwareSerial.h>
#include <Streaming.h>
#include "DHT.h"

#define DHTPIN 2   
//#define DHTTYPE DHT22
#define DHTTYPE DHT11   

//SoftwareSerial mySerial(10, 11); // RX, TX
DHT dht(DHTPIN, DHTTYPE);

Timer sendUplinkCmd_Clock;

uint16_t DLCount = 0;
uint16_t ULCount[] = {0,0} ;

float dataArray[2];
uint8_t txAckArray[64];
boolean classModeLock = false;
boolean joinNetLock = false;
boolean startLock = false;
char* DataType[] = {"HS:","TS:"};

void setup() {
  Serial.begin(9600);
  Serial2.begin(115200);
  dht.begin();
  StartCommand();
  //After initialize the LoRa Module, then start send and get msg work
  if(startLock){
//    Serial.print("Start!!");//
    sendUplinkCmd_Clock.every(30000,sendUplinkCmd);
//    excelSetUp();//
    }
}

//=====================================================================================================//

void excelSetUp(){
  Serial.println("CLEARSHEET");
  Serial.println("LABEL, Date, Time, Data, CountType, Count");
  }

//Initialize the LoRa Module, get class first, then join abp network
void StartCommand(){
  //check class mode
  Serial2 << "mac" << " " << "get_class";
  delay(200);
  getClass();
  if(joinNetLock){
    Serial2 << "mac" << " " << "join" << " " << "abp";
    delay(100);
    while(Serial2.available()){
      Serial2.read();
      Serial.flush();
      Serial2.flush();
//      Serial.print(Serial2.read());
      }
    while(!Serial2.available()){
      Serial.flush();
      Serial2.flush();
      startLock = true;
      break;
      }
    }
  return;//
  }

//Get Class Mode by sending "mac get_class" command 
void getClass(){
  uint8_t classChar;
  String classString = "";
  for(uint8_t i=0 ; i<20 ; i++){
    while(Serial2.available()){
      classChar = Serial2.read();
      classString+=char(classChar);
      delay(2);
      }
    delay(100);
    }
  classString = classString.substring(5,6);
  if(classString=="A"){
    classModeLock = false;
    joinNetLock  = true;
  }else if(classString=="C"){
    classModeLock = true;
    joinNetLock  = true;
  }else{
    Serial2 << "mac" << " " << "get_class";
    delay(200);
    getClass();
    }
  return;//
  }

//Send Data 
void sendUplinkCmd(){
  dataTH();
  String DataPackage = "";
  for(uint8_t i=0 ; i<(sizeof(dataArray)/4) ; i++){
    DataPackage = LoRaPackageTx(DataType[i],dataArray[i]);
    Serial2 << "mac tx ucnf 15 " << DataPackage;
//    delay(200);
    delay(5);
    ULCount[i]+=1;
    getDataMode();
    delay(5000);
    DataPackage = "";
//===========================================//
//    ULTOEX(i);
    LogULTOEX(i);
    
//    Serial.print(DataType[i]);
//    Serial.print(",");
//    Serial.print(dataArray[i]);
//    Serial.print(",");
//    Serial.println(ULCount[i]);
    }
  }

//Package Data to Ascii HEX form
String LoRaPackageTx(String keyword, float data){
  String  str1, str2;
  uint8_t i;
  str1 = keyword+ data;
  char    test[str1.length()];
  
  for(i=0; i<str1.length(); i++){
    test[(i<<1)] =  str1[i]>>4;      //High byte of char
    test[(i<<1)+1] = str1[i]&0xF;    //Low byte of char
    if(test[(i<<1)]<0xA){
      test[(i<<1)] = test[(i<<1)] +0x30;   //0~9+0x30(48) => char '0'~'9' (0x30~0x39)
      }
    else{
      test[(i<<1)] = test[(i<<1)] +0x57;   //10~15+0x57(87) => char 'a'~'f' (0x61~0x66)
      }                    
    if(test[(i<<1)+1]<0xA){
      test[(i<<1)+1] = test[(i<<1)+1] +0x30;
      }
    else{
      test[(i<<1)+1] = test[(i<<1)+1] +0x57;
      }
  }
  test[(i<<1)] =  0x00;
  str2 = test;
  return str2;
}

//Check Class Mode, the define how to get msg
void getDataMode(){
  if(!classModeLock){
    getMsg();       //if class == A
    }else{
      return;       //if class == C
      }
  }

//Get TX Ack and Downlink data
void getMsg(){
  uint8_t dataBuffer[64], Len, LoopCount,i ,j;
  uint8_t count = 20 ;
  uint8_t c ;
  uint8_t k = 0;
//  uint8_t count = 30 ;
  String TxAckString = "";
  TxAckString.reserve(64);
  String TxAckSubString = "";
  TxAckSubString.reserve(32);
  Len = Serial2.available();
  for(LoopCount = 0 ; LoopCount < count ; LoopCount++){
    if(Len>0){
      while(Serial2.available()){
        c = Serial2.read();
        dataBuffer[k] = c;
        delayMicroseconds(50);//
        k++;
        }
               
//      Serial2.readBytes(dataBuffer,Len);
//      delay(3);
//      for(i=0; i<Len; i++){
//        Serial.print(char(dataBuffer[i]));
//      }
      delay(2);//
      for(i=0; i<Len; i++){
        if((dataBuffer[i]=='m'||dataBuffer[i+1]=='a'||dataBuffer[i+2]=='c')&&(dataBuffer[i+4]=='r'||dataBuffer[i+5]=='x')){
          DLCount++;
          for(j=i;j<Len;j++){
            TxAckString+=(char)dataBuffer[j];
            delayMicroseconds(50);
            }
          TxAckSubString = TxAckString.substring(9,TxAckString.length());      
          Len = 0;
          }
//          else{TxAckString = "";}
      } 
      for(i=0; i<Len; i++){
        if(dataBuffer[i]=='t'|| dataBuffer[i+2]=='_'|| dataBuffer[i+3]=='o'){
//          Serial.println("GETMSG");//
          Len = 0;
          }
      }
      if(Len==0){LoopCount = count+1;}
      }
      delay(300);
//        delay(200);

    }
    //substract the the downlink, get the real data
    for(uint8_t k = 0 ; k<TxAckSubString.length() ; k++){
      if(TxAckSubString[k] == '\x0a'|| TxAckSubString[k+1]=='\x0d'){
        TxAckSubString = TxAckSubString.substring(0,k+1);
        TxAckSubString.trim();
        break;
      } 
    }

    if(TxAckSubString!=""){
      String RealData = decodeAsciiData(TxAckSubString);
//      DLTOEX(RealData,DLCount);
      LogDLTOEX(RealData,DLCount);

//      Serial.print(RealData);
//      Serial.print(",");
//      Serial.println(DLCount);
      }
//    Serial.println("Search Down!!");
//    Serial.print("SSLen:");
//    Serial.println(TxAckSubString.length());
//    Serial.print("SS:");
//    Serial.println(TxAckSubString);
//    Serial.print("DLCount:");
//    Serial.println(DLCount);
//    Serial.print("ULCount01:");
//    Serial.println(ULCount[0]);
//    Serial.print("ULCount02:");
//    Serial.println(ULCount[1]);
//    Serial.println("===========================");
//    decodeAsciiData(TxAckSubString);
}

//decode the real data
String decodeAsciiData(String Data){
  uint8_t dataLen ,dataFormate;
  uint8_t count = 0;
  String rdata = "";
  dataLen = Data.length();
  char temp[dataLen];
//  Serial.print("dataLen:");
//  Serial.println(dataLen);
  for(uint8_t i=0;i<dataLen;i++){
    if(Data[i]>96){                         //check about char from 'a'~'f'
      temp[i] = (Data[i]-96)+9;             //change to real value from 10~15
      }
    else if(Data[i]>47 && Data[i]<58){      //check about char from '0'~'9'
      temp[i] = Data[i]-48;                 //change to real value from 0~9
      }
    else{
      temp[i] = Data[i];
      }
  }
  int a = sizeof(temp);
//  Serial.print("tempLen:");
//  Serial.println(a); 
  for(uint8_t j=0;j<dataLen;j+=2){ 
    dataFormate=(temp[j])*16+temp[j+1];     //combine two value together to HEX Value
    rdata += char(dataFormate);
//    Serial.print(char(dataFormate));
   }
//   Serial.println();
//   Serial.println(rdata);
  return rdata ;
  }

void loop() {
  sendUplinkCmd_Clock.update();
  //if class A mode, then get msg after sending data
  //if class C mode, then get msg every moment
  if(classModeLock){
    if (Serial2.available()) {
        delay(5);
        getMsg();
    }
  }
}
