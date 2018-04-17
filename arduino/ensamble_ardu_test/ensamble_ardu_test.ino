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

boolean st_led=false;

void setup(){
  Wire.begin(0x3A);
  Serial.begin(115200);
  pinMode(13, OUTPUT);
  Wire.onReceive(receivent); 
}
 

void loop(){
}

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


