
import pprint
import sys
from datetime import date, timedelta, datetime
from PyQt6.QtCore import QDate,QTime,QSettings,Qt,QObject,QTimer
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtGui import QCursor
from PyQt6.QtWidgets import QApplication, QMainWindow, QMessageBox, QPushButton
from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView, QCalendarWidget
from database import Database
from jira import Jira
import io
import csv

class App(QObject): 
    def __init__(self,ui, database, jira):
        super().__init__()
        self.ui=ui
        self.uiOptions=ui.Options
        self.database = database
        self.jira = jira
        print("App inizializzata")
        self.initConnect()
        self.initVar()
        self.update_records_list()

    def initVar(self):
        current_date=date.today()
        self.date_var=date.today().strftime('%d/%m/%Y')
        date_obj = datetime.strptime(self.date_var,'%d/%m/%Y')
        weekNumber=date_obj.isocalendar()[1]    
        self.ui.dateLabel.setText(f"Date (week:{weekNumber}) :")
        qdate=QDate(current_date.year, current_date.month, current_date.day)
        self.ui.TaskDate.setDate(date.today())        
        self.ui.TaskDate.setReadOnly(True)  # Make QDateEdit read-only
        self.ui.TaskDate.installEventFilter(self)  # Install event filter to capture clicks
        hours = QTime.currentTime()
        self.ui.TaskHours.setTime(hours)
        self.ui.TaskCategory.addItems(self.get_activities())
        self.ui.ListTask.cellClicked.connect(self.on_row_clicked)
        #self.jiradesc=self.jira.getJiraID(839)
        #self.ui.JiraDesk.setTextPlain(self.jiradesc)
        # Add calendar widget
        self.TaskDateCalendar = QCalendarWidget()
        self.TaskDateCalendar.setWindowFlags(Qt.WindowType.Popup)
        self.TaskDateCalendar.clicked.connect(self.on_calendar_clicked)


    def initConnect(self):
        print("App in esecuzione")
        self.ui.SaveTask.clicked.connect(self.save_data)
        self.ui.JiraId.editingFinished.connect(self.updateJiraDes)
        self.ui.JiraSave.clicked.connect(self.save_jira_setting)


    def eventFilter(self, source, event):
        if event.type() == QtCore.QEvent.Type.MouseButtonPress and source is self.ui.TaskDate:
            self.show_calendar()
            return True
        return super().eventFilter(source, event)

    
    def show_calendar(self):
        cursor_pos = QCursor.pos()
        self.TaskDateCalendar.move(cursor_pos)
        self.TaskDateCalendar.setSelectedDate(self.ui.TaskDate.date())
        self.TaskDateCalendar.show()

    def on_calendar_clicked(self, date):
        self.ui.TaskDate.setDate(date)
        self.TaskDateCalendar.hide()
        
        
    def updateJiraDes(self):
        jiraid=self.ui.JiraId.text()
        descJira=self.jira.getJiraID(jiraid)
        self.ui.JiraDesc.setText(descJira)

    def input_only_number(self, input, maxleng=4):
        if input.isdigit()  and len(input) <= maxleng:
            return True
        else:
            return False

    def save_data(self, event=None):
        date_str = str(self.ui.TaskDate.date().toPyDate())
        ora_str = self.ui.TaskHours.time().toString("HH:mm")
        datetime_str = f"{date_str} {ora_str}"
        
    
        activity = self.ui.TaskCategory.currentText() or "Altro"
        jira=self.ui.JiraId.text()
        description = self.ui.TaskDesc.toPlainText()
        status=self.ui.TaskStatus.currentText()
        if len(description) < 1:
            dlg = QMessageBox()
            dlg.setWindowTitle("I have a question!")
            dlg.setText("Description must be at least 1 characters long.")
            return
        jiradesc=self.ui.JiraDesc.text()
        if (jira != ""):
             activity=self.jira.getJiraCat(jira)
        #jiradesc=''
        self.database.insert_data(datetime_str, jira,jiradesc, activity, description,status)
        self.update_records_list()
        #self.activity_combobox['values'] = self.get_activities()
        self.ui.TaskCategory.clear()
        self.ui.TaskCategory.addItems(self.get_activities())
        self.show_toast("Task Saved.")
      

    def update_records_list(self):
        self.ui.ListTask.clear()
        records = self.database.get_records()
        
        header = self.ui.ListTask.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        header.setMinimumSectionSize(30)
    
        self.ui.ListTask.setColumnCount(8)
        self.ui.ListTask.setHorizontalHeaderLabels(['ID', 'Week', 'Date', 'Activity','Status','Jira ID', 'Jira Desc', 'Description'])
        #self.ui.ListTask.setColumnWidth(0, 30)  # Colonna 1 larghezza 200 pixel
        #self.ui.ListTask.setColumnWidth(1, 30)  
        #self.ui.ListTask.setColumnWidth(2, 150)  
        #self.ui.ListTask.setColumnWidth(3, 100)  
        #self.ui.ListTask.setColumnWidth(4, 50)  
        #self.ui.ListTask.setColumnWidth(5, 250)  
        #self.ui.ListTask.setColumnWidth(6, 230)  
        self.ui.ListTask.resizeColumnsToContents()
        self.ui.ListTask.resizeRowsToContents()
        
        
        #self.ui.ListTask.horizontalHeader().setStretchLastSection(True)
        self.ui.ListTask.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
 
        for record in records:
            date_obj = datetime.strptime(record[1], '%Y-%m-%d %H:%M')
            date_str = date_obj.strftime('%d/%m/%Y %H:%M')
            weekNumber=date_obj.isocalendar()[1]
            
            #self.ui.ListTask.addItem('{}:({}){} - {} - {} - {} - {}'.format())
            jiraId=record[2] or "No ID";
            jiraDesc=record[3] or "No Jira Desc";
            activity=record[4] or "No Activity";
            status=record[6];
            dati = [str(record[0]),str(weekNumber),date_str,activity,status,jiraId,jiraDesc,record[5]]
           
            table_widget=self.ui.ListTask
            # Aggiungi una nuova riga
            table_widget.setRowCount(table_widget.rowCount() + 1)

            # Imposta il contenuto delle celle
            for col, dato in enumerate(dati):
                cell_item = QTableWidgetItem(dato)
                table_widget.setItem(table_widget.rowCount() - 1, col, cell_item)
                        
                        
                        
                def get_activities(self):
                    activities = self.database.get_activities()
                    return sorted(set(activities))

        self.ui.ListTask.resizeColumnsToContents()
        self.ui.ListTask.resizeRowsToContents()
        
    def export_data(self):
        try:
            days = int(self.ui.NumDayExport.getCurrentText())
            records = self.database.get_records_last_x_days(days)
            records.sort(key=lambda x: datetime.strptime(x[0], '%Y-%m-%d'))
            csv_data = io.StringIO()
            writer = csv.writer(csv_data)
            writer.writerow(['Date', 'Activity','JiraId', 'Description'])
            for record in records:
                date_obj = datetime.strptime(record[0], '%Y-%m-%d')
                date_str = date_obj.strftime('%d/%m/%Y')
                writer.writerow([date_str, record[2], record[1], record[3]])
            with open('activities.csv', 'w', newline='') as csvfile:
                csvfile.write(csv_data.getvalue())
            self.clipboard_clear()
            self.clipboard_append(csv_data.getvalue())
            #messagebox.showinfo("Success", "Data exported successfully.")
        except Exception as e:
            print ("error")
            #messagebox.showerror("Error", "An error occurred while exporting data: {}".format(str(e)))

    def delete_data(self):
        selected_indices = self.records_list.curselection()
        if not selected_indices:
            #messagebox.showerror("Error", "Please select one or more records to delete.")
            return
        for index in reversed(selected_indices):
            record_id = self.records_list.get(index).split(':')[0]
            self.db.delete_record(record_id)
        self.update_records_list()
        #messagebox.showinfo("Success", "Selected records deleted successfully.")

    def save_jira_setting(self):
        self.jira.saveJiraSetting(self.ui.JiraUrl.text(),self.ui.JiraUser.text(),self.ui.JiraPassword.text())
        
    def get_activities(self):
        activities = self.database.get_activities()
        return sorted(set(filter(None, activities)))
    
    def on_row_clicked(self, row, column):
        # Get the ID of the selected row
        record_id = self.ui.ListTask.item(row, 0).text()
        
        # Fetch the record from the database
        record = self.database.get_records_by_id(record_id)
        self.populate_input_fields(record)
       
       
    def populate_input_fields(self, record):
        # Assuming record is a dictionary with keys matching the input field names
        self.ui.TaskDate.setDate(QDate.fromString(record['date'], 'yyyy-MM-dd'))
        self.ui.TaskHours.setTime(QTime.fromString(record['time'], 'HH:mm'))
        self.ui.TaskCategory.setCurrentText(record['activity'])
        self.ui.JiraId.setText(record['jira_id'])
        self.ui.TaskDesc.setPlainText(record['description'])
        self.ui.TaskStatus.setCurrentText(record['status'])
        self.ui.JiraDesc.setText(record['jira_desc'])

    def show_toast(self, message):  # New method
        toast = QMessageBox(self.ui)
        toast.setWindowTitle("Info")
        toast.setText(message)
        #toast.setStandardButtons(QMessageBox.StandardButton.NoButton)
        #toast.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.ToolTip)
        toast.show()

        QTimer.singleShot(2000, toast.close) 