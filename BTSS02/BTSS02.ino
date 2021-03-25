#include <SoftwareSerial.h>
 

//SoftwareSerial BT(11, 10);
SoftwareSerial BT(8, 9);  
char val;
const byte LED_PIN = 13;
const byte RELAY_PIN = 3;
 
void setup() {
  Serial.begin(9600);
  Serial.setTimeout(100);
  BT.begin(38400);
  pinMode(LED_PIN, OUTPUT);
  pinMode(RELAY_PIN, OUTPUT);
}
 
void loop() {
  String ss = "";
  while (BT.available()) {
//    val = BT.read();
//    ss+=val;
    ss = BT.readStringUntil('\n');
//    delay(2);
  }
//  delay(10);
  if(ss.length()>2){
    cmds(ss);
    }

}

void cmds(String SDS){
  Serial.println(SDS);
  Serial.println(SDS.length());
  if(SDS.substring(0,1) == "A"){
    if (SDS.substring(2,3) == "1") {
      digitalWrite(LED_PIN, HIGH);
//      digitalWrite(RELAY_PIN, LOW);
//      delay(10);
      digitalWrite(RELAY_PIN, HIGH);
      BT.println("A:LED ON");
    } else if (SDS.substring(2,3) == "0") {
      digitalWrite(LED_PIN, LOW);
      digitalWrite(RELAY_PIN, LOW);
//      delay(10);
//      digitalWrite(RELAY_PIN, HIGH);
      BT.println("A:LED OFF");
    }
  }
  else if(SDS.substring(0,1) == "B"){
    if (SDS.substring(2,3) == "1") {
      digitalWrite(LED_PIN, LOW);
      digitalWrite(RELAY_PIN, LOW);
//      delay(10);
//      digitalWrite(RELAY_PIN, HIGH);
      BT.println("B:LED OFF");
    } else if (SDS.substring(2,3) == "0") {
      digitalWrite(LED_PIN, HIGH);
//      digitalWrite(RELAY_PIN, LOW);
//      delay(10);
      digitalWrite(RELAY_PIN, HIGH);
      BT.println("B:LED ON");
    }
    
    
    }

}
