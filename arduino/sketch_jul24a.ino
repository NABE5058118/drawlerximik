// Arduino код для управления шаговыми двигателями
// Использует 3x 28BYJ-48 с ULN2003 и half-stepping
// Оси: X, Y, Z (pen lift)

#define X_STEP_PIN 2
#define X_DIR_PIN  3
#define Y_STEP_PIN 4
#define Y_DIR_PIN  5
#define Z_STEP_PIN 8
#define Z_DIR_PIN  9

// Пины для лимитных выключателей
#define X_MIN_PIN 7
#define Y_MIN_PIN 6
#define Z_MIN_PIN 10

// Шаговые моторы
int motor_pins[][4] = {
  {X_STEP_PIN, X_DIR_PIN, 0, 0},
  {Y_STEP_PIN, Y_DIR_PIN, 0, 0},
  {Z_STEP_PIN, Z_DIR_PIN, 0, 0}
};

long current_steps[3] = {0, 0, 0};

void setup() {
  Serial.begin(115200);
  pinMode(X_STEP_PIN, OUTPUT);
  pinMode(X_DIR_PIN, OUTPUT);
  pinMode(Y_STEP_PIN, OUTPUT);
  pinMode(Y_DIR_PIN, OUTPUT);
  pinMode(Z_STEP_PIN, OUTPUT);
  pinMode(Z_DIR_PIN, OUTPUT);

  pinMode(X_MIN_PIN, INPUT_PULLUP);
  pinMode(Y_MIN_PIN, INPUT_PULLUP);
  pinMode(Z_MIN_PIN, INPUT_PULLUP);

  Serial.println("Ready");
}

void loop() {
  if (Serial.available()) {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();
    parse_command(cmd);
  }
}

void parse_command(String cmd) {
  if (cmd.startsWith("G0") || cmd.startsWith("G1")) {
    // Движение
    float x = 0, y = 0, z = 0;
    if (cmd.indexOf('X') != -1) x = cmd.substring(cmd.indexOf('X') + 1).toFloat();
    if (cmd.indexOf('Y') != -1) y = cmd.substring(cmd.indexOf('Y') + 1).toFloat();
    if (cmd.indexOf('Z') != -1) z = cmd.substring(cmd.indexOf('Z') + 1).toFloat();

    move_to(x, y, z);
  }
  else if (cmd.startsWith("G28")) {
    // Homing
    home_axes();
  }
  else if (cmd.startsWith("M84")) {
    // Disable motors
    disable_motors();
  }
  Serial.println("ok");
}

void move_to(float x, float y, float z) {
  // Тут логика для движения моторов
  // Упрощённый пример: шаги = координаты (в реальности нужна калибровка)
  long target_steps[3] = {(long)x, (long)y, (long)z};

  for (int i = 0; i < 3; i++) {
    long steps = target_steps[i] - current_steps[i];
    if (steps != 0) {
      digitalWrite(motor_pins[i][1], steps > 0 ? HIGH : LOW);
      for (long j = 0; j < abs(steps); j++) {
        digitalWrite(motor_pins[i][0], HIGH);
        delayMicroseconds(2000);  // 2ms delay
        digitalWrite(motor_pins[i][0], LOW);
        delayMicroseconds(2000);
      }
      current_steps[i] = target_steps[i];
    }
  }
}

void home_axes() {
  // Движение к лимитам
  // Упрощённый пример
  current_steps[0] = 0;
  current_steps[1] = 0;
  current_steps[2] = 0;
  Serial.println("Homed");
}

void disable_motors() {
  // Отключить моторы
  digitalWrite(X_STEP_PIN, LOW);
  digitalWrite(Y_STEP_PIN, LOW);
  digitalWrite(Z_STEP_PIN, LOW);
}