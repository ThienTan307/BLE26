#include <Arduino.h>
#include <WiFi.h>
#include <PubSubClient.h>
#include "gateway.h"
#include "localization.h"
#include "ema_filter.h"

const char* ssid = "THIEN TAN";
const char* password = "0912345678";
const char* mqtt_server = "192.168.100.234";
const int mqtt_port = 1883;

WiFiClient espClient;
PubSubClient client(espClient);
BLEGateway myGateway;

EMAFilter rssiFilters[3] = { EMAFilter(0.2), EMAFilter(0.2), EMAFilter(0.2) };

BeaconConfig myBeaconConfigs[3] = {
    {"3c:8a:1f:d4:a0:dc", 0.0 , 0.6 , -60, 3.5}, 
    {"e0:72:a1:d7:18:f5", 0.0 , 0.0 , -60, 3.5},
    {"14:63:93:8c:fa:6e", 1.2 , 0.0, -60, 3.5}
};
static double smooth_pos_x = -999.0;
static double smooth_pos_y = -999.0;

void setup_wifi() {
    delay(10);
    Serial.println();
    Serial.print("Dang ket noi Wi-Fi: ");
    Serial.println(ssid);

    WiFi.mode(WIFI_STA); 
    WiFi.begin(ssid, password);
    
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }
    Serial.println("\nWi-Fi da ket noi thanh cong!");
    Serial.print("IP address: ");
    Serial.println(WiFi.localIP());
}
void reconnect() {
    while (!client.connected()) {
        Serial.print("Dang ket noi MQTT Broker...");
        String clientId = "ESP32_Gateway_Tan_307";
        
        if (client.connect(clientId.c_str())) {
            Serial.println(" -> KET NOI MQTT THANH CONG!");
        } else {
            Serial.print(" -> That bai, rc=");
            Serial.print(client.state()); 
            Serial.println(" Thu lai sau 2 giay...");
            delay(2000);
        }
    }
}

void sendMQTTArray(int rssi1, int rssi2, int rssi3) {
    if (client.connected()) {
        String mac1 = myBeaconConfigs[0].macAddress;
        String mac2 = myBeaconConfigs[1].macAddress;
        String mac3 = myBeaconConfigs[2].macAddress;

        String p1 = "{\"address\":\"" + mac1 + "\",\"rssi\":" + String(rssi1) + "}";
        String p2 = "{\"address\":\"" + mac2 + "\",\"rssi\":" + String(rssi2) + "}";
        String p3 = "{\"address\":\"" + mac3 + "\",\"rssi\":" + String(rssi3) + "}";

        client.publish("beacon/rssi", p1.c_str());
        client.publish("beacon/rssi", p2.c_str());
        client.publish("beacon/rssi", p3.c_str());
    }
}

void sendPositionMQTT(double x, double y) {
    if (client.connected()) {
        String jsonPayload = "{\"x\":" + String(x, 2) + ",\"y\":" + String(y, 2) + "}";
        client.publish("beacon/location", jsonPayload.c_str());
    } 
}

void sendDistanceMQTT(double d1, double d2, double d3) {
  if (client.connected()) {
    String jsonPayload = "{\"d1\":" + String(d1, 2) + 
                         ",\"d2\":" + String(d2, 2) + 
                         ",\"d3\":" + String(d3, 2) + "}";
    client.publish("beacon/distance", jsonPayload.c_str());
  }
}

void setup() {
    Serial.begin(115200);
    delay(1000);
    setup_wifi();
    client.setServer(mqtt_server, mqtt_port);
    myGateway.begin();
}

void loop() {
    if (!client.connected()) {
        reconnect();
    }
    client.loop();
    
    Serial.println("\n--- Dang quet Beacon ---");
    myGateway.scanAndPrint();
    
    int* rssis = myGateway.getRssiValues();

 
    double smooth_rssi[3];
    for (int i = 0; i < 3; i++) {
        smooth_rssi[i] = rssiFilters[i].update((double)rssis[i]);
    }


    double d1 = rssiToDistance(smooth_rssi[0], myBeaconConfigs[0].A, myBeaconConfigs[0].n);
    double d2 = rssiToDistance(smooth_rssi[1], myBeaconConfigs[1].A, myBeaconConfigs[1].n);
    double d3 = rssiToDistance(smooth_rssi[2], myBeaconConfigs[2].A, myBeaconConfigs[2].n);

    Serial.print("Khoang cach (m) -> d1: "); Serial.print(d1);
    Serial.print(" | d2: "); Serial.print(d2);
    Serial.print(" | d3: "); Serial.println(d3);

    sendMQTTArray(rssis[0], rssis[1], rssis[2]);
    delay(10);

    sendDistanceMQTT(d1, d2, d3);
    delay(10);

    if (d1 > 0 && d2 > 0 && d3 > 0) {
        Point rawPos = calculateGatewayPosition(d1, d2, d3, myBeaconConfigs);
        
        if (rawPos.x != -1.0 && rawPos.y != -1.0) {
            if (smooth_pos_x == -999.0) {
                smooth_pos_x = rawPos.x;
                smooth_pos_y = rawPos.y;
            } else {
                smooth_pos_x = 0.3 * rawPos.x + 0.7 * smooth_pos_x;
                smooth_pos_y = 0.3 * rawPos.y + 0.7 * smooth_pos_y;
            }

            Serial.print("===> TOA DO GATEWAY (Smooth): X = "); Serial.print(smooth_pos_x);
            Serial.print(", Y = "); Serial.println(smooth_pos_y);
          
            sendPositionMQTT(smooth_pos_x, smooth_pos_y);
        } else {
            Serial.println("Loi: Khong the tinh vi tri (det xap xi 0)");
        }
    } else {
        Serial.println("Khong quet du ca 3 Beacon hop le de tinh toa do.");
    }

    delay(30);
    Serial.print("Raw RSSI: "); Serial.print(rssis[0]);
    Serial.print(" | Smooth EMA RSSI: "); Serial.println(smooth_rssi[0]);
}