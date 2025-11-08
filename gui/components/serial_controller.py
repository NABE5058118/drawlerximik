import serial
import serial.tools.list_ports
from utils.config import AppConfig

class SerialController:
    def __init__(self, app):
        self.app = app
        self.serial_conn = None
    
    def update_ports(self):
        """Обновляет список доступных COM-портов"""
        ports = [port.device for port in serial.tools.list_ports.comports()]
        self.app.port_combo['values'] = ports
        if ports:
            self.app.port_var.set(ports[0])
            self.app.log(f"Найдены порты: {', '.join(ports)}")
        else:
            self.app.port_var.set("")
            self.app.log("COM-порты не найдены")
    
    def connect_printer(self):
        """Подключается к принтеру"""
        port = self.app.port_var.get()
        if not port:
            self.app.show_error("Ошибка", "Выберите COM-порт")
            return

        try:
            self.serial_conn = serial.Serial(port, 115200, timeout=10)
            self.app.connection_status.config(text=f"✅ Подключено к {port}", 
                                            fg=AppConfig.COLORS["accent_green"])
            self.app.log(f"Успешное подключение к {port}")
            self.app.show_info("Успех", f"Подключено к принтеру на порту {port}")
        except Exception as e:
            self.app.log(f"Ошибка подключения: {e}")
            self.app.connection_status.config(text="❌ Ошибка подключения", 
                                            fg=AppConfig.COLORS["accent_red"])
            self.app.show_error("Ошибка", f"Не удалось подключиться: {e}")
    
    def send_gcode_to_printer(self, gcode_path):
        """Отправляет G-code на принтер"""
        if not self.serial_conn or not self.serial_conn.is_open:
            self.app.show_error("Ошибка", "Не подключено к принтеру")
            return False

        self.app.progress.start()
        try:
            with open(gcode_path, 'r') as f:
                gcode_lines = [line.strip() for line in f if line.strip()]

            total_lines = len(gcode_lines)
            sent_lines = 0

            for line in gcode_lines:
                if not line or line.startswith(';'):
                    continue

                self.serial_conn.write((line + '\n').encode())
                self.app.log(f"> {line}")

                # Ждём ответ от принтера
                response = self.serial_conn.readline().decode().strip()
                if response:
                    self.app.log(f"< {response}")

                sent_lines += 1
                if sent_lines % 10 == 0:
                    self.app.update_status(f"Отправка: {sent_lines}/{total_lines}")

            self.app.log("✓ G-code успешно отправлен на принтер!")
            self.app.update_status("G-code отправлен на принтер")
            return True

        except Exception as e:
            self.app.log(f"✗ Ошибка отправки: {e}")
            return False
        finally:
            self.app.progress.stop()