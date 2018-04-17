/*
 * Interspecifics // Ensamble Terrestre
 * .mmxviii.iv.v.e.
 * 
 * steppers -mA1 mA2 mB1 mB2-   -NE-  -SW-
 * 1A: 21, 20, 22, 23           E-R   W-R
 * 1B: 15, 14, 16, 17           E-L   W-L
 * 2A: 4, 3, 5, 6               N-L   S-L
 * 2B: 9, 8, 10, 11             N-R   S-R
 *
 * ---------------------------
 * 
 * 1. cachar datos i2c
 * 2. parse msg
 * 3. set beat
 *    veloc, 
 *    dur (pause between vals)
 */


#include <Stepper.h>
#include <Wire.h>
 
const int spr =200;  // steps per revolution
int nsteps_1A = 10;
int nsteps_1B = 10;
int nsteps_2A = 10;
int nsteps_2B = 10;

boolean up_1A = true;
boolean up_1B = true;
boolean up_2A = true;
boolean up_2B = true;

int dist_1A = 0;
int dist_1B = 0;
int dist_2A = 0;
int dist_2B = 0;

Stepper S1A(spr, 21, 20, 22, 23);
Stepper S1B(spr, 15, 14, 16, 17);
Stepper S2A(spr, 4, 3, 5, 6);
Stepper S2B(spr, 9, 8, 10, 11);

boolean st_led=false;

void setup(){
  Wire.begin(0x6A);
  Serial.begin(115200);
  S1A.setSpeed(20); S1B.setSpeed(20);
  S2A.setSpeed(20); S2B.setSpeed(20);
  pinMode(13, OUTPUT);
  Wire.onReceive(receivent); 
  //Wire.onReceive(catch_n_parse);
}
 

void loop(){
  //go up L
  S1A.setSpeed(20); S1B.setSpeed(20);
  S2A.setSpeed(20); S2B.setSpeed(20);
  for (int i=0; i<nsteps_1A; i++){
    S1B.step(2);
    S2A.step(2);
    delayMicroseconds(350);
  }
  delay(50);
  // go down L
  S1A.setSpeed(50); S1B.setSpeed(50);
  S2A.setSpeed(50); S2B.setSpeed(50);
  for (int i=0; i<nsteps_1A; i++){
    S1B.step(-2);
    S2A.step(-2);
    delayMicroseconds(350);
  }
  delay(1000);
  //go up R
  S1A.setSpeed(20); S1B.setSpeed(20);
  S2A.setSpeed(20); S2B.setSpeed(20);
  for (int i=0; i<nsteps_1A; i++){
    S1A.step(-2);
    S2B.step(-2);
    delayMicroseconds(350);
  }
  delay(50);
  // go down R
  S1A.setSpeed(50); S1B.setSpeed(50);
  S2A.setSpeed(50); S2B.setSpeed(50);
  for (int i=0; i<nsteps_1A; i++){
    S1A.step(2);
    S2B.step(2);
    delayMicroseconds(350);
  }
  delay(1000);}

void imprime(int cuantos){
  for (int i=0; i<cuantos; i++){
  //while (Wire.available()>0){
    int x = Wire.read();    // receive byte as an integer
    Serial.print(char(x));
  }
  Serial.println("");         // print the integer
}


void receivent(int howMany) {
  while (0 < Wire.available()) { // loop through all but the last
    char c = Wire.read(); // receive byte as a character
    Serial.print(c);         // print the character
  }
  Serial.println(" ");
}



// examples: N#0F#AA
void catch_n_parse(int sz){
  char data[20];
  byte i = 0;
  byte c = 0;
  while (i < sz){
    char car = Wire.read();    // receive byte as char
    if (car=='\n'){
      // end of record, parse data[]
      char* com = strtok(data, ",");
      while(com != 0){
        char* sep = strchr(com, ':');
        if (sep != 0){
          *sep = 0;
          int v1 =atoi(com);
          ++sep;
          int v2 = atoi(sep);
          Serial.print(v1);
          // then print
          Serial.print(":");
          Serial.println(v2);
        }
        com = strtok(NULL, "&");
      }
      // then clean array
      data[i] = NULL;
      i = 0;
    } else {
      data[i] = car;
      i++;
      data[i] = '\0';          // keep the string null terminated
    }
  }
}
