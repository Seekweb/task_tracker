import sys
from PyQt6.QtCore import QSettings
from PyQt6.QtWidgets import QStyleFactory,QApplication, QMainWindow
from PyQt6.uic import loadUi
from app import App
from database import Database
from jira import Jira

class Main(QMainWindow):
    def __init__(self):
        super(Main, self).__init__()
        self.settings= QSettings("Seekweb", "TaskTracker")
        loadUi('gui.ui', self)

        
        self.database = Database()
        self.jira = Jira()
        self.app = App(self,self.database,self.jira)



if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('windowsvista')
    mainWindow = Main()
    mainWindow.show()
    sys.exit(app.exec())