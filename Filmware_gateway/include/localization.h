#ifndef LOCALIZATION_H
#define LOCALIZATION_H

#include <Arduino.h>

struct Point {
    double x;
    double y;
};

struct BeaconConfig {
    String macAddress;
    double x;
    double y;
    double A;
    double n;
};

double rssiToDistance(int rssi, double A, double n);
Point calculateGatewayPosition(double d1, double d2, double d3, BeaconConfig beacons[]);

#endif