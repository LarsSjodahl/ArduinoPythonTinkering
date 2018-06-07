#include <OneWire.h>
#include <Servo.h>

// http://www.pjrc.com/teensy/td_libs_OneWire.html
// The DallasTemperature library can do all this work for you!
// http://milesburton.com/Dallas_Temperature_Control_Library

OneWire  ds(10);  // on pin 10 (a 1.0k-4.7K pull-UP resistor is necessary)
Servo myServo; // creates a servo object
int togglePin = 13;
int rightPin  = 12;
int leftPin   = 11;
int inByte = 0;


void setup(void) {
  Serial.begin(9600);
  pinMode(togglePin, OUTPUT);
  pinMode(rightPin, OUTPUT);
  pinMode(leftPin, OUTPUT);
  myServo.attach(9); // attaches the servo on pin 9 to the servo object
  // servos can only be controlled by pins 3, 5, 6, 9, 10 or 11, which have PWM
}

void loop(void) {
  if (Serial.available() > 0) {
    // get incoming byte:
    inByte = Serial.read();
    delay(10);
    if(inByte=='1')
      digitalWrite(togglePin, HIGH);
    else if(inByte=='0')
      digitalWrite(togglePin, LOW);
    else if(inByte=='R'){      
      digitalWrite(rightPin, HIGH);
      digitalWrite(leftPin, LOW);
    }
    else if(inByte=='L'){
      digitalWrite(leftPin, HIGH);
      digitalWrite(rightPin, LOW);
    }
    else if(inByte=='S'){
      digitalWrite(rightPin, LOW);
      digitalWrite(leftPin, LOW);
    }
    // feel free to add something for the servo using a variable "angle":
    // myservo.write(angle)
    
  }
  byte i;
  byte present = 0;
  byte type_s;
  byte data[12];
  byte addr[8];
  float celsius, fahrenheit;
  
  if ( !ds.search(addr)) {
   // Serial.println("No more addresses.");
   // Serial.println();
    ds.reset_search();
    delay(250);
    return;
  }
  
  if (OneWire::crc8(addr, 7) != addr[7]) {
      Serial.println("CRC is not valid!");
      return;
  }
  ds.reset();
  ds.select(addr);
  ds.write(0x44, 1);        // start conversion, with parasite power on at the end
  
  delay(800);     // maybe 750ms is enough, maybe not
  
  present = ds.reset(); //Lars: what the heck? What is it that reset() returns? Old lingering data?
  ds.select(addr);    
  ds.write(0xBE);         // Read Scratchpad
  for ( i = 0; i < 9; i++) {           // we need 9 bytes
    data[i] = ds.read();
  }

  // Convert the data to actual temperature
  // because the result is a 16 bit signed integer, it should
  // be stored to an "int16_t" type, which is always 16 bits
  // even when compiled on a 32 bit processor.
  int16_t raw = (data[1] << 8) | data[0];
  if (type_s) {
    raw = raw << 3; // 9 bit resolution default
    if (data[7] == 0x10) {
      // "count remain" gives full 12 bit resolution
      raw = (raw & 0xFFF0) + 12 - data[6];
    }
  } else {
    byte cfg = (data[4] & 0x60);
    // at lower res, the low bits are undefined, so let's zero them
    if (cfg == 0x00) raw = raw & ~7;  // 9 bit resolution, 93.75 ms
    else if (cfg == 0x20) raw = raw & ~3; // 10 bit res, 187.5 ms
    else if (cfg == 0x40) raw = raw & ~1; // 11 bit res, 375 ms
    //// default is 12 bit resolution, 750 ms conversion time
  }
  celsius = (float)raw / 16.0;
  fahrenheit = celsius * 1.8 + 32.0;
  Serial.print(celsius);
  Serial.println();
}
// End of program
/*
Lars own comments: Put a 4700 Ohm (pull-up) resistor  (1 kOhm also worked just fine)
between positive power (red) and the signal line (yellow). 
The DS18b20 sensor can handle -55 to +125 C, but I'm not 
so sure about the connector cable. It might get nasty from +125C.

You can have many sensors on the same three wires, and they all
have individual adresses that are discovered by this example program. (unless commented out)

Resolution is 0.0625 degrees C, but precision is only +/- 0.5 C, 
so I guess you can measure differences well, but for precision 
you need to calibrate at your baseline temperature and see the local error.
*/

