import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QWidget
from PyQt5.QtGui import QFont, QPainter, QColor, QPen, QPixmap
from PyQt5.QtCore import QTimer, Qt, QRectF

width = 800 #화면 해상도 넓이
height = 480 #화면 해상도 높이이
gauge_size = int(250 * width/800)
position = int(40 * width/800)

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
        span_angle = int(-self.value * 240/300 * 16)  # float을 int로 변환

        pen = QPen(QColor(int(255/300*self.value), 255 - int(255/300*self.value),0),int(10 * width/800))
        painter.setPen(pen)
        painter.drawArc(rect, start_angle, span_angle)

class RPMProgress(QWidget):
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
        span_angle = int(-self.value * 240/800 * 16)  # float을 int로 변환


        pen = QPen(QColor(int(255/800*self.value), 255 - int(255/800*self.value),0),int(10 * width/800))
        painter.setPen(pen)
        painter.drawArc(rect, start_angle, span_angle)

class ClusterWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Vehicle Cluster")
        self.setGeometry(0, 0, int(800*width/800), int(480 * height/480))  # 창 크기를 800x480으로 설정

        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        self.background_label = QLabel(self.central_widget)
        self.background_pixmap = QPixmap("back.png")  # 배경 이미지 경로 설정
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
        self.logo_pixmap = QPixmap("volk.png")  # 로고 이미지 경로 설정
        self.logo_label.setPixmap(self.logo_pixmap.scaled(int(150 * width/800), int(150 * width/800), Qt.KeepAspectRatio))
        self.logo_label.setAlignment(Qt.AlignCenter)
        self.logo_label.move(int(width - 150 * width/800) // 2, position)

        self.text_label = QLabel("P", self.central_widget) #주행 모드 표시
        self.text_label.setFont(QFont("Arial", int(100 * width/800)))
        self.text_label.setAlignment(Qt.AlignCenter)
        self.text_label.setStyleSheet('color:rgb(255,255,255)')
        self.text_label.resize(int(150 * width/800), int(150 * width/800))
        self.text_label.move(int(width - 150 * width/800) // 2, position + int(200 * height/480))

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_speed)
        self.timer.start(200)  # 200ms 마다 업데이트

        self.current_speed = 0
        self.current_rpm = 0

    def update_speed(self):
        # 여기서 실제 속도 값을 가져와서 업데이트합니다.
        self.current_speed = max(self.current_speed - 1, 0)
        self.speed_label.setText(f"{self.current_speed} km/h")
        self.speed_label.setStyleSheet(f'color:rgb({int(255/300*self.current_speed)},{255 - int(255/300*self.current_speed)},0)')
        self.speed_gauge.setValue(self.current_speed)  # 예시 값
        if self.current_rpm < 100:
            self.current_rpm = min(self.current_rpm + 20, 100)
        else:
            self.current_rpm = max(self.current_rpm - 10, 100)
        self.rpm_label.setText(f"{self.current_rpm/100} rpm")
        self.rpm_label.setStyleSheet(f'color:rgb({int(255/800*self.current_rpm)},{255 - int(255/800*self.current_rpm)},0)')
        self.rpm_multiple_label.setStyleSheet(f'color:rgb({int(255/800*self.current_rpm)},{255 - int(255/800*self.current_rpm)},0)')
        self.rpm_gauge.setValue(self.current_rpm)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()
        elif event.key() == Qt.Key_P and self.current_speed == 0:
            self.text_label.setStyleSheet('color:rgb(255,255,255)')
            self.update_logo("P")
        elif event.key() == Qt.Key_D and self.current_speed == 0:
            self.text_label.setStyleSheet('color:rgb(255,255,255)')
            self.update_logo("D")
        elif event.key() == Qt.Key_R and self.current_speed == 0:
            self.text_label.setStyleSheet('color:rgb(255,0,0)')
            self.update_logo("R")
        elif event.key() == Qt.Key_N and self.current_speed == 0:
            self.text_label.setStyleSheet('color:rgb(255,255,255)')
            self.update_logo("N")
        elif event.key() == Qt.Key_Up and (self.text_label.text() == "D" or self.text_label.text() == "R"):
            self.current_speed = min(self.current_speed + 3, 300)  # 속도를 10 증가, 최대 300
            if self.current_rpm < 200 or self.current_speed > 140:
                self.current_rpm = min(self.current_rpm + 20, 300)
            else:
                self.current_rpm = min(self.current_rpm + 1, 300)
            self.update_speed()
        elif event.key() == Qt.Key_Down:
            self.current_speed = max(self.current_speed - 1, 0)  # 속도를 10 감소, 최소 0
            self.current_rpm = max(self.current_rpm + 10, 100)
            self.update_speed()

    def update_logo(self, text):
        self.text_label.setText(text)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ClusterWindow()
    window.showFullScreen()  # 전체 화면 대신 창 크기를 800x480으로 설정
    sys.exit(app.exec_())