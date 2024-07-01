//This code is written for arduino nano

#include <Arduino.h>
#include <HCSR04.h>
#include <Servo.h>

//pins
#define MLn A1
#define MLp A2
#define MRp A3
#define MRn A4
#define LASER_PIN 11
#define SERVO_PIN 10

// delays and threshold
#define US_SAMPLE_DELAY 10
#define ERR_THRESHOLD  5// cm
#define OBSTACLE_THRESHOLD 15 //cm
#define ROVER_SPEED 23.5 // cm/s  #toupdate
#define TURN_DELAY 1000 // for complete 90deg rotation #toupdate 

// to update
#define KP 2 // #toupdate
#define ALIGN_DELAY 300 // #toupdate ms time to align by moving forward after stering adjustments 
#define SERVO_STEP_DELAY 50 //ms

uint8_t OFF[] ={0,0,0,0}; // driver inputs 1,2,3,4
uint8_t FORWARD[] ={0,1,0,1};
uint8_t REVERSE[] ={1,0,1,0};
uint8_t TURN_LEFT[] ={1,0,0,1};
uint8_t TURN_RIGHT[] ={0,1,1,0};
uint8_t STEER_LEFT[]={0,0,0,1};
uint8_t STEER_RIGHT[]={0,1,0,0};

HCSR04 us_right(6,7);
HCSR04 us_left(8,9);
HCSR04 us_front(4,5);

// l, f, r 0-free 1-obstacle
uint8_t LFR[]={0,0,0};
uint8_t LF[]={0,0,1};
uint8_t  LR[]={0,1,0};
uint8_t L[]={0,1,1};
uint8_t FR[]={1,0,0};
uint8_t F[]={1,0,1};
uint8_t R[]={1,1,0};
uint8_t O[]={1,1,1};

Servo lsrservo;

void get_surround_distance();
void motorWrite(uint8_t* vals);
void exec_cmd(String cmd);
void go_straight();
void go_junction(uint8_t* junction);
void laser_sweep();


void setup() {
    Serial.begin(19200);
    Serial.setTimeout(20);
    pinMode(MLp, OUTPUT);
    pinMode(MLn, OUTPUT);
    pinMode(MRp, OUTPUT);
    pinMode(MRn, OUTPUT);
    pinMode(LASER_PIN, OUTPUT);
    lsrservo.attach(SERVO_PIN);

}

String cmd;
void loop() {
    if (Serial.available()>0){
        cmd=Serial.readStringUntil(';');
        exec_cmd(cmd);
    }
    delay(100);
}

uint8_t dists[3] = {0,0,0};
void get_surround_distance(){
    /*
    for (uint8_t i = 0; i < 10; i++) // take 10 samples 
    {
        dists[0] += us_left.dist();
        dists[2] += us_right.dist();
        delay(US_SAMPLE_DELAY);
    }
    dists[0]/=10;
    dists[2]/=10;
    */
    delay(60);
    dists[0]=us_left.dist();
    delay(60);
    dists[1]=us_front.dist();
    delay(60);
    dists[2]=us_right.dist();
    
    // Serial.print(dists[1]);
    // Serial.print(dists[2]);
    return;
}

void motorWrite(uint8_t* vals){ // duration in ms
    digitalWrite(MLn, vals[0]);
    digitalWrite(MLp, vals[1]);
    digitalWrite(MRp, vals[2]);
    digitalWrite(MRn, vals[3]);
    
}

void exec_cmd(String cmd){

    if (cmd=="STP")
        motorWrite(OFF);
    else if (cmd=="FWD")
        motorWrite(FORWARD);
    else if (cmd=="STR"){ 
        Serial.print("DONE;");
        go_straight();
        return;
    }
    else if (cmd=="REV")
        motorWrite(REVERSE);
    else if (cmd=="LFT"){
        Serial.print("DONE;");
        motorWrite(TURN_LEFT);
        return;
    } else if(cmd=="RGT"){
        Serial.print("DONE;");
        motorWrite(TURN_RIGHT);
        return;
    } else if(cmd=="UTRN"){
        Serial.print("DONE;");
        motorWrite(TURN_RIGHT);
        return;
    }else if(cmd=="GOLFR")
        go_junction(LFR);
    else if(cmd=="GOLR")
        go_junction(LR);
    else if(cmd=="GOR")
        go_junction(R);
    else if(cmd=="GOL")
        go_junction(L);
    else if(cmd=="GOFR")
        go_junction(FR);
    else if(cmd=="GOLF")
        go_junction(LF);
    else if(cmd=="GOO")
        go_junction(O);
    else if(cmd=="LSR"){
        Serial.print("DONE;");
        laser_sweep();
        return;
    } else if(cmd=="NOP")
        ;
    else{
        Serial.print("ERR;WRONGCMD:"+cmd+";");
        return;
    }
    Serial.print("DONE;"); // for blocking commands
    
}

void go_straight(){  // blocking function 
    do{
        get_surround_distance();
        uint8_t err=dists[0]-dists[2]; // + means more in right - means more in left
        uint8_t steer_delay;
        if (abs(err)>ERR_THRESHOLD){
            steer_delay=KP*abs(err);
            if (err>0){
                motorWrite(STEER_LEFT);
                delay(steer_delay);
            } else {
                motorWrite(STEER_RIGHT);
                delay(steer_delay);
            }
            motorWrite(FORWARD);
            delay(ALIGN_DELAY);
        }
    }while(!Serial.available());
}

void go_junction(uint8_t* junction){
    Serial.println(String(junction[0])+""+junction[1]+""+String(junction[2]));
    uint8_t current_junction[3];
    do{
    motorWrite(FORWARD);
    delay(100);
    get_surround_distance();
    for(uint8_t i=0; i<3; i++)
        current_junction[i]=(dists[i]<OBSTACLE_THRESHOLD)?1:0;
    
    Serial.println(String(current_junction[0])+" "+String(current_junction[1])+" "+String(current_junction[2]));
    }while(!(current_junction[0]==junction[0] && current_junction[1]==junction[1] && current_junction[2]==junction[2]) && !Serial.available());
    delay(200);
    motorWrite(OFF);
}

// takes 3 sec for 30 to 90 deg
void laser_sweep(){
    digitalWrite(LASER_PIN, HIGH);
    for(uint8_t i=40; i<110; i++){ // initial angle is 30
        lsrservo.write(i);
        delay(SERVO_STEP_DELAY);
    }
    digitalWrite(LASER_PIN, LOW);
    lsrservo.write(30);
}
