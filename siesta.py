import subprocess
import os
import shutil
import glob
import signal

class Alarm(Exception):
	pass
def alarm_handler(signum, frame):
	raise Alarm

def list_variables():
  return [x.split() for x in  open("VARS").read().strip().split("\n")]

def new_input_file(parameters,var_names,file_name):
  if len(parameters) != len(var_names):
    print "ERROR: number of parameters not equal to number of input variables"
    quit()
  text=open("TEMPLATE").read()
  new_text=text[:]
  for i in range(len(var_names)):
    new_text=new_text.replace("$"+var_names[i],str(parameters[i]))
  fout=open(file_name,"w")
  fout.write(new_text)
  fout.close()

def run_siesta(input_file,output_file):
  fin=open(input_file,"r")
  siesta="/home/cathcart/code/trunk-367/Obj/siesta"
  #siesta="/home/users/cathcart/code/siesta_serial/Obj/siesta"
  #run=subprocess.Popen([siesta],stdin=fin,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,shell=True)
  fout=open(output_file,"w")
  run=subprocess.Popen([siesta],stdin=fin,stdout=fout,stderr=subprocess.STDOUT,shell=True)
  signal.signal(signal.SIGALRM, alarm_handler)
  signal.alarm(20)
  try:
    output=run.communicate()[0]
    signal.alarm(0)
  except Alarm:
    run.terminate()
    print "Siesta timeout"
  fin.close()
  fout.close()
  output=open(output_file).read()
  #fout=open(output_file,"w")
  #fout.write(output)
  return output

def parse(siesta_output):
  #start=siesta_output.find("Total =")
  start=siesta_output.find("(Free)E+")
  if start<0:
    print "ERROR: calculation failed. dumping last five lines"
    print "\n".join(siesta_output.split("\n")[-5::])
    return 9999
  if siesta_output.find("* WARNING: effective split_norm is quite small. Orbitals will be very similar.") > 0:
    print "* WARNING: effective split_norm is quite small. Orbitals will be very similar."
    return 8888
  end=siesta_output.find("\n",start)
  ans=siesta_output[start:end].split()[-1]
  return float(ans)

def siesta_function(name,parameters):
  var_file=list_variables()
  var_names=[x[0] for x in var_file]

  file_in=name+".fdf"
  file_out=name+".out"

  if os.path.exists(name+"/"+file_in):
    #input file already exists
    siesta_output_file=open(name+"/"+file_out,"r")
    siesta_output=siesta_output_file.read()
    siesta_output_file.close() 
  else:
    #set up folder
    os.mkdir(name)
    for pseudo in glob.glob('*.psf'):
      shutil.copy2(pseudo,name)#copy pseudopotentials across
    new_input_file(parameters,var_names,name+"/"+file_in)
    os.chdir(name)
    siesta_output=run_siesta(file_in,file_out)
    os.chdir("../")
  return parse(siesta_output)


if __name__=="__main__":
  var_file=list_variables()
  var_names=[x[0] for x in var_file]
  min_p_list=[float(x[1]) for x in var_file]
  max_p_list=[float(x[2]) for x in var_file]
  print siesta_function("min_test",min_p_list)
  print siesta_function("max_test",max_p_list)
