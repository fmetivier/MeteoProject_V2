// Date and time functions using a DS1307 RTC connected
// via I2C and Wirelib
// <jc@wippler.nl> http://opensource.org/licenses/mit-license.php
#include <Wire.h>
#include <RTClib.h>
#define ADRESSE_I2C_RTC 0x68 // RTC card address

RTC_DS1307 RTC;
void setup ()
{
Serial.begin(9600); // Initialisation de la liaison série
Wire.begin();
Wire.beginTransmission(ADRESSE_I2C_RTC);
RTC.begin();
// Cette ligne permet de définir une heure de départ pour le module RTC
//(Année, mois, jour, //heure, minute, seconde)
// Elle peut être mise en commentaire une fois le module mis Ã jour.

  RTC.adjust(DateTime(F(__DATE__), F(__TIME__)));
  Serial.println("Horloge mise à jour");
Wire.endTransmission();


}
void loop ()
{
  Wire.beginTransmission(ADRESSE_I2C_RTC);
  DateTime now = RTC.now();
  Wire.endTransmission();
Serial.print(now.day(), DEC);
Serial.print('/');
Serial.print(now.month(), DEC);
Serial.print('/');
Serial.print(now.year(), DEC);
Serial.println(' ');
Serial.print(now.hour(), DEC);
Serial.print(':');
Serial.print(now.minute(), DEC);
Serial.print(':');
Serial.print(now.second(), DEC);
Serial.println();
delay(3000);

}
