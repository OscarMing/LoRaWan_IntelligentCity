int dataTH() {
  delay(1500);
  float h = dht.readHumidity();
  float t = dht.readTemperature();
  float f = dht.readTemperature(true);
  if (isnan(h) || isnan(t) || isnan(f)) {
    Serial.println("Failed to read from DHT sensor!");
  }
  dataArray[0] = h ;
  dataArray[1] = t ;
//  dataArray[2] = f ;
  return *dataArray;
}
