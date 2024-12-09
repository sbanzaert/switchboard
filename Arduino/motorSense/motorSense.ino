/*****
 * To do:
 * 
 * LOW LOW off
 * LOW HI  CW
 * HI  LOW CCW
 * HI  HI  off
 * 
 */

#include <Adafruit_NeoPixel.h>
#ifdef __AVR__
  #include <avr/power.h>
#endif

#define PIN 6
#define RING_SIZE 16
Adafruit_NeoPixel strip = Adafruit_NeoPixel(RING_SIZE, PIN, NEO_GRB + NEO_KHZ800);

int brightness[RING_SIZE];


#define statePinA 4;
#define statePinB 5; // motor feedback sent directly to level shifter


void setup() {
    pinMode(statePinA, INPUT);
    pinMode(statePinB, INPUT);
    strip.begin();
    strip.setBrightness(200);
    strip.show();

    // initialize brightness "gaussian"
    for (int i=0; i< RING_SIZE; i++) {
        if (i==0 || i==4) brightness[i] = 30;
        else if (i==1 || 1==3) brightness[i] = 70;
        else if (i==2) brightness[i]=255;
        else brightness[i] = 0;
    }
}

void loop() {
    blankStrip();
    int d;
    int animation[5] = {55, 45, 35, 25, 20}; // speed ramp
    if(digitalRead(statePinA) && !digitalRead(statePinB)) {
        d = 1;
        for (int i=0; i<5; i++) {
            strip.setBrightness(i*50+10);
            crankChase(animation[i], d);
        }
        while(digitalRead(statePinA) && !digitalRead(statePinB)) crankChase(chaseSpeed, d); // 1 not d originally
        for (int i=4; i>=0; i--) {
            strip.setBrightness(i*50+10);
            crankChase(animation[i], d);
        }
    }

}

void blankStrip() {
  for (int i=0; i<RING_SIZE; i++) {
    strip.setPixelColor(i, 0);
  }
  strip.show();
}

// performs one lap of a chase sequence
void crankChase(uint8_t wait, bool dir) {
  for (int j=0; j<RING_SIZE; j++) {
    for (int i=0; i<RING_SIZE; i++) {
      strip.setPixelColor(i, strip.Color(brightness[i], brightness[i], brightness[i]));
    }
    if(dir) rotate_left(brightness, RING_SIZE);
    else rotate_right(brightness, RING_SIZE);
    strip.show();
    delay(wait);
  }
  
}

void rotate_right(int* a, const int n){
  if (n<1) return;
  const int temp = a[n-1];
  for (int i=n-1;i>0;i--){
    a[i] = a[i-1];
  }
  a[0] = temp;
}

void rotate_left(int* a, const int n){
  if (n<1) return;
  const int temp = a[0];
  for (int i=0;i<n;i++){
    a[i] = a[i+1];
  }
  a[n-1] = temp;
}
