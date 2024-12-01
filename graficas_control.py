import serial
import time
import matplotlib.pyplot as plt
import threading
from collections import deque

# Configuración del puerto serial
try:
    ser = serial.Serial('COM10', 115200, timeout=2) 
    time.sleep(2)  # Espera para estabilizar la conexión
    print(f"Conexión establecida con {ser.portstr}")
except Exception as e:
    print(f"Error al abrir el puerto serial: {e}")
    exit()

# Variables de almacenamiento
val_deseados = deque(maxlen=100)  # Lista para almacenar los setpoints
val_actuales = deque(maxlen=100)  # Lista para almacenar los valores actuales
val_error = deque(maxlen=100)     # Lista para almacenar el error
val_salida = deque(maxlen=100)    # Lista para almacenar la salida PID
val_kp = deque(maxlen=100)        # Lista para almacenar Kp
val_ki = deque(maxlen=100)        # Lista para almacenar Ki
val_kd = deque(maxlen=100)        # Lista para almacenar Kd

# Configuración de la gráfica
fig, ax = plt.subplots(figsize=(10, 6))
linea1, = ax.plot([], [], label="Deseado (Setpoint)", color='g')
linea2, = ax.plot([], [], label="Actual", color='b')
linea3, = ax.plot([], [], label="Error", color='r')

ax.set_xlim(0, 100)
ax.set_xlabel("Tiempo (ms)")
ax.set_ylabel("Ángulo")
ax.legend(loc="upper left")
ax.text(0.5, 1.05, "Péndulo Hélice", ha='center', va='top', transform=ax.transAxes)

texto_deseado = ax.text(0.8, 0.95, f"Deseado: {0}", ha='center', va='top', transform=ax.transAxes, fontsize=10, color='green')
texto_actual = ax.text(0.8, 0.90, f"Actual: {0}", ha='center', va='top', transform=ax.transAxes, fontsize=10, color='blue')
texto_error = ax.text(0.8, 0.85, f"Error: 0", ha='center', va='top', transform=ax.transAxes, fontsize=10, color='red')
texto_kp = ax.text(0.8, 0.80, f"Kp: {0}", ha='center', va='top', transform=ax.transAxes, fontsize=10, color='purple')
texto_ki = ax.text(0.8, 0.75, f"Ki: {0}", ha='center', va='top', transform=ax.transAxes, fontsize=10, color='orange')
texto_kd = ax.text(0.8, 0.70, f"Kd: {0}", ha='center', va='top', transform=ax.transAxes, fontsize=10, color='brown')

# Función actualizar la gráfica
def actualizar_grafica():
    while True:
        if len(val_deseados) > 0: 
            linea1.set_xdata(range(len(val_deseados)))
            linea1.set_ydata(val_deseados)
            linea2.set_xdata(range(len(val_actuales)))
            linea2.set_ydata(val_actuales)
            linea3.set_xdata(range(len(val_error)))
            linea3.set_ydata(val_error)

            ax.set_xlim(0, len(val_deseados))
            ax.set_ylim(
                min(min(val_deseados), min(val_actuales), min(val_error), min(val_salida)) - 5,
                max(max(val_deseados), max(val_actuales), max(val_error), max(val_salida)) + 5
            )

            texto_deseado.set_text(f"Deseado: {val_deseados[-1]}")
            texto_actual.set_text(f"Actual: {val_actuales[-1]}")
            texto_error.set_text(f"Error: {val_error[-1]}")
            
            texto_kp.set_text(f"Kp: {val_kp[-1]}")
            texto_ki.set_text(f"Ki: {val_ki[-1]}")
            texto_kd.set_text(f"Kd: {val_kd[-1]}")

            plt.pause(0.05)

# Función para leer datos del puerto serial
def leer_datos():
    while True:
        try:
            line = ser.readline().decode('utf-8').strip()
            if line:
                print(f"Datos recibidos: {line}") 

                data = line.split(',')
                if len(data) == 6:
                    setpoint = float(data[0])   # Valor deseado (setpoint)
                    actual = float(data[1])     # Valor actual
                    output = float(data[2])     # Salida del PID
                    kp = float(data[3])         # Ganancia proporcional
                    ki = float(data[4])         # Ganancia integrativa
                    kd = float(data[5])         # Ganancia derivativa

                    val_deseados.append(setpoint)
                    val_actuales.append(actual)
                    val_error.append(setpoint - actual)
                    val_salida.append(output)
                    val_kp.append(kp)
                    val_ki.append(ki)
                    val_kd.append(kd)

        except Exception as e:
            print(f"Error al leer los datos: {e}")

thread_datos = threading.Thread(target=leer_datos, daemon=True)
thread_datos.start()

actualizar_grafica()