#include <dht.h>

dht DHT;

#define DHT11_PIN 7

void setup(){
  Serial.begin(9600);
}

void loop(){
  int chk = DHT.read11(DHT11_PIN);
  float temp = DHT.temperature;
  float humid = DHT.humidity;
  if(temp != -999.0 && humid != -999.0) {
    Serial.print("Temperature = ");
    Serial.println(temp);
    Serial.print("Humidity = ");
    Serial.println(humid);
  }
  delay(1000);
}
