import pandas as pd
import os
import datetime
from datetime import timedelta
import sys
from PyQt4 import QtGui, QtCore
def run_accrual():
	#Import original dataset and allow changes to dataset
	path = r'C:\Users\tommy\Downloads'
	file_name = 'Test Dataset - Sheet1 (1)'
	current_date = '09/22/2017'

	# Convert current_date into a date
	current_date = datetime.datetime.strptime(current_date, '%m/%d/%Y')

	def import_data(path, file_name):
		os.chdir(path)
		original_df = pd.read_csv(file_name + '.csv',parse_dates=["Hire_Date"])
		return original_df

	original_df = import_data(path,file_name)

	#Creates DF With Only Necessary Data
	def new_dataframe(df):
		new_df = df[['Hourly/Salary','Dept',r'D/IL/Sal','Hire_Date','Prior_Year_Carry_Forward','Hours_Taken ', 'Rate']].copy()
		# 'Dept', 'D/IL/Sal', 'Hire Date', 'Prior Year Carry Forward', 'Hours Taken', 'Rate'])
		return new_df

	use_df = new_dataframe(original_df)


	#Function to calculate number of days earned in current year and for next year
	def indy_cy_days(time_delta):
		vacation_days = 5
		if time_delta >= timedelta(days = (365 *20)):
			vacation_days = 20
		elif time_delta >= timedelta(days = (365 * 10)):
			vacation_days = 15
		return vacation_days

	#Create 'years_of_service' column
	use_df['current_date'] = current_date
	use_df['years_of_service'] = (use_df['current_date'] - use_df['Hire_Date'])

	#Apply indy_cy_days function to create CY_Days
	use_df['CY_Days'] = use_df['years_of_service'].apply(indy_cy_days)

	#Calculate remaining days
	remaining_days_list = []
	for index,row in use_df.iterrows():
		cf = row['Prior_Year_Carry_Forward']
		hours_taken = row['Hours_Taken ']
		cy_days = row['CY_Days']
		total_days = cf + cy_days - (hours_taken/8.0)
		remaining_days = total_days
		max_accrual = cy_days/2.0
		if total_days >= max_accrual:
			remaining_days = max_accrual
		remaining_days_list.append(remaining_days)

	use_df['remaining_days'] = remaining_days_list


	#Function to calculate accrual amount based on rate
	def calculate_accrual(use_df, year_end = False):
		use_df['total_accrual'] = use_df['remaining_days'] * use_df['Rate']
		if year_end != False:
			use_df['total_accrual'] += (use_df['next_year_days']* use_df['Rate'])
		return use_df

	use_df = calculate_accrual(use_df)
	#Summarize results by GL Code
	def summarize_by_GL_Code(df, to_csv = False):
		output_df = df.groupby('D/IL/Sal')['total_accrual'].sum()
		if to_csv != False:
			output_df.to_csv()
		return output_df
	return summarize_by_GL_Code(use_df)

#Developing GUI
class Window(QtGui.QMainWindow):
	#Creatig Vacation Accrual GUI
	def __init__(self):
		super(Window,self).__init__()
		self.setGeometry(50,100 ,1000,800)
		self.setWindowTitle('Vacation Accrual Calculation')
		#Add Exit File Menu
		extractAction = QtGui.QAction("Exit", self)
		extractAction.setShortcut("Ctrl+Q")
		extractAction.setStatusTip('Exit App')
		extractAction.triggered.connect(self.close_application)

		#Run File Menu Action
		runAction = QtGui.QAction("Run", self)
		runAction.setShortcut('Ctrl+R')
		runAction.setStatusTip('Run Program')
		runAction.triggered.connect(self.run_program)

		self.statusBar()
		#Create File Menubar obect
		mainMenu = self.menuBar()
		fileMenu = mainMenu.addMenu('&File')
		fileMenu.addAction(runAction)
		fileMenu.addAction(extractAction)
		self.home()
#Home Screen Code
	def home(self):
		#Quit Button Visual
		quit_btn = QtGui.QPushButton("Quit",self)
		quit_btn.resize(quit_btn.sizeHint())
		quit_btn.move(200,44)
		quit_btn.clicked.connect(self.close_application)

		#Run Button Visual
		run_btn = QtGui.QPushButton("Run", self)
		run_btn.resize(run_btn.sizeHint())
		run_btn.move(0,44)
		run_btn.clicked.connect(self.run_program)
		

		self.show()
#Action for quit_btn
	def close_application(self):
		choice = QtGui.QMessageBox.question(self, 'Warning!', "Quit?", QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
		if choice == QtGui.QMessageBox.Yes:
			print('Qutting')
			sys.exit()
		else:
			pass
#Action for run_btn
	def run_program(self):
		print(run_accrual())


def run():
	app = QtGui.QApplication(sys.argv)
	GUI = Window()
	sys.exit(app.exec_())

run()
