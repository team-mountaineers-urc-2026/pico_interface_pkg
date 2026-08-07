#include <Wire.h>

#define SENSOR_ADDR 0x28

void setup() {
  Serial.begin(115200);  // match node baudrate
  while (!Serial);

  pinMode(4, INPUT_PULLUP);
  pinMode(5, INPUT_PULLUP);
  Wire.begin();
}

void loop() {
  Wire.requestFrom(SENSOR_ADDR, 2);
  if (Wire.available() == 2) {
    byte high = Wire.read();
    byte low  = Wire.read();
    int raw = ((high & 0x3F) << 8) | low;
    Serial.println("force," + String(raw));  // e.g. "force,1042"
  }

  delay(50);
}