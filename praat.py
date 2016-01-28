import subprocess

def runScript(scriptName, args):
   praatExec = ["praat/praat", "--run", scriptName];
   praatExec.extend(args)
   output = subprocess.check_output(praatExec);

   return output

if __name__ == "__main__":
   runScript("sp1.wav", "drawSpectrogram")
   energy = runScript("sp1.wav", "queryEnergy")
   print energy

