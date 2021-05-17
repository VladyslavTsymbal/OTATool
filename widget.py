import sys
from pathlib import Path
from queue import Queue

from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QSpacerItem, QTextEdit, QProgressBar
from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QMessageBox, QDesktopWidget, QFileDialog, QDialog
from PyQt5.QtGui import QIcon, QTextCursor
from PyQt5.QtCore import QStandardPaths, QSize, QFileInfo, QThread, QObject, QDir, pyqtSignal, pyqtSlot, QRunnable, QThreadPool

from ota_from_target_files import startBuildingIncrementalOta

first_tf_path  = ""
second_tf_path = ""
output_dir     = QStandardPaths.writableLocation(QStandardPaths.HomeLocation) + '/'

# The new Stream Object which replaces the default stream associated with sys.stdout
# This object just puts data in a queue!
class WriteStream(object):
    def __init__(self,queue):
        self.queue = queue

    def write(self, text):
        self.queue.put(text)

    def flush(self):
        pass

# A QObject (to be run in a QThread) which sits waiting for data to come through a Queue.Queue().
# It blocks until data is available, and one it has got something from the queue, it sends
# it to the "MainThread" by emitting a Qt Signal
class MyReceiver(QObject):
    mysignal = pyqtSignal(str)

    def __init__(self,queue, *args, **kwargs):
        QObject.__init__(self, *args, **kwargs)
        self.queue = queue

    @pyqtSlot()
    def run(self):
        while True:
            text = self.queue.get()
            self.mysignal.emit(text)

class WorkerSignals(QObject):
    '''
    Defines the signals available from a running worker thread.

    Supported signals are:

    started
        No data

    finished
        No data

    error
        tuple (exctype, value, traceback.format_exc() )

    result
        object data returned from processing, anything

    progress
        int indicating % progress

    '''
    started = pyqtSignal()
    finished = pyqtSignal()
    error = pyqtSignal(tuple)
    result = pyqtSignal(object)

class Worker(QRunnable):

    def __init__(self, fn, *args, **kwargs):

        super(Worker, self).__init__()

        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

    def run(self):

        self.signals.started.emit()

        try:
            result = self.fn(*self.args, **self.kwargs)
        except:
            exctype, value = sys.exc_info()[:2]
        else:
            # Return the result of the processing
            self.signals.result.emit(result)
        finally:
            # Done
            self.signals.finished.emit()

class UiWidget(QWidget):

    def __init__(self):

        super().__init__()

        self.threadpool = QThreadPool()
        self.init()

    def init(self):

        self.output_dir_button = QPushButton("Output Dir")
        self.output_dir_button.setFixedSize(QSize(100, 40))
        self.output_dir_button.clicked.connect(self.showOutputDirDialog)
        self.output_dir_label = QLabel(output_dir)

        self.first_tf_button = QPushButton("First TF")
        self.first_tf_button.setFixedSize(QSize(100, 40))
        self.first_tf_button.clicked.connect(self.showDialogFirst)
        self.first_tf_label = QLabel("")

        self.second_tf_button = QPushButton("Second TF")
        self.second_tf_button.setFixedSize(QSize(100, 40))
        self.second_tf_button.clicked.connect(self.showDialogSecond)
        self.second_tf_label = QLabel("")

        hbox0 = QHBoxLayout()
        hbox0.addWidget(self.output_dir_button)
        hbox0.addWidget(self.output_dir_label)

        hbox1 = QHBoxLayout()
        hbox1.addWidget(self.first_tf_button)
        hbox1.addWidget(self.first_tf_label)

        hbox2 = QHBoxLayout()
        hbox2.addWidget(self.second_tf_button)
        hbox2.addWidget(self.second_tf_label)

        self.text_field = QTextEdit()
        self.text_field.setReadOnly(True)

        vbox1 = QVBoxLayout()
        vbox1.addLayout(hbox0)
        vbox1.addLayout(hbox1)
        vbox1.addLayout(hbox2)
        vbox1.addWidget(self.text_field)

        self.progress_bar = QProgressBar(self)
        self.progress_bar.setRange(0, 1)
        self.start_button = QPushButton("Start")
        self.start_button.clicked.connect(self.startButtonClicked)
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.close)

        hbox3 = QHBoxLayout()
        hbox3.addWidget(self.progress_bar)
        hbox3.addStretch(1)
        hbox3.addWidget(self.start_button)
        hbox3.addWidget(self.cancel_button)

        main_vbox = QVBoxLayout()
        main_vbox.addLayout(vbox1)
        main_vbox.addLayout(hbox3)

        self.setLayout(main_vbox)
        self.center()

    def progressBarOnStart(self):
        self.progress_bar.setRange(0, 0)

    def progressBarOnFinished(self):
        self.progress_bar.setRange(0, 1)

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

    def showOutputDirDialog(self):

        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        options |= QFileDialog.DontUseCustomDirectoryIcons
        dialog = QFileDialog()
        dialog.setOptions(options)
        dialog.setFileMode(QFileDialog.DirectoryOnly)
        dialog.setFilter(dialog.filter() | QDir.Hidden)

        if dialog.exec_() == QDialog.Accepted:

            temp = dialog.selectedFiles()[0]
            if temp:
                global output_dir
                output_dir = temp + "/"
                self.output_dir_label.setText(output_dir)

    def showDialogFirst(self):

        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        options |= QFileDialog.DontUseCustomDirectoryIcons
        dialog = QFileDialog()
        dialog.setOptions(options)
        dialog.setNameFilters(["Zip archives (*.zip)"])
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
        dialog.setNameFilters(["Zip archives (*.zip)"])
        dialog.setFilter(dialog.filter() | QDir.Hidden)

        if dialog.exec_() == QDialog.Accepted:

            temp = dialog.selectedFiles()[0]
            if temp:
                global second_tf_path
                second_tf_path = temp
                filename = Path(second_tf_path).name
                self.second_tf_label.setText(filename)

    def showWarningDialog(self):
        QMessageBox.warning(self, 'Select target files', "Select First and Second target files!")

    def disableWidgetsOnBuildingStarted(self):

        self.output_dir_button.setDisabled(True)
        self.first_tf_button.setDisabled(True)
        self.second_tf_button.setDisabled(True)
        self.start_button.setDisabled(True)

    def enableWidgetsOnBuildingFinished(self):

        self.output_dir_button.setEnabled(True)
        self.first_tf_button.setEnabled(True)
        self.second_tf_button.setEnabled(True)
        self.start_button.setEnabled(True)

    def startButtonClicked(self):

        global first_tf_path
        global second_tf_path

        if first_tf_path and second_tf_path:
            self.text_field.clear()

            try:
                first_tf = self.parseTargetFileVersion(self.first_tf_label.text())
                second_tf = self.parseTargetFileVersion(self.second_tf_label.text())
                self.createOTA(first_tf, second_tf)
            except:
                print("Bad things happened during parsing target file version!")
        else:
            self.showWarningDialog()

    def parseTargetFileVersion(self, target_file):

        dash = target_file.rfind("-")
        dot = target_file.rfind(".")

        return target_file[dash + 1:dot]

    def createOTA(self, first_tf, second_tf):

        outname = output_dir + first_tf + "-" + second_tf + ".zip"
        exec_list_options = ['--block', '-n', '-v', '-d', 'MMC', '-v', '-p', '.', '-m', 'linux_embedded', '--no_signing', '-i']
        exec_list_options.append(first_tf_path)
        exec_list_options.append(second_tf_path)
        exec_list_options.append(outname)

        worker = Worker(startBuildingIncrementalOta, exec_list_options)
        worker.signals.started.connect(self.disableWidgetsOnBuildingStarted)
        worker.signals.started.connect(self.progressBarOnStart)
        worker.signals.finished.connect(self.enableWidgetsOnBuildingFinished)
        worker.signals.finished.connect(self.progressBarOnFinished)

        self.threadpool.start(worker)

    @pyqtSlot(str)
    def appendText(self, text):

        self.text_field.moveCursor(QTextCursor.End)
        self.text_field.insertPlainText(text)

if __name__ == '__main__':

    queue = Queue()
    ws = WriteStream(queue)
    sys.stdout = ws
    sys.stderr = ws

    app = QApplication(sys.argv)

    widget = UiWidget()
    widget.resize(600, 450)
    widget.setWindowTitle('OTATool')
    widget.show()

    thread = QThread()
    my_receiver = MyReceiver(queue)
    my_receiver.mysignal.connect(widget.appendText)
    my_receiver.moveToThread(thread)
    thread.started.connect(my_receiver.run)
    thread.start()

    sys.exit(app.exec_())
