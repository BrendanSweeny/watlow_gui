from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtGui import QPainter, QColor, QBrush
import sys

class LEDWidget(QWidget):

    def __init__(self, parent):
        super().__init__(parent)

        self.red = QColor(200, 0, 0)
        self.green = QColor(0, 200, 0)
        self.state = False
        self.show()

    def paintEvent(self, e):
        qp = QPainter()
        qp.begin(self)
        self.drawRectangles(qp)
        qp.end()

    def drawRectangles(self, qp):
        if self.state:
            qp.setBrush(self.green)
        else:
            qp.setBrush(self.red)
        qp.drawRect(0, 0, 10, 20)

    def changeState(self, val):
        self.state = val
        self.update()


if __name__ == '__main__':

    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())
