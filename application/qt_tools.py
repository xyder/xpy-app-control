from PyQt5 import QtCore
import sys
import webbrowser
from PyQt5.QtCore import QThread

from PyQt5.QtGui import QIcon, QCursor
from PyQt5.QtWidgets import QMenu, QSystemTrayIcon, QApplication, QAction

from config import *


class FlaskThread(QThread):
    """
    Class that defines the main flask server thread.
    """
    from application import app
    server_app = app

    exit_signal = QtCore.pyqtSignal()

    def __init__(self):
        super(FlaskThread, self).__init__()

    def run(self):
        """
        Starts the server.
        """
        self.server_app.thread = self
        self.server_app.run(use_reloader=False)

    def connect_exit_signal_to_slot(self, slot):
        """
        Connects the exit signal to the specified slot.
        """
        self.exit_signal.connect(slot)

    def stop(self):
        """
        Stops the server thread.
        """
        self.quit()


class SystemTrayIcon(QSystemTrayIcon):
    """
    Class that defines the application system tray
    """
    server_thread = FlaskThread()

    def __init__(self, icon, parent=None):
        QSystemTrayIcon.__init__(self, icon, parent)
        menu = QMenu(parent)

        # initialize and add the open webpage menu item
        launch_action = QAction('&Open Webpage', self)
        launch_action.setToolTip('Server is @ ' + ActiveConfig.SERVER_NAME)
        launch_action.triggered.connect(self.launch_slot)
        menu.addAction(launch_action)

        menu.addSeparator()

        # initialize and add the exit application menu item
        exit_action = QAction('&Exit', self)
        exit_action.triggered.connect(self.exit_slot)
        menu.addAction(exit_action)

        menu.setToolTipsVisible(True)
        self.setContextMenu(menu)

        # connect signals
        self.activated.connect(self.tray_activated_slot)
        self.server_thread.connect_exit_signal_to_slot(self.exit_slot)

    @staticmethod
    def launch_slot():
        """
        Slot that opens the server web page.
        """
        webbrowser.open_new_tab('http://' + ActiveConfig.SERVER_NAME)

    def exit_slot(self):
        """
        Slot that triggers the application exit.
        :return:
        """
        print('Exit signal received..')
        self.setVisible(False)
        self.server_thread.stop()
        sys.exit(0)

    def tray_activated_slot(self, reason):
        if reason == QSystemTrayIcon.Trigger:
            self.contextMenu().popup(QCursor.pos())
            self.contextMenu().activateWindow()

    def start(self):
        """
        Starts the flask server.
        """
        self.show()
        self.server_thread.start()


def main():
    qapp = QApplication(sys.argv)
    tray_icon = SystemTrayIcon(QIcon(os.path.join(PathsConfig.ICONS_DIR, 'app-icon-on.ico')))
    tray_icon.start()
    sys.exit(qapp.exec())
