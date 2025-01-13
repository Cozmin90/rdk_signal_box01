// Define the pin numbers for the sensors
const int sensor1Pin = 2;
const int sensor2Pin = 3;
const int photodiodePin = A0;  // Analog pin for the photodiode

const int debounceDelay = 20;        // 50 ms debounce delay
const int photodiodeThreshold = 20;  // Threshold for photodiode changes

// Variables to store the sensor values and their previous states
int sensor1Value = 0;
int sensor2Value = 0;
int photodiodeValue = 0;
int prevSensor1Value = -1;
int prevSensor2Value = -1;
int prevPhotodiodeValue = -1;

unsigned long lastDebounceTime1 = 0;
unsigned long lastDebounceTime2 = 0;

void setup() {
  // Initialize the serial communication at 115200 baud rate
  Serial.begin(9600);

  // Set the sensor pins as input
  pinMode(sensor1Pin, INPUT);
  pinMode(sensor2Pin, INPUT);
}

void loop() {
  // Read the current sensor values
  int currentSensor1 = digitalRead(sensor1Pin);
  int currentSensor2 = digitalRead(sensor2Pin);
  int currentPhotodiode = analogRead(photodiodePin);  // Read photodiode value
  unsigned long currentTime = millis();

  // Debounce sensor 1
  if (currentSensor1 != prevSensor1Value && (currentTime - lastDebounceTime1) > debounceDelay) {
    lastDebounceTime1 = currentTime;
    prevSensor1Value = currentSensor1;
    sendSensorData("IO1", currentSensor1);
  }

  // Debounce sensor 2
  if (currentSensor2 != prevSensor2Value && (currentTime - lastDebounceTime2) > debounceDelay) {
    lastDebounceTime2 = currentTime;
    prevSensor2Value = currentSensor2;
    sendSensorData("IO2", currentSensor2);
  }

  // Send photodiode data only if it changes significantly (above the threshold)
  if (abs(currentPhotodiode - prevPhotodiodeValue) > photodiodeThreshold) {  // Threshold to reduce noise
    prevPhotodiodeValue = currentPhotodiode;
    sendSensorData("PD", currentPhotodiode);
  }
}

void sendSensorData(String sensor, int value) {
  // Include the timestamp (millis) when sending data
  unsigned long timestamp = millis();
  String data = sensor + "_" + String(value) + "_" + String(timestamp);
  Serial.println(data);
}
