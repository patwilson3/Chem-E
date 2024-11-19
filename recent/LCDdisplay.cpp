#include <liquidCrystal:k>

const int rs = 12, en = 11, d4 = 5, d5 = 4, d6 = 3, d7 = 2;
LiquidCrystal lcd(rs, en, d4, d5, d6, d7);

void setup() {
  //initalizes comms between arduino and rasp at 9600 baud, the max speed or transmission
  Serial.begin(9600);
  //setting up col and row of lcd
  lcd.begin(16,2);
  lcd.print("loading up the car...");
}

void loop() {
  //checks if theres any information to be read 
  if (Serial.available() > 0) {
    //reads until \n, built into raspi function
    String message = Serial.readStringUntil('\n');
    //clears whatever is written currently on the display
    lcd.clear();
    lcd.setCursor(0,0);
    //prints message
    lcd.print(message);
  }
}
