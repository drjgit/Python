# This Python file uses the following encoding: utf-8
import sys
import os

from PySide2.QtWidgets import QApplication, QWidget
from PySide2.QtCore import QFile, QBitArray, Qt, QObject, Signal, Slot
from PySide2.QtUiTools import QUiLoader
from PySide2.QtGui import QBitmap, QPainter, QPixmap, QTextCursor
from PySide2 import QtCore, QtXml

from WebAns import AutoAns, EmittingStream
from Configure import ConfigManger


class LoginView(QWidget):
    def __init__(self):
        super(LoginView, self).__init__()
        self.load_ui()
        self.load_qss()
        self.load_config()
        self.redirect_stream()
        self.setFixedSize(820,350)

    def load_ui(self):
        loader = QUiLoader()
        path = os.path.join(os.path.dirname(__file__), "form.ui")
        ui_file = QFile(path)
        ui_file.open(QFile.ReadOnly)
        self.ui = loader.load(ui_file, self)
        ui_file.close()

    def load_qss(self):
        path = os.path.join(os.path.dirname(__file__), "form.qss")
        qss_file = QFile(path)
        qss_file.open(QFile.ReadOnly)
        if (qss_file.isOpen()):
            styleArray = qss_file.readAll()
            qss_file.close()
            self.setStyleSheet(str(styleArray, encoding='utf-8'))

    def load_config(self):
        self.cfg = ConfigManger()

    def init_widget(self):
        self.init_web()
        self.set_style()
        self.set_parameter()
        self.set_connect()

    def set_parameter(self):
        self.ui.LnEdName.setText(self.cfg.get_username())
        self.ui.LnEdPasswd.setText(self.cfg.get_password())
        self.ui.BtnLogin.setEnabled(False)
        self.ui.BtnLogout.setEnabled(False)
        self.ui.LabPinImg.setText('验证码加载中...')
    
    def set_connect(self):
        self.ui.BtnLogin.clicked.connect(self.on_btn_login)
        self.ui.BtnLogout.clicked.connect(self.on_btn_logout)
        self.web.vercode_signal.connect(self.show_vercode)
        # 此方法暂时不能用
        # QObject.connect(self.web, QtCore.SIGNAL('vercode_signal(bytes)'), self, QtCore.SLOT('update_vercode(bytes)'))

    def set_style(self):
        # 设置widget为圆角，QSS中radius属性无法生效
        # self.bmp = QBitmap(410,350)  #这里将window size引入，否则无效果！
        # self.bmp.fill()
        # self.Painter = QPainter(self.bmp)
        # self.Painter.setPen(Qt.NoPen)
        # self.Painter.setBrush(Qt.black)
        # self.Painter.setRenderHint(QPainter.Antialiasing)
        # self.Painter.drawRoundedRect(self.bmp.rect(), 10, 10) #倒边角为10px
        # self.setMask(self.bmp)  #切记将self.bmp Mark到window
        # self.setAttribute(Qt.WA_StyledBackground)
        # self.setWindowFlags(Qt.FramelessWindowHint)
        self.ui.LabLine.setObjectName('Line')
        self.ui.LabSplitLn.setObjectName('Line')

    def on_btn_login(self): 
        name = self.ui.LnEdName.text()
        passwd = self.ui.LnEdPasswd.text()
        pin = self.ui.LnEdPin.text()
        if (name == '' or passwd == '' or pin == ''):
            return None
        self.web.set_user_info(name, passwd, pin)
        self.ui.BtnLogin.setEnabled(False)

    def on_btn_logout(self):
        if (self.web.is_run()):
            self.web.stops()
        self.ui.BtnLogin.setEnabled(True)

    def output_written(self, text):
        # self.ui.PrintBrow.clear()
        cursor = self.ui.PrintBrow.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.insertText(text)
        self.ui.PrintBrow.setTextCursor(cursor)
        self.ui.PrintBrow.ensureCursorVisible()

    def init_web(self):
        self.web = AutoAns()

    def redirect_stream(self):
        out_emit_stream = EmittingStream()
        out_emit_stream.text_written.connect(self.output_written)
        sys.stdout = out_emit_stream
        err_emit_stream = EmittingStream()
        err_emit_stream.text_written.connect(self.output_written)
        sys.stderr = err_emit_stream

    @Slot()
    def show_vercode(self, img_data):
        if (img_data==None):
            return None
        img = QPixmap()
        img.loadFromData(img_data)
        self.ui.LabPinImg.setText('')
        self.ui.LabPinImg.setPixmap(img)
        self.ui.BtnLogin.setEnabled(True)
        self.ui.BtnLogout.setEnabled(True)

    @Slot()
    def update_vercode(self, img_data):
        if (img_data==None):
            return None
        img = QPixmap()
        img.loadFromData(img_data)
        self.ui.LabPinImg.setPixmap(img)

    def start_ans(self):
        self.web.starts()


if __name__ == "__main__":
    app = QApplication([])
    widget = LoginView()
    widget.init_widget()
    widget.show()
    widget.start_ans()
    sys.exit(app.exec_())
