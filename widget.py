import sys
from pathlib import Path
from threading import Thread

from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QSpacerItem, QTextEdit
from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QMessageBox, QDesktopWidget, QFileDialog
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QStandardPaths, QSize, QFileInfo

from ota_from_target_files import startBuildingIncrementalOta

first_tf_path  = ""
second_tf_path = ""

class UiWidget(QWidget):

    def __init__(self):

        super().__init__()

        self.init()

    def init(self):

        self.first_tf_button = QPushButton("First TF")
        self.first_tf_button.setFixedSize(QSize(100, 40))
        self.first_tf_button.clicked.connect(self.showDialogFirst)
        self.first_tf_label = QLabel("")

        self.second_tf_button = QPushButton("Second TF")
        self.second_tf_button.setFixedSize(QSize(100, 40))
        self.second_tf_button.clicked.connect(self.showDialogSecond)
        self.second_tf_label = QLabel("")

        hbox1 = QHBoxLayout()
        hbox1.addWidget(self.first_tf_button)
        hbox1.addWidget(self.first_tf_label)

        hbox2 = QHBoxLayout()
        hbox2.addWidget(self.second_tf_button)
        hbox2.addWidget(self.second_tf_label)

        self.text_field = QTextEdit()

        vbox1 = QVBoxLayout()
        vbox1.addLayout(hbox1)
        vbox1.addLayout(hbox2)
        vbox1.addWidget(self.text_field)

        self.start_button = QPushButton("Start")
        self.start_button.clicked.connect(self.startButtonClicked)
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.close)

        hbox3 = QHBoxLayout()
        hbox3.addStretch(1)
        hbox3.addWidget(self.start_button)
        hbox3.addWidget(self.cancel_button)

        main_vbox = QVBoxLayout()
        main_vbox.addLayout(vbox1)
        main_vbox.addLayout(hbox3)

        self.setLayout(main_vbox)
        self.center()

    def center(self):

        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())


    def closeEvent(self, event):

        reply = QMessageBox.question(self, 'Message',
            "Are you sure to quit?", QMessageBox.Yes |
            QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

    def showDialogFirst(self):

        temp = QFileDialog.getOpenFileName(self, 'Choose target file archive',
               QStandardPaths.writableLocation(QStandardPaths.HomeLocation), "Zip archive (*.zip)")[0]

        if temp:
            global first_tf_path
            first_tf_path = temp
            filename = Path(first_tf_path).name
            self.first_tf_label.setText(filename)

    def showDialogSecond(self):

        temp = QFileDialog.getOpenFileName(self, 'Choose target file archive',
               QStandardPaths.writableLocation(QStandardPaths.HomeLocation), "Zip archive (*.zip)")[0]

        if temp:
            global second_tf_path
            second_tf_path = temp

            filename = Path(second_tf_path).name
            self.second_tf_label.setText(filename)

    def startOTABuilding(self):

        global first_tf_path
        global second_tf_path

        path_to_output = "/home/vlad/"
        common_args = "--block -n -v -d MMC -v -p . -m linux_embedded --no_signing -i "
        #self.text_field.append("Nu ti i huila")
        outname = path_to_output + self.first_tf_label.text() + "-" + self.second_tf_label.text() + ".zip"
        #self.text_field.append(common_args + first_tf_path + " " + second_tf_path + " " + outname)
        #startBuildingIncrementalOta(common_args + first_tf_path + " " + second_tf_path + " " + outname)
        execstr = '--block', '-n', '-v', '-d', 'MMC', '-v', '-p', '.', '-m', 'linux_embedded', '--no_signing', '-i', '/home/vlad/target_files/tf-motocaddy-m5-AL-SAR09A02-1.12.3_debug_1.4.7.zip', '/home/vlad/target_files/tf-motocaddy-m5-AL-SAR09A02-1.12.4_debug_1.4.7.zip', '/home/vlad/target_files/tf-motocaddy-m5-AL-SAR09A02-1.12.3_debug_1.4.7.zip-tf-motocaddy-m5-AL-SAR09A02-1.12.4_debug_1.4.7.zip.zip'
        startBuildingIncrementalOta(execstr)

    def startButtonClicked(self):

        global first_tf_path
        global second_tf_path

        #if first_tf_path and second_tf_path:
        thread = Thread(target = self.startOTABuilding, args = [])
        thread.start()

if __name__ == '__main__':

    app = QApplication(sys.argv)

    widget = UiWidget()
    widget.resize(600, 450)
    widget.setWindowTitle('OTATool')
    widget.show()

    sys.exit(app.exec_())
