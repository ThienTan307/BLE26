#ifndef GATEWAY_H
#define GATEWAY_H

#include <Arduino.h>
#include <BLEDevice.h>
#include <BLEScan.h>
#include <BLEAdvertisedDevice.h>

class BLEGateway {
private:
    String beaconMacs[3];
    int rawRssiValues[3];
    float filteredRssiValues[3];
    unsigned long lastSeenTimes[3];
    BLEScan* pBLEScan;

public:
    BLEGateway();
    void begin();
    void scanAndPrint();
    void updateRSSI(String mac, int rssi);
    int* getRssiValues();
    int getFilteredRssi(int index);
};

class GatewayCallbacks: public BLEAdvertisedDeviceCallbacks {
private:
    BLEGateway* gatewayInstance;
public:
    GatewayCallbacks(BLEGateway* instance);
    void onResult(BLEAdvertisedDevice device);
};

#endif