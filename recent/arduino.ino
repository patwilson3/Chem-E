#include <Adafruit_NeoPixel.h>
#include <Adafruit_DS3502.h>

#define PIN 6
#define NUMPIXELS_PER_STRIP 8
#define NUM_STRIPS 4
#define NUMPIXELS (NUMPIXELS_PER_STRIP * NUM_STRIPS)

Adafruit_DS3502 ds3502 = Adafruit_DS3502();
Adafruit_NeoPixel pixels(NUMPIXELS, PIN, NEO_GRB + NEO_KHZ800);
float brightness_factor = 0.3;

void setup() {

  Serial.begin(9600);
  while (!Serial) { delay(1); }

  if (!ds3502.begin()) {
    Serial.println("Couldn't find DS3502 chip");
    while (1);
  }
  Serial.println("Found DS3502 chip");

  ds3502.setWiper(63);

  pixels.setBrightness(int(255 * brightness_factor));
  pixels.begin();

}

void loop() {
  pixels.clear();

  // Loop through each LED in all strips
  for (int strip = 0; strip < NUM_STRIPS; strip++) {
    for (int pixel = 0; pixel < NUMPIXELS_PER_STRIP; pixel++) {
      int pixelIndex = strip * NUMPIXELS_PER_STRIP + pixel;
      pixels.setPixelColor(pixelIndex, pixels.Color(255, 255, 255));
    }
  }
  
  pixels.show();
}
