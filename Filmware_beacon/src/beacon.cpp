#include "beacon.h"

BLEBeacon::BLEBeacon(String name) {
    beaconName = name;
}

void BLEBeacon::begin() {
    BLEDevice::init(beaconName.c_str());
    
    BLEServer *pServer = BLEDevice::createServer();
    BLEAdvertising *pAdvertising = pServer->getAdvertising();
    
    pAdvertising->setScanResponse(true);
    pAdvertising->setMinPreferred(0x06);
    
    pAdvertising->start();
    Serial.println("Beacon đang phát sóng...");
}