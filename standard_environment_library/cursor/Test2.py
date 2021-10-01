import time
from plugins.standard_environment_library.cursor.Test import Test
import subprocess

class Test2(Test):
	
	def __init__(self, proband):
		Test.__init__(self,"test2")
		print("Test2")
		self.proband = proband
		self.ergebnis_txt = ["blueBird.jpg", "pigeon.jpg", "duck.jpg", "sparrow.jpg", "seagull.jpg"]
		self.ergebnis_txt.sort()

	# Define a function for the thread
	def test_thread(self, delay):
		time.sleep(delay)
		proc = subprocess.Popen(["xmessage","-geometry", "730x200+300+400", "Please read the task carefully. Once you're ready, click on the 'Start' Button. \n\n TASK: SEARCHING \n 1. Create a new bubble that contains all bird images. \n"])
		#proc = subprocess.Popen(["xmessage", "-geometry", "730x200+300+400",
		#						 "Bitte lese dir die Aufgabe sorgfaeltig durch. Klicke auf den 'Start' Button, sobald du bereit bist. \n\n TASK: SEARCHING \n 1. Erstelle eine Bubble, die nur alle Vogelbilder enthaelt. \n"])
		proc.wait(1000)
		self.starttime = time.time()
		print("Start: {}".format(Test.timestring(self.starttime)))
		with open(self.log_file, 'a') as out:
			out.write("-------------------------------------------------------------\n")
			out.write("Proband: {}\n".format(self.proband))
			out.write("Ordner: {}\n".format(self.dest))
			out.write("Beginn:{}\n".format(self.timestring(self.starttime)))
			running = True
			while running:
				found_txt_dir = Test.existsDirOnlyContainingGivenFiles(self.ergebnis_txt)
				if found_txt_dir != None:
					endtime = time.time()
					out.write("Ende:{}\n".format(Test.timestring(endtime)))
					dauer = endtime-self.starttime
					out.write("pysi,{},{},{},{},{}\n".format(self.test,self.proband,dauer,Test.timestring(self.starttime), Test.timestring(endtime)))
					Test.finish()
					return
				time.sleep(0.1)
		print("finished")


