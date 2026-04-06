#include "DFRobot_DF1201S.h"
#include "SoftwareSerial.h"

SoftwareSerial mySoftwareSerial(2, 3); // RX, TX
DFRobot_DF1201S dfplayer;

int currentVol = 5;
bool isPaused = false;

void printHelp() {
  Serial.println("--- Controls ---");
  Serial.println("  n = Next track");
  Serial.println("  b = Back (previous track)");
  Serial.println("  p = Pause / Resume");
  Serial.println("  + = Volume up");
  Serial.println("  - = Volume down");
  Serial.println("  1-9 = Play track number");
  Serial.println("----------------");
}

void setup() {
  Serial.begin(115200);
  mySoftwareSerial.begin(115200);

  while (!dfplayer.begin(mySoftwareSerial)) {
    Serial.println("Initialization failed. Check wiring!");
    delay(1000);
  }

  Serial.println("DFPlayer Pro Online");
  dfplayer.setVol(currentVol);
  dfplayer.switchFunction(dfplayer.MUSIC);
  dfplayer.playFileNum(1);
  Serial.println("Playing track 1");
  printHelp();
}

void loop() {
  if (Serial.available()) {
    char cmd = Serial.read();

    switch (cmd) {
      case 'n':
        dfplayer.next();
        isPaused = false;
        Serial.println("Next track");
        break;

      case 'b':
        dfplayer.last();
        isPaused = false;
        Serial.println("Previous track");
        break;

      case 'p':
        if (isPaused) {
          dfplayer.start();
          isPaused = false;
          Serial.println("Resumed");
        } else {
          dfplayer.pause();
          isPaused = true;
          Serial.println("Paused");
        }
        break;

      case '+':
        if (currentVol < 30) {
          currentVol++;
          dfplayer.setVol(currentVol);
          Serial.print("Volume: ");
          Serial.println(currentVol);
        } else {
          Serial.println("Volume at max (30)");
        }
        break;

      case '-':
        if (currentVol > 0) {
          currentVol--;
          dfplayer.setVol(currentVol);
          Serial.print("Volume: ");
          Serial.println(currentVol);
        } else {
          Serial.println("Volume at min (0)");
        }
        break;

      case '1': case '2': case '3': case '4': case '5':
      case '6': case '7': case '8': case '9':
        int trackNum = cmd - '0'; // convert char to int
        dfplayer.playFileNum(trackNum);
        isPaused = false;
        Serial.print("Playing track ");
        Serial.println(trackNum);
        break;

      case 'h':
        printHelp();
        break;
    }
  }
}
