import time
from plugins.standard_environment_library.cursor.Test import Test
import subprocess

class Test3(Test):
	
	def __init__(self, proband):
		Test.__init__(self,"test3")
		print("Test3")
		self.proband = proband
		self.ergebnis_txt = ["animals.txt",
				"groceryList.txt",
				"icecream.txt",
				"joke.txt",
				"message.txt",
				"movies.txt",
				"plants.txt",
				"sources.txt",
				"todo.txt",
				"travel.txt",
				"size.txt"]
		self.ergebnis_txt.sort()
		self.ergebnis_img = ["blueBird.jpg",
				"cat.jpg",
				"bear.jpg",
				"panda.jpg",
				"pigeon.jpg",
				"rabbit.jpg",
				"duck.jpg",
				"shiba.jpg",
				"sparrow.jpg",
				"seagull.jpg"]
		self.ergebnis_img.sort()

	# Define a function for the thread
	def test_thread(self, delay):
		time.sleep(delay)
		proc = subprocess.Popen(["xmessage","-geometry", "730x200+300+400", "Please read the task carefully. Once you're ready, click on the 'Start' Button. \n\n TASK: MERGING \n 1. Merge all 4 bubbles. \n 2. Sort by filetype: Separate image and text files and make sure they're in two different bubbles. \n"])
		#proc = subprocess.Popen(["xmessage", "-geometry", "730x200+300+400",
		#						 "Bitte lese dir die Aufgabe sorgfaeltig durch. Klicke auf den 'Start' Button, sobald du bereit bist. \n\n TASK: MERGING \n 1. Fuehre alle vier Bubbles zusammen. \n 2. Sortiere anschliessend nach Dateityp: \n Alle Bilddateien und Textdateien müssen nun jeweils in eine separate Bubble. \n"])
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
				found_img_dir = Test.existsDirOnlyContainingGivenFiles(self.ergebnis_img)
				if found_txt_dir != None and found_img_dir != None:
					endtime = time.time()
					out.write("Ende:{}\n".format(Test.timestring(endtime)))
					dauer = endtime-self.starttime
					out.write("pysi,{},{},{},{},{}\n".format(self.test,self.proband,dauer,Test.timestring(self.starttime), Test.timestring(endtime)))
					Test.finish()
					return				time.sleep(0.1)
		print("finished")


