#include <OneWire.h> 
#include <DallasTemperature.h>
#include <SPI.h>
#include <nRF24L01.h>
#include <RF24.h>

#define ptemp1 2 
#define ptemp2 4 


void pool_temperature();
void uvindex();
void temperature();

RF24 radio(9, 10);  


OneWire oneWire1(ptemp1); 
OneWire oneWire2(ptemp2); 


DallasTemperature sensor1(&oneWire1);
DallasTemperature sensor2(&oneWire2);

int UVOUT = A5; 
int REF_3V3 = A4; 
int count = 0;

float pooltemp1, pooltemp2, airtemp;

int8_t ThermistorPin = 0;
int Vo;
float R1 = 10500;
float logR2, R2, T;
float c1 = 1.009249522e-03, c2 = 2.378405444e-04, c3 = 2.019202697e-07;

struct {
  float pooltemp1data;
  float pooltemp2data;
  float airtempdata;
  float uvdata;
}measurements;

void setup(void) 
{  
 Serial.begin(9600); 
 sensor1.begin(); 
 sensor2.begin(); 
 pinMode(UVOUT, INPUT);
 pinMode(REF_3V3, INPUT);
 radio.begin();
 radio.openWritingPipe(0xF0F0F0F0CC);
 radio.setPALevel(RF24_PA_MAX);
 radio.stopListening();
} 

void loop(void) 
{ 
   pool_temperature();
   measurements.pooltemp1data = pooltemp1;
   measurements.pooltemp2data = pooltemp2;
   uvindex();
   air_temperature();
   measurements.airtempdata = airtemp;
   radio.write(&measurements, sizeof(measurements));
   Serial.println(measurements.airtempdata);
   Serial.println(measurements.pooltemp1data);
   delay(10000);
} 

void pool_temperature()
{
 sensor1.requestTemperatures();
 sensor2.requestTemperatures(); 
 pooltemp1 = sensor1.getTempCByIndex(0);
 pooltemp2 = sensor2.getTempCByIndex(0);
}


void uvindex()
{  
 float fresult = NULL;
 int uvLevel = averageAnalogRead(UVOUT);
 int refLevel = averageAnalogRead(REF_3V3);
 float outputVoltage = 3.3 / refLevel * uvLevel;  
 float uvIntensity = mapfloat(outputVoltage, 0.99, 2.8, 0.0, 15.0);  
 measurements.uvdata = uvIntensity;
}

int averageAnalogRead(int pinToRead)
{
  byte numberOfReadings = 8;
  unsigned int runningValue = 0; 
  for(int x = 0 ; x < numberOfReadings ; x++)
    runningValue += analogRead(pinToRead);
  runningValue /= numberOfReadings;
  return(runningValue);  
}

float mapfloat(float x, float in_min, float in_max, float out_min, float out_max)
{
  return ((x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min);
}


void air_temperature()
{
  Vo = analogRead(ThermistorPin);
  R2 = R1 * (1023.0 / (float)Vo - 1.0);
  logR2 = log(R2);
  airtemp = (1.0 / (c1 + c2*logR2 + c3*logR2*logR2*logR2));
  airtemp = airtemp - 273.15;
  airtemp = ceilf(airtemp * 100) / 100;  
}
