const int EMG_PIN = A0;

const unsigned long BAUD_RATE = 115200;
const unsigned long SAMPLE_INTERVAL_US = 2000;
const unsigned long ACQUISITION_TIME_S = 5;

const unsigned long SAMPLE_RATE_HZ =
    1000000UL / SAMPLE_INTERVAL_US;

const unsigned long TOTAL_SAMPLES =
    SAMPLE_RATE_HZ * ACQUISITION_TIME_S;

unsigned long nextSampleTime = 0;
unsigned long sampleCount = 0;

void setup() {
  Serial.begin(BAUD_RATE);

  delay(1000);

  nextSampleTime = micros();

  Serial.print("SAMPLE_RATE_HZ=");
  Serial.println(SAMPLE_RATE_HZ);

  Serial.print("TOTAL_SAMPLES=");
  Serial.println(TOTAL_SAMPLES);

  Serial.println("START");
}

void loop() {
  if (sampleCount >= TOTAL_SAMPLES) {
    return;
  }

  unsigned long currentTime = micros();

  if (currentTime >= nextSampleTime) {
    int sensorValue = analogRead(EMG_PIN);

    Serial.println(sensorValue);

    sampleCount++;
    nextSampleTime += SAMPLE_INTERVAL_US;
  }
}
