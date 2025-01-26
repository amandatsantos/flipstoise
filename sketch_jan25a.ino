const int encoderPinSW = 3; // Pino do botão (switch) do KY-040
const int potentiometerPin = A0; // Pino analógico para o potenciômetro

void setup() {
  Serial.begin(9600); // Inicializa a comunicação serial
  pinMode(encoderPinSW, INPUT_PULLUP); // Configura o pino do botão como entrada
}

void loop() {
  int potentiometerValue = analogRead(potentiometerPin); // Lê o valor do potenciômetro
  int buttonState = digitalRead(encoderPinSW); // Lê o estado do botão

  // Envia o valor do potenciômetro e o estado do botão
  Serial.print("Potenciômetro:");
  Serial.print(potentiometerValue);
  Serial.print(", Botão:");
  Serial.println(buttonState);

  delay(100); // Pequeno delay para evitar excesso de leituras
}
