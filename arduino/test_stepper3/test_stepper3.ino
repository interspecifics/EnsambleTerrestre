/*
 * Interspecifics // Ensamble Terrestre
 * .mmxviii.iv.v.e.
 * 
 * steppers (mA1 mA2 mB1 mB2)
 * 1A: 21, 20, 22, 23
 * 1B: 15, 14, 16, 17
 * 2A: 4, 3, 5, 6
 * 2B: 9, 8, 10, 11
 */


#include <Stepper.h>
#include <Wire.h>
 
const int spr =200;  // steps per revolution
int nsteps_1A = 5;
int nsteps_1B = 10;
int nsteps_2A = 20;
int nsteps_2B = 40;

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
  Wire.begin(0x3A);
  Serial.begin(115200);
  S1A.setSpeed(100); S1B.setSpeed(100);
  S2A.setSpeed(100); S2B.setSpeed(100);
  pinMode(13, OUTPUT);
  Wire.onReceive(imprime); 
}
 

void loop(){
  while(true){
    // stepper 1A
    if (up_1A==true){
      S1A.step(2);
      dist_1A++;
      if(dist_1A>=nsteps_1A){
        up_1A = false;
      }
    }
    else {
      S1A.step(-2);
      dist_1A--;
      if (dist_1A<=0){
        up_1A = true;
      }
    }
    // stepper 1B
    if (up_1B==true){
      S1B.step(2);
      dist_1B++;
      if(dist_1B>=nsteps_1B){
        up_1B = false;
      }
    }
    else{
      S1B.step(-2);
      dist_1B--;
      if (dist_1B<=0){
        up_1B = true;
      }
    }
    
    // stepper 2A
    if (up_2A==true){
      S2A.step(2);
      dist_2A++;
      if(dist_2A>=nsteps_2A){
        up_2A = false;
      }
    }
    else {
      S2A.step(-2);
      dist_2A--;
      if (dist_2A<=0){
        up_2A = true;
      }
    }
    // stepper 2B
    if (up_2B==true){
      S2B.step(2);
      dist_2B++;
      if(dist_2B>=nsteps_2B){
        up_2B = false;
        digitalWrite(13, LOW);
      }
    }
    else{
      S2B.step(-2);
      dist_2B--;
      if (dist_2B<=0){
        up_2B = true;
        digitalWrite(13, HIGH);
      }
    }
  delay(5);
  }
}

void imprime(int cuantos){
  int x = Wire.read();    // receive byte as an integer
  Serial.print(cuantos);
  Serial.println(x);         // print the integer
}
