void setup() {
  Serial.begin(9600);

}

void loop() {
  if(Serial.available()){
    while(Serial.available()){
      Serial.read();
      delay(10);
    } 
    long random_number =random(50);
    long error_rate =random(2);
    if(error_rate !=0){
      Serial.println(random_number);
    }
  }
}
