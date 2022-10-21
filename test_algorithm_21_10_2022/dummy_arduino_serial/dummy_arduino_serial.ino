//sudo chmod a+rw /dev/ttyACM0

#define ERROR_PROBABILITY 4
void setup() {
  Serial.begin(9600);
}

void loop() {
  if (Serial.available() > 0) {
    delay(50);
    while (Serial.available()) {
      Serial.read();
    }

    uint8_t is_error = random(ERROR_PROBABILITY);
    if (is_error > 0) {
      Serial.println(random(50));
    }

  }
}
