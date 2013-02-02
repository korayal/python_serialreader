#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
ZetCode PyQt4 tutorial

In this example, we create a bit
more complicated window layout using
the QGridLayout manager.

author: Jan Bodnar
website: zetcode.com
last edited: October 2011
"""

import sys
import time
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import serial
import serial.tools.list_ports

def main():
    app = QApplication(sys.argv)
    global ex
    ex = Arabirim()
    sys.exit(app.exec_())


class ArabirimThread(QThread):

    def __init__(self, parent=None):
        QThread.__init__(self, parent)
        self.emit(SIGNAL("SystemText(QString)"), "{0}\r\n".format("Background Thread Init"))
        self.exiting = False

    def __del__(self):
        self.wait()

    def run(self):
        #print("Entering SerialLoop")
        self.exiting = False;
        self.emit(SIGNAL("SystemText(QString)"), "{0}\r\n".format("--- CONNECTED ---"))
        while not self.exiting:
            if ex.ser.isOpen:
                time.sleep(0.1)
                incomingSerial = ex.ser.read(ex.ser.inWaiting())
                incomingLines = incomingSerial.split("\r\n")
                for line in incomingLines:
                    if line:
                        self.emit(SIGNAL("IncomingSerialText(QString)"), "{0}\r\n".format(line))
        ex.ser.close()
        self.emit(SIGNAL("SystemText(QString)"), "{0}\r\n".format("--- DISCONNECTED ---"))

    def stop(self):
        self.exiting = True


class Arabirim(QWidget):
    def __init__(self, parent=None):
        super(Arabirim, self).__init__()
        self.thread = ArabirimThread()
        self.initUI()

    def initUI(self):

        self.connect(self.thread, SIGNAL("IncomingSerialText(QString)"),  self.IncomingSerialText)
        self.connect(self.thread, SIGNAL("SystemText(QString)"),  self.SystemText)

        self.PortName = QLabel('Port')
        self.BaudRate = QLabel('Baud Rate')
        self.PortNameEdit = QLineEdit("/dev/ttyUSB0")
        self.BaudRateEdit = QLineEdit("115200")

        self.PortList = QComboBox(self)

        PortListItems = serial.tools.list_ports.comports()
        for item in PortListItems:
            if item[2] != 'n/a':
                self.PortList.addItem(item[0])

        self.connectbutton = QPushButton("&Connect")
        self.connectbutton.clicked.connect(self.onConnectClicked)

        self.TextEdit = QTextEdit()
        self.TextDocument = QTextDocument(self.TextEdit)

        self.TextCursor = QTextCursor(self.TextEdit.document())

        self.CommandBox = QLineEdit()
        self.CommandBox.returnPressed.connect(self.onSendClicked)
        self.SendButton = QPushButton("&Send")
        self.SendButton.clicked.connect(self.onSendClicked)

        grid = QGridLayout()
        grid.setSpacing(10)

        grid.addWidget(self.PortName, 1, 0)
        grid.addWidget(self.PortList, 1, 1)

        grid.addWidget(self.BaudRate, 2, 0)
        grid.addWidget(self.BaudRateEdit, 2, 1)

        grid.addWidget(self.connectbutton, 1, 3, 2, 1)

        grid.addWidget(self.TextEdit, 3, 0, 5, 4)

        grid.addWidget(self.CommandBox, 9, 0, 1, 3)
        grid.addWidget(self.SendButton, 9, 3)

        self.CommandBox.setEnabled(False)
        self.SendButton.setEnabled(False)

        self.setLayout(grid)

        self.setGeometry(300, 300, 350, 300)
        self.setWindowTitle('Serial Port Tool')
        self.show()

    def onConnectClicked(self):
        self.connectbutton.clicked.disconnect(self.onConnectClicked)
        self.connectbutton.clicked.connect(self.onDisconnectClicked)
        self.connectbutton.setText("&Disconnect")
        portname = unicode(self.PortList.currentText())
        baudrate = int(self.BaudRateEdit.text())
        print("Connecting to port {0} {1}".format(portname, baudrate))
        global serialopen
        serialopen = True
        self.ser = serial.Serial(portname, baudrate)
        if not self.ser.isOpen:
            self.ser.open()
        if self.ser.isOpen:
            self.thread.start()
            self.CommandBox.setEnabled(True)
            self.SendButton.setEnabled(True)

    def onDisconnectClicked(self):
        self.connectbutton.clicked.disconnect(self.onDisconnectClicked)
        self.connectbutton.clicked.connect(self.onConnectClicked)
        self.connectbutton.setText("&Connect")
        if self.ser.isOpen:
            serialopen = False
            self.CommandBox.setEnabled(False)
            self.SendButton.setEnabled(False)
            self.thread.stop()

    def onSendClicked(self):
        command = "{0}\r\n".format(str(self.CommandBox.text()))
        #print(command)
        if self.ser.isOpen:
            self.OutgoingSerialText(command)
            self.ser.write(command)

    def IncomingSerialText(self, line):
        blockformat = QTextBlockFormat()
        textformat = QTextCharFormat()
        textformat.setProperty(QTextFormat.ForegroundBrush, QVariant(QBrush(QColor(Qt.red))))
        self.TextCursor.setBlockFormat(blockformat)
        self.TextCursor.setCharFormat(textformat)
        self.TextCursor.insertText(line)
        self.TextEdit.moveCursor(QTextCursor.End)

    def OutgoingSerialText(self, line):
        blockformat = QTextBlockFormat()
        textformat = QTextCharFormat()
        textformat.setProperty(QTextFormat.ForegroundBrush, QVariant(QBrush(QColor(Qt.blue))))
        self.TextCursor.setBlockFormat(blockformat)
        self.TextCursor.setCharFormat(textformat)
        self.TextCursor.insertText(line)
        self.TextEdit.moveCursor(QTextCursor.End)

    def SystemText(self, line):
        blockformat = QTextBlockFormat()
        textformat = QTextCharFormat()
        textformat.setProperty(QTextFormat.ForegroundBrush, QVariant(QBrush(QColor(Qt.black))))
        self.TextCursor.setBlockFormat(blockformat)
        self.TextCursor.setCharFormat(textformat)
        self.TextCursor.insertText(line)
        self.TextEdit.moveCursor(QTextCursor.End)



if __name__ == '__main__':
    main()
