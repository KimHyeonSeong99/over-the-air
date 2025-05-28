import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QWidget
from PyQt5.QtGui import QFont, QPainter, QColor, QPen, QPixmap
from PyQt5.QtCore import QTimer, Qt, QRectF
import can

width = 800
height = 480
gauge_size = int(250 * width/800)
position = int(40 * width/800)
program_dir = os.path.dirname(os.path.abspath(__file__))

class SpeedProgress(QWidget):
	def __init__(self, parent=None):
		super().__init__(parent)
		self.value = 0
		self.setFixedSize(gauge_size,gauge_size)

	def setValue(self, value):
		self.value = value
		self.update()

	def paintEvent(self, event):
		painter = QPainter(self)
		painter.setRenderHint(QPainter.Antialiasing)

		rect = QRectF(5*width/800, 5*width/800, gauge_size - 10*width/800, gauge_size - 10*width/800)
		start_angle = 210 * 16
		span_angle = int(-self.value * 240/300 * 16)

		pen = QPen(QColor(int(255/300*self.value), 255 - int(255/300*self.value),0),int(10 * width/800))
		painter.setPen(pen)
		painter.drawArc(rect, start_angle, span_angle)
		
class RPMProgress(QWidget):
	def __init__(self, parent=None):
		super().__init__(parent)
		self.value = 0
		self.setFixedSize(gauge_size, gauge_size)

	def setValue(self, value):
		self.value = min(value, 8000)  # Ensure value does not exceed 8000
		self.update()

	def paintEvent(self, event):
		painter = QPainter(self)
		painter.setRenderHint(QPainter.Antialiasing)

		rect = QRectF(5 * width / 800, 5 * width / 800, gauge_size - 10 * width / 800, gauge_size - 10 * width / 800)
		start_angle = 210 * 16
		span_angle = int(-self.value * 240 / 8000 * 16)  # Scale based on max RPM of 8000

		pen = QPen(QColor(int(255 / 8000 * self.value), 255 - int(255 / 8000 * self.value), 0), int(10 * width / 800))
		painter.setPen(pen)
		painter.drawArc(rect, start_angle, span_angle)

		
class ClusterWindow(QMainWindow):
	def __init__(self):
		super().__init__()
		self.setWindowTitle("Vehicle Cluster")
		self.setGeometry(0, 0, int(800*width/800), int(480 * height/480))

		self.central_widget = QWidget(self)
		self.setCentralWidget(self.central_widget)

		self.background_label = QLabel(self.central_widget)
		self.background_pixmap = QPixmap(os.path.join(program_dir, "image/back.png"))
		self.background_label.setPixmap(self.background_pixmap.scaled(int(800 * width/800), int(480 * height/480)))
		self.background_label.setGeometry(0, 0, int(800 * width/800), int(480 * height/480))

		self.speed_gauge = SpeedProgress(self.central_widget)
		self.speed_gauge.move(position, position)
		self.speed_label = QLabel("0 km/h", self.central_widget)
		self.speed_label.setFont(QFont("Arial", int(25 * width/800)))
		self.speed_label.setAlignment(Qt.AlignCenter)
		self.speed_label.resize(gauge_size, gauge_size)
		self.speed_label.move(position, position)

		self.rpm_gauge = RPMProgress(self.central_widget)
		self.rpm_gauge.move(width - position - gauge_size, position)
		self.rpm_label = QLabel("0 rpm", self.central_widget)
		self.rpm_multiple_label = QLabel("x1000",self.central_widget)
		self.rpm_label.setFont(QFont("Arial", int(25 * width/800)))
		self.rpm_label.setAlignment(Qt.AlignCenter)
		self.rpm_label.resize(gauge_size, gauge_size)
		self.rpm_label.move(width - position - gauge_size, position)
		self.rpm_multiple_label.setFont(QFont("Arial", int(10 * width/800)))
		self.rpm_multiple_label.setAlignment(Qt.AlignCenter)
		self.rpm_multiple_label.resize(gauge_size, gauge_size)
		self.rpm_multiple_label.move(width - position - gauge_size, position - int(15 * width/800))

		self.logo_label = QLabel(self.central_widget)
		self.logo_pixmap = QPixmap(os.path.join(program_dir, "image/volk.png"))
		self.logo_label.setPixmap(self.logo_pixmap.scaled(int(150 * width/800), int(150 * width/800), Qt.KeepAspectRatio))
		self.logo_label.setAlignment(Qt.AlignCenter)
		self.logo_label.move(int(width - 150 * width/800) // 2, position)

		self.text_label = QLabel("P", self.central_widget)
		self.text_label.setFont(QFont("Arial", int(100 * width/800)))
		self.text_label.setAlignment(Qt.AlignCenter)
		self.text_label.setStyleSheet('color:rgb(255,255,255)')
		self.text_label.resize(int(150 * width/800), int(150 * width/800))
		self.text_label.move(int(width - 150 * width/800) // 2, position + int(200 * height/480))

		self.timer = QTimer(self)
		self.timer.timeout.connect(self.update_infomation)
		self.timer.start(200)

		self.current_speed = 0
		self.current_rpm = 0
		try:
			self.can = can.interface.Bus(channel=f'can0', bustype='socketcan')
		except can.CanError as e:
			print(f"Error initializing CAN interface: {e}")
			sys.exit(1)
		
		self.setFocusPolicy(Qt.StrongFocus)  # 메인 윈도우가 키 이벤트를 받도록 설정
		self.central_widget.setFocusPolicy(Qt.NoFocus)  # (선택) central widget이 포커스를 가로채지 않도록
		
	def update_infomation(self):
		self.can_receive_event()  # Fetch CAN data before updating the UI
		self.speed_label.setText(f"{self.current_speed} km/h")
		self.speed_label.setStyleSheet(f'color:rgb({int(255/300*self.current_speed)},{255 - int(255/300*self.current_speed)},0)')
		self.speed_gauge.setValue(self.current_speed)

		# Updated: Show RPM with a maximum of 8000
		self.rpm_label.setText(f"{(self.current_rpm / 1000):.1f} rpm")
		self.rpm_label.setStyleSheet(f'color:rgb({int(255/8000*self.current_rpm)},{255 - int(255/8000*self.current_rpm)},0)')
		self.rpm_multiple_label.setStyleSheet(f'color:rgb({int(255/8000*self.current_rpm)},{255 - int(255/8000*self.current_rpm)},0)')
		self.rpm_gauge.setValue(self.current_rpm)
	
	def keyPressEvent(self, event):
		if event.key() == Qt.Key_Escape:  # Check if the pressed key is ESC
			self.close()  # Close the application
			 
	def can_receive_event(self):
		try:
			msg = self.can.recv()  # Non-blocking or short timeout
			if msg is not None:
				can_id = msg.arbitration_id
				if can_id == 99:
					if msg.data[1] == 1:
						self.text_label.setStyleSheet('color:rgb(255,255,255)')
						self.update_logo("P")
					elif msg.data[1] == 2:
						self.text_label.setStyleSheet('color:rgb(255,255,255)')
						self.update_logo("D")
					elif msg.data[1] == 3:
						self.text_label.setStyleSheet('color:rgb(255,0,0)')
						self.update_logo("R")
					elif msg.data[1] == 4:
						self.text_label.setStyleSheet('color:rgb(255,255,255)')
						self.update_logo("N")
				elif can_id == 100:
					 # Corrected: Combine bytes manually if RPM spans two bytes
					self.current_rpm = min((msg.data[6] << 8) | msg.data[7], 8000)
				elif can_id == 101:
					self.current_speed = msg.data[5]  # Corrected indexing for speed
		except Exception as e:
			print(f"CAN receive error: {e}")  # Log any errors
		
	def update_logo(self, text):
		self.text_label.setText(text)
	 
if __name__ == "__main__":
	app = QApplication(sys.argv)
	window = ClusterWindow()
	window.show()  # Changed from showFullScreen() to show()
	sys.exit(app.exec_())
