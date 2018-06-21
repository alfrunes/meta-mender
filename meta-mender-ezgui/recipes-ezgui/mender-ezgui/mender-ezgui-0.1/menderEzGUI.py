import sys
import requests
import re
import os
import json

from PyQt5 import QtCore, QtGui, QtWidgets
from menderLogin import Ui_MainWindow

"""
This is the main GUI login application for logging in to Hosted Mender
and fetching the tenant token.
NOTE: This is the editable GUI-file, while menderLogin.py is generated
      by Qt-creator.
"""

class LogInWindow(QtWidgets.QMainWindow, Ui_MainWindow):

    # Base url: can also be set in gui textfield "server_addr"
    url_base = "https://hosted.mender.io"
    def __init__(self, parent=None):
        super(LogInWindow, self).__init__(parent)

        # Setup window to fixed size without frame and always on top
        self.setupUi(self)
        self.setFixedSize(420, 420)
        self.setWindowFlags(QtCore.Qt.Window |
                            QtCore.Qt.CustomizeWindowHint |
                            QtCore.Qt.WindowStaysOnTopHint)

        # Move window to center of the screen
        qtRectangle = self.frameGeometry()
        screenCenter = QtWidgets.QDesktopWidget().availableGeometry().center()
        qtRectangle.moveCenter(screenCenter)
        self.move(qtRectangle.topLeft())

        # Setup button event functions
        self.logInBtn.setDisabled(True)
        self.logInBtn.setShortcut("Return")
        self.quitBtn.clicked.connect(self._quit_clicked)
        self.logInBtn.clicked.connect(self._logIn_clicked)
        self.serverCheckBox.clicked.connect(self._server_checked)
        self.showPwd.clicked.connect(self._show_pwd)

        # Setup line edit event functions
        self.usr.textChanged.connect(self._txt_change)
        self.pwd.textChanged.connect(self._txt_change)
        self.server_addr.editingFinished.connect(self._domain_changed)


    def _txt_change(self):
        # check if user has entered a valid user name (e-mail)
        # and the password is longer than 5 characters. And
        # enable/disable log in button accordingly
        res = re.search(".+@.+\..+", self.usr.text())
        if res == None:
            self.logInBtn.setDisabled(True)
        elif len(self.pwd.text()) > 5:
            self.logInBtn.setDisabled(False)

    def _quit_clicked(self):
        # Open dialog (sure you want to leave)
        _exit = QtWidgets.QMessageBox.question(self, "Exit",
                                               "Are you sure you want to exit?",
                                               QtWidgets.QMessageBox.Yes |
                                               QtWidgets.QMessageBox.No,
                                               QtWidgets.QMessageBox.No)
        if (_exit == QtWidgets.QMessageBox.Yes):
            QtCore.QCoreApplication.instance().quit()

    def _do_login(self, username, password):
        url = self.url_base + "/api/management/v1/useradm/auth/login"
        try:
            r = requests.post(url,
                              auth=requests.auth.HTTPBasicAuth(username, password))
        except (requests.exceptions.InvalidURL, requests.exceptions.InvalidSchema,
                requests.exceptions.MissingSchema):
            print(sys.exc_info()[0])
            QtWidgets.QMessageBox.warning(self, "Invalid URL",
                                          "Invalid URL: %s" % self.url_base)
            return None
        except requests.exceptions.SSLError:
            _nocert = QtWidgets.QMessageBox.warning(self, "SSL error",
                                                    "Could not POST to: %s" % url)
            if _nocert:
                return self._do_login(username, password, False)[0]
            else:
                return None

        except:
            print(sys.exc_info()[0])
            QtWidgets.QMessageBox.warning(self, "Unexpected Error",
                                          "Could not POST to: %s" % url)
            return None

        return r

    def _logIn_clicked(self):
        # Curl for tenant token
        # Dialog with status (success / failure (invalid credential etc))
        usrName = self.usr.text()
        usrPwd  = self.pwd.text()
        r = self._do_login(usrName, usrPwd)
        if r == None:
            return
        elif (r.status_code == 401):
            msg = QtWidgets.QMessageBox.warning(self, "Log in failed",
                                                "Log in failed: Wrong user name or password")
            return
        elif (r.status_code != 200):
            msg = QtWidgets.QMessageBox.warning(self, "Log in failed",
                                                    "Error: Bad statuscode: %d" %
                                                    r.status_code)
            return

        header = {"Authorization": "Bearer " + str(r.text)}
        url = self.url_base + "/api/management/v1/tenantadm/user/tenant"
        try:
            r = requests.get(url, headers=header)
        except (requests.exceptions.InvalidURL, requests.exceptions.InvalidSchema,
                requests.exceptions.MissingSchema):
            QtWidgets.QMessageBox.warning(self, "Invalid URL",
                                          "Invalid URL: %s" % self.url_base)
            return
        except:
            QtWidgets.QMessageBox.warning(self, "Unexpected Error",
                                          "Could not GET from: %s" % url)
            return
        f = None
        # open mender.conf and add/rewrite tenant token
        if os.path.exists("/etc/mender/mender.conf"):
            try:
                f = open("/etc/mender/mender.conf", "r+")
                data = json.load(f)

                data["tenant_token"] = r.json()["tenant_token"]
                f.seek(0)
                json.dump(data, f, indent=2, sort_keys=True)
                f.truncate()
            finally:
                if f != None:
                    f.close()

        else: # not os.path.exists()
            # Should not occur
            os.makedirs("/etc/mender")
            try:
                f = open("/etc/mender/mender.conf", "w")
                data = {"tenant_token": r.json()["tenant_token"]}
                json.dump(data, f, indent=2)
            finally:
                if f != None:
                    f.close()

        QtWidgets.QMessageBox.information(self, "Success",
                                          "Successfully stored your Hosted Mender token")
        QtCore.QCoreApplication.instance().quit()

    def _domain_changed(self):
        # text entered in domain name
        if self.server_addr.text() == "":
            self.url_base = "https://hosted.mender.io"
        else:
            # prepend "https://" if user doesn't
            if self.server_addr.text().startswith("https://"):
                self.url_base = self.server_addr.text()
            else:
                self.server_addr.setText("https://" + self.server_addr.text())
                self.url_base = self.server_addr.text()

    def _server_checked(self):
        # checkBox callback: toggle textfield editable
        if self.serverCheckBox.isChecked():
            self.server_addr.setReadOnly(False)
            self.server_addr.setFrame(True)
        else:
            self.server_addr.setReadOnly(True)
            self.server_addr.setFrame(False)
            self.server_addr.setText("")
            self._domain_changed()

    def _show_pwd(self):
        # check box showPwd callback
        if self.showPwd.isChecked():
            self.pwd.setEchoMode(QtWidgets.QLineEdit.Normal)
        else:
            self.pwd.setEchoMode(QtWidgets.QLineEdit.Password)




if __name__ == "__main__":
    if os.getcwd() != "/etc/mender-ezgui":
        # TODO: Remove this...
        os.chdir("/etc/mender-ezgui")
    app = QtWidgets.QApplication(sys.argv)
    win = LogInWindow()
    QtWidgets.QDesktopWidget().availableGeometry().center()
    win.show()
    app.exec_()
