#include <SPI.h>
#include <WiFiNINA.h> // ESP8266에서 Wi-Fi 기능을 사용하기 위한 라이브러리 입니다.
#include <PubSubClient.h>

//For pedometer
#include "SparkFunLSM6DS3.h"
#include "Wire.h"

#define CLEAR_STEP      true
#define NOT_CLEAR_STEP  false

//Create a instance of class LSM6DS3
LSM6DS3 pedometer( I2C_MODE, 0x6A );  //I2C device address 0x6A

const char* ssid = "Roboin";
const char* password = "roboin1234";
const char* mqtt_server = "192.168.0.51";

WiFiClient espClient;
PubSubClient client(espClient);
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

void setup_wifi() {
  delay(10);
  WiFi.begin(ssid, password); // 앞서 설정한 ssid와 페스워드로 Wi-Fi에 연결합니다.
  while (WiFi.status() != WL_CONNECTED) { // 연결될 때 까지 0.5초 마다 Wi-Fi 연결상태를 확인합니다.
    delay(500);
  }
  randomSeed(micros()); // 렌덤 문자를 위한 렌덤 시드를 설정합니다.
}

void callback(char* topic, byte* payload, unsigned int length) {
  // Topic에 메시지가 도착하면 실행됨
}

void reconnect() {
  while (!client.connected()) {
    String clientId = "33IoTClient-"; // 클라이언트 ID를 설정합니다.
    clientId += String(random(0xffff), HEX); // 같은 이름을 가진 클라이언트가 발생하는것을 방지하기 위해, 렌덤 문자를 클라이언트 ID에 붙입니다.
    if (client.connect(clientId.c_str())) { // 앞서 설정한 클라이언트 ID로 연결합니다.
      // Publisher이기 때문에 Subscribe를 하지 않습니다.
    } else {
      delay(5000);
    }
  }
}

void setup() {
  setup_wifi();
  client.setServer(mqtt_server, 1883); // MQTT 서버에 연결합니다.
  client.setCallback(callback);
  Serial.begin(9600);
  if ( pedometer.begin() != 0 ) {
    Serial.println("Device error");
  }
  else {
    Serial.println("Device OK!");
  }

  //Configure LSM6DS3 as pedometer
  if ( 0 != config_pedometer(NOT_CLEAR_STEP) )
  {
    Serial.println("Configure pedometer fail!");
  }
  Serial.println("Success to Configure pedometer!");
  Serial.println("Initializing...");
  pixels.begin(); // This initializes the NeoPixel library.

  // Initialize sensor
  if (!particleSensor.begin(Wire, I2C_SPEED_FAST)) //Use default I2C port, 400kHz speed
  {
    Serial.println("MAX3010x was not found. Please check wiring/power. ");
    while (1);
  }
  Serial.println("Place your index finger on the sensor with steady pressure.");

  particleSensor.setup(); //Configure sensor with default settings
  particleSensor.setPulseAmplitudeRed(0x0A); //Turn Red LED to low to indicate sensor is running
  particleSensor.setPulseAmplitudeGreen(0); //Turn off Green LED
 }


void loop() {
  if (!client.connected()) {
    reconnect();
    Serial.println("reconnect");
  }
  uint8_t dataByte = 0;
  uint16_t stepCount = 0;

   long redValue = particleSensor.getRed();

  if (checkForBeat(redValue) == true)
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

    int r, g, b, w;
    int max_bright = 100; //value of maximum brightness, max 255. But you don't always want it at max :)
    float dd = 20; //change in BPM between color tones (blue->green->yellow->pink->red)
    float t1 = 60, t2, t3, t4; //t1 - "base" BPM, lower than t1 would be blue
    t2 = t1 + dd;
    t3 = t2 + dd;
    t4 = t3 + dd;

    if (beatAvg < t1) {
      r = 0;
      g = 0;
      b = max_bright, w = 0;
    }
    else if (beatAvg < t2) {
      r = 0;
      g = max_bright * (beatAvg - t1) / dd;
      b = max_bright - g, w = 0;
    }
    else if (beatAvg < t3) {
      r = max_bright * (beatAvg - t2) / dd;
      g = max_bright - r;
      b = r / 4, w = 0;
    }
    else if (beatAvg < t4) {
      r = max_bright;
      g = 0;
      b = max_bright / 2 - max_bright * (beatAvg - t3) / (2 * dd), w = 0;
    }
    else {
      r = max_bright;
      g = 0;
      b = 0, w = 0;
    }

    int on_pixels = (beatAvg + 5) / 20; //number of used LEDs: for 60 BPM, 3 LEDs will be on, for 120 - 6 etc
    for (int i = 0; i < NUMPIXELS; i++)
    {
      if (i < on_pixels) pixels.setPixelColor(i, pixels.Color(r, g, b, w));
      else pixels.setPixelColor(i, pixels.Color(0, 0, 0, 0)); //turn off all other LEDs
    }
    pixels.show();
    pedometer.readRegister(&dataByte, LSM6DS3_ACC_GYRO_STEP_COUNTER_H);
    stepCount = (dataByte << 8) & 0xFFFF;

    pedometer.readRegister(&dataByte, LSM6DS3_ACC_GYRO_STEP_COUNTER_L);
    stepCount |=  dataByte;

    Serial.print("Step: ");
    Serial.println(stepCount);
    Serial.print("RED=");
    Serial.print(redValue);
    Serial.print(", BPM=");
    Serial.print(beatsPerMinute);
    Serial.print(", Avg BPM=");
    Serial.print(beatAvg);

  if (redValue < 50000)
    Serial.print(" No finger?");
    Serial.println();

    client.loop();
    int bpm_len = sprintf(beatAvg_char, "%d", beatAvg);
    int stepCount_len = sprintf(stepCount_char, "%d", stepCount); //converting 만보기 수 (the float variable above) to 문자열
    //stepCount_str.toCharArray(stepCount, stepCount_str.length() + 1); //packaging up the data to publish to mqtt whoa...
    client.publish("StepCount", stepCount_char); // inTopic 토픽으로 메시지를 전송합니다.
    client.publish("BPM", beatAvg_char);
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
