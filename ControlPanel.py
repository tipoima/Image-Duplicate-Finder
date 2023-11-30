from PyQt5.QtWidgets import QWidget,QHBoxLayout,QVBoxLayout,QLabel,QPushButton,QFileDialog,QCheckBox 
import os

class ControlPanel(QWidget):
    def __init__(self,parent):
        super().__init__()
        
        self.parent=parent
        
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        self.searchDir=None
        
        self.startButton=QPushButton("Start",self)
        self.startButton.clicked.connect(self.start)
        self.startButton.setEnabled(False)
        self.startButton.setToolTip("This might take a while...")
        
        dirSelectButton=QPushButton('Select directory', self)
        dirSelectButton.clicked.connect(self.setDir)
        
        innerWidget=QWidget()
        innerLayout=QHBoxLayout(innerWidget)
        
        self.currDirlabel=QLabel()
        self.currDirlabel.setText("No directory selected")
        
        layout.addWidget(self.startButton)
        layout.addWidget(dirSelectButton)
        layout.addWidget(self.currDirlabel)
        layout.addWidget(innerWidget)
        
        self.RGBcheckbox=QCheckBox("Color-sensitive mode")
        self.RGBcheckbox.stateChanged.connect(self.RGBupdate)
        self.RGBcheckbox.setToolTip("Different colorations will be considered distinct images. Triples execution time")
        
        self.threadingCheckbox=QCheckBox("Allow multiprocessing")
        self.threadingCheckbox.stateChanged.connect(self.threadingUpdate)
        self.threadingCheckbox.setToolTip("Massively speeds up preprocessing. Has no effect for already preprocessed directories")
        
        innerLayout.addWidget(self.RGBcheckbox)
        innerLayout.addWidget(self.threadingCheckbox)
        
        
        
        innerWidget.setLayout(innerLayout)
        
        self.setLayout(layout)
        
        self.show()
        
    def setDir(self):
        file = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        if file!="":
            file=os.path.normpath(file)
            self.searchDir=file
            self.currDirlabel.setText(file)
            self.startButton.setEnabled(True)
            
        
        
        
    def RGBupdate(self):
        self.parent.parent.RGBmode=self.RGBcheckbox.isChecked()
    def threadingUpdate(self):
        self.parent.parent.Threading=self.threadingCheckbox.isChecked()
        
    def start(self):
        self.parent.parent.start(self.searchDir)