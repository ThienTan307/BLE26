#ifndef BEACON_H
#define BEACON_H

#include <Arduino.h>
#include <BLEDevice.h>
#include <BLEServer.h>

class BLEBeacon {
private:
    String beaconName;

public:
    BLEBeacon(String name);
    void begin();
};

#endif