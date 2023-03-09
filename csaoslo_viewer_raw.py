import sys
import glob
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtGui import *
import skvideo.io
import numpy as np
import matplotlib.pyplot as plt
import cv2

def mat2gray(img):
    return (img.copy() - img.min())/(img.max() - img.min())

def convert_np_to_qimage(np_img):
	# convert the numpy array to a qimage
	img_scaled = (mat2gray(np_img)*255).astype(np.uint8)
	frame = cv2.cvtColor(img_scaled, cv2.COLOR_GRAY2RGB)
	h, w = img_scaled.shape
	return QImage(frame.data, h, w, 3*w, QImage.Format_RGB888)

def parse_avi(fname):
	# parse the avi file
	videodata = skvideo.io.vread(fname, as_grey=True)
	return np.squeeze(np.array(videodata))

class RawViewerUI(QMainWindow):
	def __init__(self):
		super(RawViewerUI, self).__init__()

		# Load the ui file
		uic.loadUi("raw_viewer.ui", self)

		# Define our widgets
		self.horizontalscrollbar = self.findChild(QScrollBar, "horizontalScrollBar")
		self.spinbox = self.findChild(QSpinBox, "spinBox")
		self.label = self.findChild(QLabel, "label")
		self.actionload = self.findChild(QAction, "actionLoad")
		self.actionsave = self.findChild(QAction, "actionSave_Current")
		self.statusbar = self.findChild(QStatusBar, "statusbar")
		self.plaintextedit = self.findChild(QPlainTextEdit, "plainTextEdit")
		self.checkbox = self.findChild(QCheckBox, "checkBox")


		# Connect the widgets to functions
		self.horizontalscrollbar.valueChanged.connect(self.scrollbar_changed)
		self.spinbox.valueChanged.connect(self.spinbox_changed)
		self.actionload.triggered.connect(self.load)
		self.actionsave.triggered.connect(self.save_current)
		self.checkbox.stateChanged.connect(self.mark_good_frame)

		# Set default values
		self.defaultfilepath = "/Users/daniel/Library/CloudStorage/Box-Box/Daniel Personal Box/CSAOSLO/Human imaging data"
		self.currentframenindex = 0
		self.scalefactor = 1
		self.fnames = []
		self.data = np.array([])
		self.numframes = 0
		self.height = 0
		self.width = 0
		self.goodframes = np.array([])

		# Show The App
		self.show()

	def load(self):
		fname_temp = QFileDialog.getOpenFileName(self, "Open File", self.defaultfilepath, "AVI Files (*.avi)")[0][:-6]
		self.statusbar.showMessage(fname_temp.rsplit("/", 1)[-1])
		self.defaultfilepath = fname_temp.rsplit("/", 1)[0] # update the default file path
		self.fnames = glob.glob(fname_temp + "*.avi") # get all the files
		self.fnames.sort() # sort the files
		self.data = np.concatenate([parse_avi(fname) for fname in self.fnames])
		self.numframes, self.height, self.width = self.data.shape
		self.goodframes = np.zeros(self.numframes)
		self.spinbox.setMaximum(self.numframes-1)
		self.spinbox.setValue(0)
		self.horizontalscrollbar.setMaximum(self.numframes-1)
		self.horizontalscrollbar.setValue(0)
		self.update_image()
		self.mark_good_frame()

	def save_current(self):
		# save the current image
		return

	def scrollbar_changed(self):
		# update the image based on the slider position
		self.currentframenindex = self.horizontalscrollbar.value()
		self.spinbox.setValue(self.currentframenindex)
		self.checkbox.setChecked(int(self.goodframes[self.currentframenindex]))
		self.update_image()

	def spinbox_changed(self):
		# update the image based on the spinbox value
		self.currentframenindex = self.spinbox.value()
		self.horizontalscrollbar.setValue(self.currentframenindex)
		self.checkbox.setChecked(int(self.goodframes[self.currentframenindex]))
		self.update_image()

	def update_image(self):
		# update the image
		if self.data.size > 0:
			self.scalefactor = self.label.frameGeometry().height()/self.height
			img_resized = cv2.resize(self.data[self.currentframenindex], dsize=(int(self.height*self.scalefactor), int(self.width*self.scalefactor)), interpolation=cv2.INTER_CUBIC)
			qimg = convert_np_to_qimage(img_resized)
			self.label.setPixmap(QPixmap.fromImage(qimg))

	def resizeEvent(self, event: QResizeEvent) -> None:
		# override the resize event
		self.update_image()

	def mark_good_frame(self):
		# mark the current frame as good
		self.goodframes[self.currentframenindex] = self.checkbox.isChecked()
		self.plaintextedit.setPlainText(", ".join([str(i) for i in np.where(self.goodframes == 1)[0]]))

# Initialize The App
app = QApplication(sys.argv)
UIWindow = RawViewerUI()
app.exec_()