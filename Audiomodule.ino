#include "DFRobot_DF1201S.h"
#include "SoftwareSerial.h"

SoftwareSerial mySoftwareSerial(2, 3);
DFRobot_DF1201S dfplayer;

void setup() {
  Serial.begin(115200);
  mySoftwareSerial.begin(115200);

  while (!dfplayer.begin(mySoftwareSerial)) {
    Serial.println("Init failed!");
    delay(1000);
  }

  dfplayer.setVol(15);
  dfplayer.switchFunction(dfplayer.MUSIC);
  dfplayer.setPlayMode(dfplayer.SINGLE);
  Serial.println("READY");
}

void loop() {
  if (Serial.available()) {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();

    if (cmd.startsWith("PLAY:")) {
      int track = cmd.substring(5).toInt();
      if (track >= 1 && track <= 14) {
        dfplayer.playFileNum(track);
        delay(500); // let player start before querying duration
        uint16_t duration = dfplayer.getTotalTime();
        Serial.print("DURATION:");
        Serial.println(duration);
      }
    } else if (cmd == "PAUSE") {
      dfplayer.pause();
    } else if (cmd == "RESUME") {
      dfplayer.start();
    } else if (cmd.startsWith("VOL:")) {
      int vol = cmd.substring(4).toInt();
      dfplayer.setVol(constrain(vol, 0, 30));
    }
  }
}
