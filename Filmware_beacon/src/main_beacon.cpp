#include <Arduino.h>
#include "beacon.h"

BLEBeacon myBeacon("Beacon_ESP32");

void setup() {
    Serial.begin(115200);
    delay(500);
    Serial.println("Beacon khởi động...");
    myBeacon.begin();
    Serial.print("BLE MAC Address cua thiet bi nay: ");
    Serial.println(BLEDevice::getAddress().toString().c_str());
}

void loop() {
    delay(1000);
}