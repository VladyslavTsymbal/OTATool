import sys
from pathlib import Path

from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QSpacerItem, QTextEdit
from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QMessageBox, QDesktopWidget, QFileDialog, QDialog
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QStandardPaths, QSize, QFileInfo, QThread, QObject, QDir

from ota_from_target_files import startBuildingIncrementalOta

first_tf_path  = ""
second_tf_path = ""

class BuildingOTAWorker(QObject):

    def __init__(self, opts, parent=None):

        super(BuildingOTAWorker, self).__init__(parent)
        self.opts = opts

    def run(self):

        startBuildingIncrementalOta(self.opts)


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

        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        options |= QFileDialog.DontUseCustomDirectoryIcons
        dialog = QFileDialog()
        dialog.setOptions(options)
        dialog.setFilter(dialog.filter() | QDir.Hidden)

        if dialog.exec_() == QDialog.Accepted:

            temp = dialog.selectedFiles()[0]
            if temp:
                global first_tf_path
                first_tf_path = temp
                filename = Path(first_tf_path).name
                self.first_tf_label.setText(filename)

    def showDialogSecond(self):

        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        options |= QFileDialog.DontUseCustomDirectoryIcons
        dialog = QFileDialog()
        dialog.setOptions(options)
        dialog.setFilter(dialog.filter() | QDir.Hidden)

        if dialog.exec_() == QDialog.Accepted:

            temp = dialog.selectedFiles()[0]
            if temp:
                global second_tf_path
                second_tf_path = temp

                filename = Path(second_tf_path).name
                self.second_tf_label.setText(filename)

    def startButtonClicked(self):

        global first_tf_path
        global second_tf_path

        if first_tf_path and second_tf_path:

            path_to_output = QStandardPaths.writableLocation(QStandardPaths.HomeLocation) + '/'
            outname = path_to_output + self.first_tf_label.text() + "-" + self.second_tf_label.text() + ".zip"
            exec_list_options = ['--block', '-n', '-v', '-d', 'MMC', '-v', '-p', '.', '-m', 'linux_embedded', '--no_signing', '-i']
            exec_list_options.append(first_tf_path)
            exec_list_options.append(second_tf_path)
            exec_list_options.append(outname)

            self.thread = QThread()
            self.worker = BuildingOTAWorker(exec_list_options)
            self.worker.moveToThread(self.thread)
            self.thread.started.connect(self.worker.run)
            #self.worker.finished.connect(self.thread.quit)
            #self.worker.finished.connect(self.worker.deleteLater)
            #self.thread.finished.connect(self.thread.deleteLater)

            self.thread.start()

if __name__ == '__main__':

    app = QApplication(sys.argv)

    widget = UiWidget()
    widget.resize(600, 450)
    widget.setWindowTitle('OTATool')
    widget.show()

    sys.exit(app.exec_())
