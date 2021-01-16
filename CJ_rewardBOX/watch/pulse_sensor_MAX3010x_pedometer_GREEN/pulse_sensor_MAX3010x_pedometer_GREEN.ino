  /*
  This is a demo to show the reading of heart rate or beats per minute (BPM) using
  a Penpheral Beat Amplitude (PBA) algorithm.

 Hardware Connections (Breakoutboard to Arduino):
  -5V = 5V (3.3V is allowed)
  -GND = GND
  -SDA = A4 (or SDA)
  -SCL = A5 (or SCL)
  -INT = Not connected
*/
//For pedometer
#include "SparkFunLSM6DS3.h"
#include "Wire.h"

#define CLEAR_STEP      true
#define NOT_CLEAR_STEP  false

//Create a instance of class LSM6DS3
LSM6DS3 pedometer( I2C_MODE, 0x6A );  //I2C device address 0x6A

long lastMsg = 0;
String stepCount_str;
char stepCount_char[50];
char beatAvg_char[50];
int value = 0;

#include <Wire.h>
#include "MAX30105.h"
#include "heartRate.h"
#include <Adafruit_NeoPixel.h>
#ifdef __AVR__
#include <avr/power.h>
#endif

MAX30105 particleSensor;

#define PIN            12
#define NUMPIXELS     8
Adafruit_NeoPixel pixels = Adafruit_NeoPixel(NUMPIXELS, PIN, NEO_GRBW + NEO_KHZ800);


const byte RATE_SIZE = 4; //Increase this for more averaging. 4 is good.
byte rates[RATE_SIZE]; //Array of heart rates
byte rateSpot = 0;
long lastBeat = 0; //Time at which the last beat occurred

float beatsPerMinute;
int beatAvg;

void setup()
{
  Serial.begin(115200);
    if ( pedometer.begin() != 0 ) {
    Serial.println("Device error");
  }
  else {
    Serial.println("Device OK!");
  }

   if ( 0 != config_pedometer(NOT_CLEAR_STEP) )
  {
    Serial.println("Configure pedometer fail!");
  }
  Serial.println("Success to Configure pedometer!");
  Serial.println("Initializing...");
    pixels.begin(); // This initializes the NeoPixel library.


  // Initialize sensor
  if (!particleSensor.begin(Wire, I2C_SPEED_FAST)) //Use default I2C port, 300kHz speed
  {
    Serial.println("MAX30105 was not found. Please check wiring/power. ");
    while (1);
  }
  Serial.println("Place your index finger on the sensor with steady pressure.");

  particleSensor.setup(); //Configure sensor with default settings
  particleSensor.setPulseAmplitudeRed(0); //Turn Red LED to low to indicate sensor is running
  particleSensor.setPulseAmplitudeGreen(0x0F); //Turn Green LED
}

void loop()
{  uint8_t dataByte = 0;
  uint16_t stepCount = 0;
  long greenValue = particleSensor.getGreen();

  if (checkForBeat(greenValue) == true)
  {
    //We sensed a beat!
    long delta = millis() - lastBeat;
    lastBeat = millis();

    beatsPerMinute = 60 / (delta / 1000.0);

    if (beatsPerMinute < 255 && beatsPerMinute > 20)
    {
      rates[rateSpot++] = (byte)beatsPerMinute; //Store this reading in the array
      rateSpot %= RATE_SIZE; //Wrap variable

      //Take average of readings
      beatAvg = 0;
      for (byte x = 0 ; x < RATE_SIZE ; x++)
        beatAvg += rates[x];
      beatAvg /= RATE_SIZE;
    }
  }


int r,g,b,w;
int max_bright = 100; //value of maximum brightness, max 255. But you don't always want it at max :)
float dd = 20; //change in BPM between color tones (blue->green->yellow->pink->red)
float t1 = 60, t2, t3, t4; //t1 - "base" BPM, lower than t1 would be blue
t2 = t1 + dd;
t3 = t2 + dd;
t4 = t3 + dd;

if(beatAvg < t1){ r = 0; g = 0; b = max_bright, w=0; }
else if(beatAvg < t2) { r = 0; g = max_bright * (beatAvg-t1)/dd; b = max_bright - g, w=0; }
else if(beatAvg < t3) { r = max_bright * (beatAvg-t2)/dd; g = max_bright - r; b = r/4, w=0; }
else if(beatAvg < t4) { r = max_bright; g = 0; b = max_bright/2 - max_bright * (beatAvg-t3)/(2*dd), w=0; }
else {r = max_bright; g = 0; b = 0, w=0; }

int on_pixels = (beatAvg+5)/15; //number of used LEDs: for 60 BPM, 6 LEDs will be on, for 120 - 12 etc
for(int i=0;i<NUMPIXELS;i++)
{
if(i < on_pixels) pixels.setPixelColor(i, pixels.Color(r,g,b,w));
else pixels.setPixelColor(i, pixels.Color(0,0,0,0)); //turn off all other LEDs
}
pixels.show();

    pedometer.readRegister(&dataByte, LSM6DS3_ACC_GYRO_STEP_COUNTER_H);
    stepCount = (dataByte << 8) & 0xFFFF;

    pedometer.readRegister(&dataByte, LSM6DS3_ACC_GYRO_STEP_COUNTER_L);
    stepCount |=  dataByte;

    Serial.print("Step: ");
    Serial.println(stepCount);
    Serial.print("GREEN=");
   Serial.print(greenValue);
   Serial.print(", BPM=");
   Serial.print(beatsPerMinute);
   Serial.print(", Avg BPM=");
   Serial.print(beatAvg);

 Serial.println();

}

//Setup pedometer mode
int config_pedometer(bool clearStep)
{
  uint8_t errorAccumulator = 0;
  uint8_t dataToWrite = 0;  //Temporary variable

  //Setup the accelerometer******************************
  dataToWrite = 0;

  //  dataToWrite |= LSM6DS3_ACC_GYRO_BW_XL_200Hz;
  dataToWrite |= LSM6DS3_ACC_GYRO_FS_XL_2g;
  dataToWrite |= LSM6DS3_ACC_GYRO_ODR_XL_26Hz;


  // Step 1: Configure ODR-26Hz and FS-2g
  errorAccumulator += pedometer.writeRegister(LSM6DS3_ACC_GYRO_CTRL1_XL, dataToWrite);

  // Step 2: Set bit Zen_G, Yen_G, Xen_G, FUNC_EN, PEDO_RST_STEP(1 or 0)
  if (clearStep)
    errorAccumulator += pedometer.writeRegister(LSM6DS3_ACC_GYRO_CTRL10_C, 0x3E);
  else
    errorAccumulator += pedometer.writeRegister(LSM6DS3_ACC_GYRO_CTRL10_C, 0x3C);

  // Step 3:  Enable pedometer algorithm
  errorAccumulator += pedometer.writeRegister(LSM6DS3_ACC_GYRO_TAP_CFG1, 0x40);

  //Step 4: Step Detector interrupt driven to INT1 pin, set bit INT1_FIFO_OVR
  errorAccumulator += pedometer.writeRegister( LSM6DS3_ACC_GYRO_INT1_CTRL, 0x10 );

  return errorAccumulator;
}
