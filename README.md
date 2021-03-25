### LoRaWan_IntelligentCity ###
#### package ####
>1. Communicate with CHIOT(Cloud Service of Chunghwa Telecom Co., Ltd. Taiwan)
>2. Communicate with Google Firebase firestore

#### BTSS02 ####
>1. An Actuator control vis bluetooth
>2. Extend to OscarMing/Gas_Sensor Repo(https://github.com/OscarMing/Gas_Sensor) .

#### CoreRun.py ####
>1. An MCU Sensing Prototype Module.
>2. Include Temperature, Humidity also extend to OscarMing/Gas_Sensor Repo(https://github.com/OscarMing/Gas_Sensor) .
>3. Data via LoRa to communicate with backend.
>4. Post Data to Firebase, NodeRED Dashboard, CHIOT(Cloud Service of Chunghwa Telecom Co., Ltd. Taiwan)

#### LocalQuery.py ####
>1. An RPI Zero and MCU combine, RPI use Serial Port.
>2. Query Data and Save as CSV File.

#### IFTTTTOLINENotify.py ####
>1. Query Data via LoRA Gateway and MQTT .
>2. Send Notification to LINE.