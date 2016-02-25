import subprocess

def runScript(scriptName, args):
   praatExec = ["praat/praat", "--run", "--no-pref-files", scriptName];
   praatExec.extend(args)
   output = subprocess.check_output(praatExec);

   return output

