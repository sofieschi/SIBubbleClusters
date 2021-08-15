import subprocess
from threading import Thread
import time
from datetime import datetime
import os
from pathlib import Path
from plugins.standard_environment_library.SIEffect import SIEffect
from plugins.standard_environment_library.lasso.Lasso import Lasso

class Test:
    
    def __init__(self, testname):
        print("Test start")
        self.root_dir = "/home/sofie/Desktop"
        self.test = testname
        self.proband="SchiesslingSofie"
        self.log_file = self.root_dir +"/"+self.proband+".log"
        self.dest = self.getUniqueDest()
        self.start_test_thread()
    
        
    def start_test_thread(self):
        try:
            print("Start Test Thread")
            t = Thread(target=self.test_thread, args=(2,))
            t.start()
        except:
            print("Start Test Thread failed")

   # Define a function for the thread
    def test_thread(self, delay):
        pass

    @staticmethod
    def timestring(time):
        return datetime.fromtimestamp(time).strftime("%Y-%m-%d %H:%M:%S")

    def getUniqueDest(self):
        dest = self.root_dir+"/"+self.proband+"-test1-pysi"
        index = 0
        while True:
                proband_dir = Path(dest)
                if not proband_dir.is_dir() and not proband_dir.is_file():
                        break
                dest = self.root_dir+"/"+self.proband+"-"+self.test+"-pysi"+str(index)
                index += 1
        return dest

    @staticmethod
    def existsDirOnlyContainingGivenFiles(ergebnis):
        lassos = SIEffect.get_all_objects_extending_class(Lasso)
        for lasso in lassos:
            names = []
            ll = lasso.get_linked_lassoables()
            for l in ll:
                names.append(l.filename)
            #print("names={}=?{} {}".format(names, ergebnis, lasso.get_uuid()))
            names.sort()
            if names == ergebnis:
                #print("gleich!")
                return lasso 
        return None
        
    @staticmethod
    def finish():
        proc = subprocess.Popen(["xmessage","-geometry", "730x200+300+400", "Erfolgreich beendet!"])
        proc.wait(1000)
        exit()
