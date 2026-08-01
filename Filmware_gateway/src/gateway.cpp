#include "gateway.h"

GatewayCallbacks::GatewayCallbacks(BLEGateway *instance) {
  gatewayInstance = instance;
}

void GatewayCallbacks::onResult(BLEAdvertisedDevice device) {
  String currentMac = device.getAddress().toString().c_str();
  currentMac.toLowerCase();
  int rssi = device.getRSSI();

  gatewayInstance->updateRSSI(currentMac, rssi);
}

BLEGateway::BLEGateway() {
  beaconMacs[0] = "3c:8a:1f:d4:a0:dc";
  beaconMacs[1] = "e0:72:a1:d7:18:f5";
  beaconMacs[2] = "14:63:93:8c:fa:6e";

  unsigned long bootTime = millis();
  for (int i = 0; i < 3; i++) {
    rawRssiValues[i] = -100;
    filteredRssiValues[i] = -100.0f;
    lastSeenTimes[i] = bootTime;
  }
}

static bool matchMacAddress(const String &scannedMac, const String &targetMac) {
  if (scannedMac.equalsIgnoreCase(targetMac))
    return true;

  if (scannedMac.length() >= 12 && targetMac.length() >= 12) {
    if (scannedMac.substring(0, 12).equalsIgnoreCase(
            targetMac.substring(0, 12))) {
      return true;
    }
  }
  
  if (scannedMac.length() >= 17 && targetMac.length() >= 17) {
    if (scannedMac.substring(12, 17).equalsIgnoreCase(
            targetMac.substring(12, 17))) {
      return true;
    }
  }
  return false;
}

void BLEGateway::updateRSSI(String mac, int rssi) {
  unsigned long now = millis();
  mac.toLowerCase();

  bool matchedAny = false;
  for (int i = 0; i < 3; i++) {
    if (matchMacAddress(mac, beaconMacs[i])) {
      matchedAny = true;
      rawRssiValues[i] = rssi;
      lastSeenTimes[i] = now;

      
      if (filteredRssiValues[i] <= -99.0f) {
        filteredRssiValues[i] = (float)rssi;
      } else {
        filteredRssiValues[i] =
            0.4f * (float)rssi + 0.6f * filteredRssiValues[i];
      }

      Serial.print("[BLE MATCH] Beacon ");
      Serial.print(i + 1);
      Serial.print(" (Scanned MAC: ");
      Serial.print(mac);
      Serial.print(") -> RSSI: ");
      Serial.print(rssi);
      Serial.print(" | Filtered: ");
      Serial.println((int)round(filteredRssiValues[i]));
    }
  }


  if (!matchedAny && (mac.startsWith("3c:8a") || mac.startsWith("ec:da") ||
                      mac.startsWith("14:63"))) {
    Serial.print("[BLE SCANNED OTHER ESP32] MAC: ");
    Serial.print(mac);
    Serial.print(" | RSSI: ");
    Serial.println(rssi);
  }
}

void BLEGateway::begin() {
  BLEDevice::init("Gateway");
  pBLEScan = BLEDevice::getScan();

  pBLEScan->setAdvertisedDeviceCallbacks(new GatewayCallbacks(this));

  pBLEScan->setActiveScan(true);
  pBLEScan->setInterval(160);
  pBLEScan->setWindow(120);
}

void BLEGateway::scanAndPrint() {
  pBLEScan->start(1, false);

  unsigned long now = millis();
  for (int i = 0; i < 3; i++) {
    if (now - lastSeenTimes[i] > 6000) {
      filteredRssiValues[i] = -100.0f;
      rawRssiValues[i] = -100;
    }
  }

         Serial.print("=== RSSI STATUS -> B1 (58): ");
  Serial.print((int)round(filteredRssiValues[0]));
  Serial.print(" | B2 (dc): ");
  Serial.print((int)round(filteredRssiValues[1]));
  Serial.print(" | B3 (6c): ");
  Serial.println((int)round(filteredRssiValues[2]));

  pBLEScan->clearResults();
}

int *BLEGateway::getRssiValues() {
  static int result[3];
  for (int i = 0; i < 3; i++) {
    result[i] = (int)round(filteredRssiValues[i]);
  }
  return result;
}

int BLEGateway::getFilteredRssi(int index) {
  if (index >= 0 && index < 3) {
    return (int)round(filteredRssiValues[index]);
  }
  return -100;
}