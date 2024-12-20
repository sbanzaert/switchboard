/*****
 * To do:
 * 
 * LOW LOW off
 * LOW HI  go!
 * HI  LOW go!
 * HI  HI  off
 * 
 */

#include <Adafruit_NeoPixel.h>
#ifdef __AVR__
  #include <avr/power.h>
#endif

const int ringPin = 4;
const int ringSize = 16;


int brightness[ringSize];
int chaseSpeed = 15;
char receivedChar;
boolean newdata = false;

//#define statePinA 4
//#define statePinB 5
Adafruit_NeoPixel strip = Adafruit_NeoPixel(ringSize, ringPin, NEO_GRB + NEO_KHZ800);



void setup() {

    strip.begin();
    strip.setBrightness(255);
    strip.show();
    Serial.begin(9600);
    // initialize brightness "gaussian"
    for (int i=0; i< ringSize; i++) {
        if (i==0 || i==4) brightness[i] = 30;
        else if (i==1 || 1==3) brightness[i] = 70;
        else if (i==2) brightness[i]=255;
        else brightness[i] = 0;
    }
}

void loop() {
    Serial.println("loop");
    blankStrip();
    int d;
    int animation[5] = {55, 45, 35, 25, 20}; // speed ramp
    recvOneChar();
    if(newdata) {
      newdata = false;
      Serial.println("newdata");
      if (receivedChar == 'y') {
        Serial.println("y received");
        receivedChar='x';
        d = 1;
//        for (int i=0; i< ringSize; i++){
//          strip.setPixelColor(i, strip.Color(255, 255, 255));
//          strip.show();
//          delay(500);
//          strip.setPixelColor(i, strip.Color(0,0,0));
//          strip.show();
//          delay(300);
//        }
//        strip.show();

        for (int i=0; i<5; i++) {
          strip.setBrightness(i*50+10);
          crankChase(animation[i], d);
        }
        while(true) {
          crankChase(chaseSpeed, d);
          recvOneChar();
          if (newdata == true) {
            if(receivedChar == 'n') break;
            }
          }
        
        newdata=false;
        for (int i=4; i>=0; i--) {
          strip.setBrightness(i*50+10);
          crankChase(animation[i], d);
        }   
      }
    }
    
}

void blankStrip() {
  for (int i=0; i<ringSize; i++) {
    strip.setPixelColor(i, 0);
  }
  strip.show();
}

// performs one lap of a chase sequence
void crankChase(uint8_t wait, bool dir) {
  for (int j=0; j<ringSize; j++) {
    for (int i=0; i<ringSize; i++) {
      strip.setPixelColor(i, strip.Color(brightness[i], brightness[i], brightness[i]));
    }
    if(dir) rotate_left(brightness, ringSize);
    else rotate_right(brightness, ringSize);
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

void recvOneChar() {
    if (Serial.available() > 0) {
        receivedChar = Serial.read();
        newdata = true;
    }
}

void showNewData() {
    if (newdata == true) {
        Serial.print("This just in ... ");
        Serial.println(receivedChar);
        newdata = false;
    }
}
