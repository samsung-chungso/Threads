import serial
import struct
import threading
import time
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib.animation import FuncAnimation

class JDamr:
    def __init__(self, com="COM11", baud_rate=9600):
        # 시리얼 포트 초기화
        self.ser = serial.Serial(com, baud_rate, timeout=1)
        if self.ser.is_open:
            print("JDamr serial port opened!")
        else:
            print("Can't open JDamr serial port!")
        time.sleep(2)

        # 데이터 저장용 리스트
        self.yaw_data = []
        self.motor_data = []
        self.time_data = []
        self.start_time = time.time()
        self.running = True

    def receive_data(self):
        self.ser.reset_input_buffer()
        while self.running:
            if self.ser.in_waiting > 0:
                head = self.ser.read(1)
                if head == b'\xf5':  # Start byte
                    length = self.ser.read(1)
                    if length == b'\x06':  # 총 6바이트 (Yaw: 4바이트 + motorOutput: 2바이트)
                        payload = self.ser.read(6)
                        yaw, motor_output = struct.unpack('f h', payload)  # Yaw(float) + motorOutput(int)
                        self.yaw_data.append(yaw)
                        self.motor_data.append(motor_output)
                        current_time = time.time() - self.start_time
                        self.time_data.append(current_time)  # 시간 추가

    def send_pid_values(self, Kp, Ki, Kd):
        # PID 값을 아두이노로 전송
        pid_data = f"{Kp} {Ki} {Kd}\n".encode('utf-8')
        self.ser.write(pid_data)
        print(f"Sent PID values: Kp={Kp}, Ki={Ki}, Kd={Kd}")

    def stop(self):
        self.running = False
        self.ser.close()

def plot_yaw_motor(jdamr, fig, ax1, ax2):
    # Yaw 플롯
    ax1.set_ylim(-180, 180)
    ax1.set_xlim(0, 10)
    line1, = ax1.plot([], [], lw=2)

    # motorOutput 플롯
    ax2.set_ylim(-255, 255)
    ax2.set_xlim(0, 10)
    line2, = ax2.plot([], [], lw=2)

    def init():
        line1.set_data([], [])
        line2.set_data([], [])
        return line1, line2

    def update(frame):
        if len(jdamr.time_data) > 0:
            line1.set_data(jdamr.time_data, jdamr.yaw_data)
            line2.set_data(jdamr.time_data, jdamr.motor_data)
            if jdamr.time_data[-1] > 10:
                ax1.set_xlim(jdamr.time_data[0], jdamr.time_data[-1] + 1)
                ax2.set_xlim(jdamr.time_data[0], jdamr.time_data[-1] + 1)
        return line1, line2

    ani = FuncAnimation(fig, update, init_func=init, blit=True, interval=100)
    return ani

def start_gui(jdamr):
    root = tk.Tk()
    root.title("PID Controller and Plot")

    # Matplotlib Figure 설정
    fig = Figure(figsize=(8, 6), dpi=100)
    ax1 = fig.add_subplot(211)
    ax1.set_title("Yaw Plot")
    ax2 = fig.add_subplot(212)
    ax2.set_title("Motor Output Plot")
    
    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.get_tk_widget().grid(row=0, column=0, rowspan=4)

    # 실시간 플롯 시작
    ani = plot_yaw_motor(jdamr, fig, ax1, ax2)

    # PID 입력창과 버튼
    tk.Label(root, text="P").grid(row=0, column=1)
    tk.Label(root, text="I").grid(row=1, column=1)
    tk.Label(root, text="D").grid(row=2, column=1)

    p_entry = tk.Entry(root)
    p_entry.grid(row=0, column=2)
    i_entry = tk.Entry(root)
    i_entry.grid(row=1, column=2)
    d_entry = tk.Entry(root)
    d_entry.grid(row=2, column=2)

    def send_pid():
        try:
            Kp = float(p_entry.get())
            Ki = float(i_entry.get())
            Kd = float(d_entry.get())
            jdamr.send_pid_values(Kp, Ki, Kd)
        except ValueError:
            print("Invalid PID values. Please enter valid numbers.")

    enter_button = tk.Button(root, text="Enter", command=send_pid)
    enter_button.grid(row=3, column=2)

    root.mainloop()

if __name__ == '__main__':
    com = 'COM11'  # 아두이노가 연결된 COM 포트
    jdamr = JDamr(com)

    # 시리얼 데이터 수신 쓰레드 시작
    receive_thread = threading.Thread(target=jdamr.receive_data)
    receive_thread.start()

    # GUI 시작
    start_gui(jdamr)

    # 종료 처리
    jdamr.stop()
    receive_thread.join()