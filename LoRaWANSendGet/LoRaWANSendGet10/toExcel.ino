void ULTOEX(uint8_t index){
  Serial.print("DATA, DATE, TIME,");
  Serial.print(dataArray[index]);
  Serial.print(",");
  Serial.print(DataType[index]);
  Serial.print(",");
  Serial.println(ULCount[index]);
  }

void DLTOEX(String RDATA, uint16_t DCOUNT){
  String X = "H"+String(DCOUNT+1);
  String Y = "I"+String(DCOUNT+1);
  String Z = "J"+String(DCOUNT+1);
  Serial.print("CELL,SET,"); 
  Serial.print(X);
  Serial.print(",");
  Serial.println(RDATA);
  
  Serial.print("CELL,SET,"); 
  Serial.print(Y);
  Serial.print(",");
  Serial.println("TIME");
  
  Serial.print("CELL,SET,"); 
  Serial.print(Z);
  Serial.print(",");
  Serial.println(DCOUNT);
  }
