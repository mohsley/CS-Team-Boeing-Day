const int BUFFER_SIZE = 64;
char inputBuffer[BUFFER_SIZE];
int bufferIndex = 0;

void setup() {
  Serial.begin(115200);
  while (!Serial) {
    ; // wait for serial port to connect. Needed for native USB port only
  }
  Serial.println("READY");
}

void loop() {
  while (Serial.available() > 0) {
    char inChar = (char)Serial.read();
    if (inChar == '\n') {
      inputBuffer[bufferIndex] = '\0';
      processBuffer();
      bufferIndex = 0;
      Serial.println("READY");
    } else if (bufferIndex < BUFFER_SIZE - 1) {
      inputBuffer[bufferIndex++] = inChar;
    }
  }
}

void processBuffer() {
  Serial.print("Received: ");
  Serial.println(inputBuffer);
  
  char* token = strtok(inputBuffer, ",");
  int index = 0;
  while (token != NULL && index < 12) {  // Assuming 12 values (4 legs * 3 angles each)
    int value = atoi(token);
    Serial.print("Value ");
    Serial.print(index);
    Serial.print(": ");
    Serial.println(value);
    token = strtok(NULL, ",");
    index++;
  }
  Serial.println("---");
}
