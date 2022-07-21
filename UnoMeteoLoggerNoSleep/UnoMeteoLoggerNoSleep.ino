


//SD Card lib
#include <SPI.h>
#include <SD.h>
const int chipSelect = 4; // SD card on Nano

//RTC lib
#include <Wire.h>
#include <RTClib.h>
#define ADRESSE_I2C_RTC 0x68 // RTC card address
RTC_DS1307 rtc;

// DHT sensor lib
#include <DHT_U.h>
#include <DHT.h>
#define DHT_TYPE DHT11
#define DHT_PIN 7
DHT dht(DHT_PIN,DHT_TYPE);


const byte pluvio = 2;  // pullup for pluviometer on D2
volatile int pcount = 0;
long t0 = 0;



void setup()
{
  Serial.begin(9600); // pour affichage dans le moniteur série
  
  pinMode(pluvio, INPUT_PULLUP);
 
  attachInterrupt(digitalPinToInterrupt(pluvio), pCount, FALLING);

  while (!Serial) {
   delay(100) ; // wait for serial port to connect. Needed for native USB port only
  }

  Wire.begin();
  Wire.beginTransmission(ADRESSE_I2C_RTC);
  while (!rtc.begin()){
      Serial.println("Attente module HTR");
      delay(1000);
  }
  Wire.endTransmission();

  dht.begin(); 

  Serial.print("Initializing SD card...");

  // see if the card is present and can be initialized:
  if (!SD.begin(chipSelect)) {
    Serial.println("Card failed, or not present");
    // don't do anything more:
    //while (1);
  }
  else {
    Serial.println("card initialized.");
  }
}

void loop()
{
  Wire.beginTransmission(ADRESSE_I2C_RTC);
  DateTime now = rtc.now();
  Wire.endTransmission();

  char sdate[12];
  sprintf(sdate,"%04d:%02d:%02d",now.year(),now.month(),now.day());
  char stime[10];
  sprintf(stime,"%02d:%02d:%02d",now.hour(),now.minute(),now.second());
 
  // input voltage
  //int sensorValue = analogRead(A0);


 if (pcount > 0){
 
  String dataString =  "p,";
  dataString +=  String(sdate) + "," + String(stime) + "," +  String(pcount) + "\n";
  Serial.print(dataString);

  writeData(dataString);
  pcount=0;
 }
 if (abs(now.unixtime()-t0) >= 300){

 
  float t = dht.readTemperature();
  float h = dht.readHumidity();
  
    
    String dataString = "w," + String(sdate) + "," + String(stime) + "," + String(t) + " , " + String(h) + "\n";
    
   Serial.print(dataString);
    writeData(dataString);
    Serial.println(now.unixtime()-t0);
    t0 = now.unixtime();
    Serial.println(t0);
 
    
 }
  
}



void writeData(String dataString)
{
  if (SD.begin(chipSelect)){
  
     File dataFile = SD.open("METEOLOG.TXT", FILE_WRITE);
  
     // if the file is available, write to it:
     if (dataFile) {
      dataFile.print(dataString);
      dataFile.close();
     }
     // if the file isn't open, pop up an error:
     else {
       Serial.println("error opening METEOLOG.TXT");
     }
   }
   else{
    Serial.println("No card available. Loosing data");
   }
}


void pCount()
{

  pcount += 1;
  
}
