/*
 *    - i n t e r s p e c i f i c s -
 *        [ENSAMBLE TERRESTRE]
 *          e.mmxviii.iv.xix
 * 
 * steppers -mA1 mA2 mB1 mB2-   -NE-  -SW-
 * 1A: 21, 20, 22, 23           E-R   W-R
 * 1B: 15, 14, 16, 17           E-L   W-L
 * 2A: 4, 3, 5, 6               N-L   S-L
 * 2B: 9, 8, 10, 11             N-R   S-R
 * 
 * address_NE = 0x6A
 * address_SW = 0x3A
 */

#include <Stepper.h>
#include <Wire.h>
#define MICROSECONDS_PER_MICROSTEP   375
#define STEP_DELAY 375
#define SPR 200 

// invocaciones al tiempo
uint32_t curTime = 0;
uint32_t t0_1A = 0;
uint32_t t0_1B = 0;
uint32_t t0_2A = 0;
uint32_t t0_2B = 0;
// luego al movimiento
uint16_t c_1A, c_1B, c_2A, c_2B;
uint16_t delay_pre_1A, delay_pre_1B, delay_pre_2A, delay_pre_2B;
uint16_t maxdist_1A, maxdist_1B, maxdist_2A, maxdist_2B;
//uint8_t dist_1A, dist_1B, maxdist_2A, maxdist_2B;
uint16_t delay_post_1A, delay_post_1B, delay_post_2A, delay_post_2B;
// states= {0:stop, 1:up, 2:down, 3: stop, 4:waiting}
uint8_t st_1A, st_1B, st_2A, st_2B;
// y luego las dems
Stepper S1A(SPR, 21, 20, 22, 23);
Stepper S1B(SPR, 15, 14, 16, 17);
Stepper S2A(SPR, 4, 3, 5, 6);
Stepper S2B(SPR, 9, 8, 10, 11);
boolean st_led=false;
// data
char rData1;
char rData2;
char mag_1A, mag_1B, mag_2A, mag_2B;


void setup(){
  Wire.begin(0x3A);
  Serial.begin(115200);
  pinMode(13, OUTPUT);
  // received data
  rData1 = 0;
  rData2 = 0;
  mag_1A = rData1;
  mag_1B = rData1;
  mag_2A = rData2;
  mag_2B = rData2;
  // state vars
  st_1A = 0;
  st_1B = 0;
  st_2A = 0;
  st_2B = 0;
  // counters
  c_1A = 0;
  c_1B = 0;
  c_2A = 0;
  c_2B = 0;
  // st0
  delay_pre_1A = 0;
  delay_pre_1B = 0;
  delay_pre_2A = 0;
  delay_pre_2B = 0;
  // st1, st2
  maxdist_1A = 0;
  maxdist_1B = 0;
  maxdist_2A = 0;
  maxdist_2B = 0;
  // st3
  delay_post_1A = 0;
  delay_post_1B = 0;
  delay_post_2A = 0;
  delay_post_2B = 0;
  // others
  Wire.onReceive(catchData); 
  //Wire.onReceive(receivent); 

  //
  /*
  c_1A = 0;
  delay_pre_1A = int(constrain(map(rData2, 0, 20, 400, 20), 0, 400));
  maxdist_1A = int(constrain(map(rData1, 0, 20, 5, 30), 0, 30));
  delay_post_1A = int(constrain(map(rData2, 0, 20, 800, 20), 0, 800)); 
  c_1B = 0;
  delay_pre_1B = int(constrain(map(rData2, 0, 20, 800, 40), 0, 800));
  maxdist_1B = int(constrain(map(rData1, 0, 20, 5, 30), 0, 30));
  delay_post_1B = int(constrain(map(rData2, 0, 20, 1600, 40), 0, 1600));
  c_2A = 0;
  delay_pre_2A = int(constrain(map(rData1, 0, 20, 400, 20), 0, 400));
  maxdist_2A = int(constrain(map(rData2, 0, 20, 5, 30), 0, 30));
  delay_post_2A = int(constrain(map(rData1, 0, 20, 800, 20), 0, 800));
  c_2B = 0;
  delay_pre_2B = int(constrain(map(rData1, 0, 20, 800, 40), 0, 800));
  maxdist_2B = int(constrain(map(rData2, 0, 20, 5, 30), 0, 30));
  delay_post_2B = int(constrain(map(rData1, 0, 20, 1600, 40), 0, 1600));
  */
}

/*
 *DIRECTIONS:
 * 1A UP-, DW+
 * 1B UP+, DW-
 * 2A UP+, DW-
 * 2B UP-, DW+
 */

void loop(){
  curTime = micros();
  /*
  Serial.print(st_1A);
  Serial.print(":");
  Serial.print(c_1A);
  Serial.print(" // ");
  Serial.print(st_1B);
  Serial.print(":");
  Serial.println(c_1B); 
  */
  
  
  // // ---- ---- state machinery 1A
  if (st_1A == 0){
    if( (curTime - t0_1A)> MICROSECONDS_PER_MICROSTEP ){
      t0_1A = curTime;
      delayMicroseconds(STEP_DELAY);
      c_1A++;
      // enought delay? change state
      if (c_1A >= delay_pre_1A){
        c_1A = 0;
        if (mag_1A > 0){
          st_1A = 1;
          digitalWrite(13, HIGH);
        } else { 
          st_1A = 3;
        }
      }
    }
  } else if (st_1A == 1){
    S1A.setSpeed(20);
    if ( (curTime - t0_1A)> MICROSECONDS_PER_MICROSTEP ){
      t0_1A = curTime;
      // step and record
      S1A.step(-1);
      delayMicroseconds(STEP_DELAY);
      c_1A++;
      // enought up? change state
      if ( c_1A >= maxdist_1A ){
        st_1A = 2;
      }
    }
  } else if (st_1A == 2){
    S1A.setSpeed(20);
    if( (curTime - t0_1A)> MICROSECONDS_PER_MICROSTEP ){
      t0_1A = curTime;
      // step and record
      S1A.step(1);
      delayMicroseconds(STEP_DELAY);
      c_1A--;
      // enought down? change state
      if ( c_1A <= 0){
        st_1A = 3;
        c_1A = 0;
        digitalWrite(13, LOW);
      }
    }
  } else if(st_1A == 3){
    if( (curTime - t0_1A)> MICROSECONDS_PER_MICROSTEP ){
      t0_1A = curTime;
      delayMicroseconds(STEP_DELAY);
      c_1A++;
      // enought delay? change state
      if (c_1A >= delay_post_1A){
        st_1A = 4;
        c_1A = 0;
      }
    }
  } else if(st_1A == 4){
    // reassign
    if (rData1 == 0){
      mag_1A = 0;
      delay_pre_1A = 10;
      maxdist_1A = 0;
      delay_post_1A = 10;
    } else {
      mag_1A = rData1;
      delay_pre_1A = int(constrain(map(rData1, 0, 20, 400, 100), 0, 400));
      maxdist_1A = int(constrain(map(rData1, 0, 20, 3, 30), 0, 30));
      delay_post_1A = int(constrain(map(rData1, 0, 20, 800, 100), 0, 800));
    }
    c_1A = 0;
    st_1A = 0;  
  }
  
// ---- ---- state machinery 1B
  if (st_1B == 0){
    if( (curTime - t0_1B)> MICROSECONDS_PER_MICROSTEP ){
      t0_1B = curTime;
      delayMicroseconds(STEP_DELAY);
      c_1B++;
      // enought delay? change state
      if (c_1B >= delay_pre_1B){
        c_1B = 0;
        if (mag_1B>0){
          st_1B = 1;
          //digitalWrite(13, HIGH);
        } else { 
          st_1B = 3;
        }
      }

    }
  } else if (st_1B == 1){
    S1B.setSpeed(20);
    if ( (curTime - t0_1B)> MICROSECONDS_PER_MICROSTEP ){
      t0_1B = curTime;
      // step and record
      S1B.step(1);
      delayMicroseconds(STEP_DELAY);
      c_1B++;
      // enought up? change state
      if ( c_1B >= maxdist_1B ){
        st_1B = 2;
      }
    }
  } else if (st_1B == 2){
    S1B.setSpeed(20);
    if( (curTime - t0_1B)> MICROSECONDS_PER_MICROSTEP){
      t0_1B = curTime;
      // step and record
      S1B.step(-1);
      delayMicroseconds(STEP_DELAY);
      c_1B--;
      // enought down? change state
      if ( c_1B <= 0){
        st_1B = 3;
        c_1B = 0;
      }
    }
  } else if(st_1B == 3){
    if( (curTime - t0_1B)> MICROSECONDS_PER_MICROSTEP ){
      t0_1B = curTime;
      delayMicroseconds(STEP_DELAY);
      c_1B++;
      // enought delay? change state
      if (c_1B >= delay_post_1B){
        st_1B = 4;
        c_1B = 0;
      }
    }
  } else if(st_1B == 4){
    // reassign
    if (rData1 == 0){
      mag_1B = 0;
      delay_pre_1B = 10;
      maxdist_1B = 0;
      delay_post_1B = 10;
    } else {
      mag_1B = rData1;
      delay_pre_1B = int(constrain(map(rData1, 0, 20, 800, 50), 0, 800));
      maxdist_1B = int(constrain(map(rData1, 0, 20, 3, 30), 0, 30));
      delay_post_1B = int(constrain(map(rData1, 0, 20, 1600, 50), 0, 1600));
    }
    c_1B = 0;
    st_1B = 0;  
  }


    // // ---- ---- state machinery 2A
  if (st_2A == 0){
    if( (curTime - t0_2A)> MICROSECONDS_PER_MICROSTEP ){
      t0_2A = curTime;
      delayMicroseconds(STEP_DELAY);
      c_2A++;
      // enought delay? change state
      if (c_2A >= delay_pre_2A){
        c_2A = 0;
        if (mag_2A > 0){
          st_2A = 1;
          //digitalWrite(13, HIGH);
        } else { 
          st_2A = 3;
        }
      }
    }
  } else if (st_2A == 1){
    S2A.setSpeed(20);
    if ( (curTime - t0_2A)> MICROSECONDS_PER_MICROSTEP ){
      t0_2A = curTime;
      // step and record
      S2A.step(1);
      delayMicroseconds(STEP_DELAY);
      c_2A++;
      // enought up? change state
      if ( c_2A >= maxdist_2A ){
        st_2A = 2;
      }
    }
  } else if (st_2A == 2){
    S2A.setSpeed(20);
    if( (curTime - t0_2A)> MICROSECONDS_PER_MICROSTEP ){
      t0_2A = curTime;
      // step and record
      S2A.step(-1);
      delayMicroseconds(STEP_DELAY);
      c_2A--;
      // enought down? change state
      if ( c_2A <= 0){
        st_2A = 3;
        c_2A = 0;
        //digitalWrite(13, LOW);
      }
    }
  } else if(st_2A == 3){
    if( (curTime - t0_2A)> MICROSECONDS_PER_MICROSTEP ){
      t0_2A = curTime;
      delayMicroseconds(STEP_DELAY);
      c_2A++;
      // enought delay? change state
      if (c_2A >= delay_post_2A){
        st_2A = 4;
        c_2A = 0;
      }
    }
  } else if(st_2A == 4){
    // reassign
    if (rData2 == 0){
      mag_2A = 0;
      delay_pre_2A = 10;
      maxdist_2A = 0;
      delay_post_2A = 10;
    } else {
      mag_2A = rData2;
      delay_pre_2A = int(constrain(map(rData2, 0, 20, 500, 50), 0, 500));
      maxdist_2A = int(constrain(map(rData2, 0, 20, 3, 20), 0, 20));
      delay_post_2A = int(constrain(map(rData2, 0, 20, 600, 50), 0, 600));
    }
    c_2A = 0;
    st_2A = 0;  
  }
  
// ---- ---- state machinery 2B
  if (st_2B == 0){
    if( (curTime - t0_2B)> MICROSECONDS_PER_MICROSTEP ){
      t0_2B = curTime;
      delayMicroseconds(STEP_DELAY);
      c_2B++;
      // enought delay? change state
      if (c_2B >= delay_pre_2B){
        c_2B = 0;
        if (mag_2B>0){
          st_2B = 1;
          //digitalWrite(13, HIGH);
        } else { 
          st_2B = 3;
        }
      }

    }
  } else if (st_2B == 1){
    S2B.setSpeed(20);
    if ( (curTime - t0_2B)> MICROSECONDS_PER_MICROSTEP ){
      t0_2B = curTime;
      // step and record
      S2B.step(-1);
      delayMicroseconds(STEP_DELAY);
      c_2B++;
      // enought up? change state
      if ( c_2B >= maxdist_2B ){
        st_2B = 2;
      }
    }
  } else if (st_2B == 2){
    S2B.setSpeed(20);
    if( (curTime - t0_2B)> MICROSECONDS_PER_MICROSTEP){
      t0_2B = curTime;
      // step and record
      S2B.step(1);
      delayMicroseconds(STEP_DELAY);
      c_2B--;
      // enought down? change state
      if ( c_2B <= 0){
        st_2B = 3;
        c_2B = 0;
      }
    }
  } else if(st_2B == 3){
    if( (curTime - t0_2B)> MICROSECONDS_PER_MICROSTEP ){
      t0_2B = curTime;
      delayMicroseconds(STEP_DELAY);
      c_2B++;
      // enought delay? change state
      if (c_2B >= delay_post_2B){
        st_2B = 4;
        c_2B = 0;
      }
    }
  } else if(st_2B == 4){
    // reassign
    if (rData2 == 0){
      delay_pre_2B = 10;
      maxdist_2B = 0;
      delay_post_2B = 10;
      mag_2B = 0;
    } else {
      delay_pre_2B = int(constrain(map(rData2, 0, 20, 900, 100), 0, 900));
      maxdist_2B = int(constrain(map(rData2, 0, 20, 3, 20), 0, 20));
      delay_post_2B = int(constrain(map(rData2, 0, 20, 1000, 100), 0, 1000));
      mag_2B = rData2;
    }
    c_2B = 0;
    st_2B = 0;  
  }
} // end LOOP


void receivent(int nbytes) {
  rData1 = Wire.read();
  rData2 = Wire.read();
  rData1 = rData1;
  rData2 = rData2;
  Serial.print(rData1);
  Serial.print(rData2);
  Serial.println("");
}


void catchData(int howMany) {
  int ii = 0;
  while (0 < Wire.available()) {
    char c = Wire.read();
    //Serial.print(c);
    if (ii==1) rData1 = c-65;
    else if (ii==2) rData2 = c-65;
    ii++;
  }
  Serial.print(byte(rData1));
  Serial.print(byte(rData2));
  Serial.println("");
}

