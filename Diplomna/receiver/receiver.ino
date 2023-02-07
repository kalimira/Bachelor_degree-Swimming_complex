#include <SPI.h>
#include <nRF24L01.h>
#include <RF24.h>
#include <UIPEthernet.h>


void connection();

struct {
  float pooltemp1data;
  float pooltemp2data;
  float airtempdata;
  float uvdata;
}measurements;

byte mac[] = { 0xDE, 0xAD, 0xBE, 0xEF, 0xFE, 0xED };
EthernetClient client;

int    HTTP_PORT   = 80;
String HTTP_METHOD = "GET";
char   HOST_NAME1[] = "192.168.0.105"; 

float pt1data, pt2data, atdata, sunuvdata;
String buffer;
RF24 radio(9, 10);

void setup() {
  Serial.begin(115200);
  radio.begin();
  radio.openReadingPipe(0, 0xF0F0F0F0CC);
  radio.setPALevel(RF24_PA_MAX);
  radio.startListening();
  Ethernet.begin(mac);
  if (Ethernet.hardwareStatus() == EthernetNoHardware) {
    Serial.println("Sorry, can't run without hardware. :(");
    while (1) {
      delay(5); 
    }
  }
}


void loop() 
{
  if(radio.available())
  {
    radio.read(&measurements, sizeof(measurements));
    Serial.println(measurements.pooltemp1data);
    Serial.println(measurements.pooltemp2data);
    Serial.println(measurements.uvdata);
    Serial.println(measurements.airtempdata);
  
    pt1data = measurements.pooltemp1data;
    pt2data = measurements.pooltemp2data;
    atdata = measurements.airtempdata;
    sunuvdata = measurements.uvdata;
    connection();
  }
}  


void connection()
{
  while(client.connect("192.168.0.105", 80)) 
  {
    client.print("GET /arduino/insert.php?pt1data=");
    client.print(pt1data);
    client.print("&pt2data=");
    client.print(pt2data);
    client.print("&atdata=");
    client.print(atdata);
    client.print("&sunuvdata=");
    client.print(sunuvdata);
    client.print(" ");
    client.print("HTTP/1.1");
    client.println();
    client.println("Host: " + String(HOST_NAME1));
    client.println("Connection: close");
    client.println();
    
    while(client.connected()) {
      if(client.available()){
        char c = client.read();
        Serial.print(c);
      }
    }
    
    client.stop();
    Serial.println();
    Serial.println("disconnected");
    break;
  } 
}
