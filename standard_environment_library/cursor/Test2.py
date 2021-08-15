import time
from plugins.standard_environment_library.cursor.Test import Test
import subprocess

class Test2(Test):
	
	def __init__(self, proband):
		Test.__init__(self,"test2")
		print("Test2")
		self.proband = proband
		self.ergebnis_txt = ["vers1.txt", "vers2.txt", "vers3.txt", "vers4.txt"]
		self.ergebnis_txt.sort()

	# Define a function for the thread
	def test_thread(self, delay):
		time.sleep(delay)
		proc = subprocess.Popen(["xmessage","-geometry", "730x200+300+400", "Bitte Textdateien in einen eigenen Ordner geben und alle Bilddateien in einen eigenen Ordner geben!"])
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
				time.sleep(0.1)
		print("finished")


