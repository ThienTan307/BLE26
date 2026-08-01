#include "localization.h"
#include <math.h>

double rssiToDistance(int rssi, double A, double n) {
   
    if (rssi >= 0 || rssi <= -95) return -1.0; 
    
  
    double dist = pow(10.0, (A - (double)rssi) / (10.0 * n));
    
   
    if (dist > 10.0) return 10.0;
    if (dist < 0.05) return 0.05;
    return dist;
}


Point calculateGatewayPosition(double d1, double d2, double d3, BeaconConfig beacons[]) {
    Point gatewayPos = {-1.0, -1.0};

    if (d1 <= 0 || d2 <= 0 || d3 <= 0) {
        return gatewayPos;
    }

    double x = (beacons[0].x + beacons[1].x + beacons[2].x) / 3.0;
    double y = (beacons[0].y + beacons[1].y + beacons[2].y) / 3.0;

    double d[3] = {d1, d2, d3};
    double learning_rate = 0.05; 
    int epochs = 100;            

    for (int step = 0; step < epochs; step++) {
        double grad_x = 0.0;
        double grad_y = 0.0;

        for (int i = 0; i < 3; i++) {
          
            double dist_calc = sqrt(pow(x - beacons[i].x, 2) + pow(y - beacons[i].y, 2));
            if (dist_calc < 0.001) continue; 

        
            double error = dist_calc - d[i];
            
            grad_x += 2.0 * error * (x - beacons[i].x) / dist_calc;
            grad_y += 2.0 * error * (y - beacons[i].y) / dist_calc;
        }

        x -= learning_rate * grad_x;
        y -= learning_rate * grad_y;
    }

    gatewayPos.x = x;
    gatewayPos.y = y;
    
    return gatewayPos;
   
}