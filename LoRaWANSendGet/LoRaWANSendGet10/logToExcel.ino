void LogULTOEX(uint8_t index){
  Serial.print(DataType[index]);
  Serial.print(",");
  Serial.print(dataArray[index]);
  Serial.print(",");
  Serial.println(ULCount[index]);
  }
void LogDLTOEX(String RDATA, uint16_t DCOUNT){
  Serial.print(RDATA);
  Serial.print(",");
  Serial.println(DCOUNT);
  
  }
