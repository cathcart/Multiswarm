import math
import random
import multiprocessing
import siesta
import multi
import logging
import pickle

class Vector:
  def __class__(self):
    return "Vector"
  def __init__(self, data):
    self.data = data
  def __repr__(self):
    return repr(self.data)  
  def __add__(self, other):
    data = []
    for j in range(len(self.data)):
      data.append(self.data[j] + other.data[j])
    return Vector(data)
  def __sub__(self,other):
    return self+(-1)*other
  def __len__(self):
    return len(self.data)
  def __rmul__(self,time):
    return self*time
  def __mul__(self,time):
    return Vector([time*self.data[i] for i in range(len(self.data))])
  def __getitem__(self,index):
    return self.data[index]
  def __setitem__(self,index,value):
    self.data[index] = value

class Particle:

    def __init__(self,min_p,max_p,constants):
        self.min_p = min_p
        self.max_p = max_p
        self.position = Vector([(min_p+(max_p-min_p)*next(r()))[i] for i in range(len(min_p))])
        self.velocity = Vector([((max_p-min_p)*(2*next(r())-1))[i] for i in range(len(min_p))])
        [self.K_l, self.K_g, self.K_gv, self.mass] = constants 
        self.local_min=self.position
        self.local_min_cost=9999

    def update(self,min_position,group_position):

	#print some info
	logging.info("Updating particle %s position and velocity" %str(self.position))
	print "Updating particle %s position and velocity" %str(self.position)
	
        global_vector = min_position-self.position
        local_vector = self.local_min-self.position
        group_vector = group_position-self.position
    
        #get random numbers for the different vector quantities above
        [r_l,r_g,r_gv]=[next(r()) for i in range(3)]
    
        #update velocity
        update_vector = (self.K_l*r_l*local_vector + self.K_g*r_g*global_vector + self.K_gv*r_gv*group_vector)
        velocity = self.mass * self.velocity + update_vector
        #the velocity is bound from -d to d where d=|max_p-min_p|
        d=Vector([abs(x) for x in (self.max_p-self.min_p)])
        velocity = [bound(velocity[i],-1*d[i],d[i]) for i in range(len(velocity))]
        self.velocity = Vector(velocity)
    
        #update position
        position = self.position + self.velocity
        position = [bound(position[i],self.min_p[i],self.max_p[i]) for i in range(len(position))] 
        self.position = Vector(position)

    def set_cost(self,value):
        self.cost=value
        #update local position
        if self.cost < self.local_min_cost:
            self.local_min = self.position
            self.local_min_cost = self.cost

def sed_file(name,X):
	var_file = siesta.list_variables()
	var_names=[x[0] for x in var_file]
	output_string =""
	for x in zip(var_names,X):
		output_string += "s/$%s/%f/g\n"%(x[0],x[1])
	out=open(name,"w")
	out.write(output_string)
	out.close

def pickle_write(object):
	output = open('swarm.pkl', 'wb')
	# Pickle the list using the highest protocol available.
	pickle.dump(object, output, -1)
	logging.info("Swarm has been pickled")

def pickle_read():
	pkl_file = open('swarm.pkl', 'rb')
	logging.info("Loading swarm from pickle")
	return pickle.load(pkl_file)

def distance(one,two):
    return math.sqrt(sum([(one[i]-two[i])**2 for i in range(len(one))]))

def bound(x,l,u):

    if x < l :
        return l
    if x > u :
        return u
    return x

def grouping(vector_list,n):
    l = []
    tmp_list = vector_list
    groups = []
    t = len(vector_list)/n
    for one in vector_list[0::len(vector_list)/n]:
        sorted_list = sorted(tmp_list,key=lambda x: distance(one.position,x.position))
        groups.append(sorted_list[0:len(vector_list)/n])
        tmp_list = tmp_list[len(vector_list)/n::]

    return groups

def r():
    yield random.random()

def my_function(parameters):
    [x1,x2]=parameters
    return 100*(x2-x1**2)**2+(1-x1)**2

def run(function,min_p,max_p,constants,procs):
#########################################################
	"""
    run takes the following arguments:
    
    function:
    	the function the PSO is to minimise
    
    min_p:
    	the minimium bounding parameters to search from. Passed as a Vector. One element per parameter
    
    max_p:
    	the maximium bounding parameters to search to. Passed as a Vector. One element per parameter
    
    constants:
    	These are the constants of the PSO. In order:
    		No. particles
    		No. iterations
    		No. of groups (This is the number of groups the swarm will be split into for the calculation of the group local mins)
    		local constant (These constants allow for a weighted average of the different parameters)
    		global constant
    		group constant
    		particle mass
    
    procs:
    	The number of processors that the PSO should use. PSO are almost 100% trivially parallel. The only serial calculations that are required is the calculation of the global min.
	"""
#########################################################
	N = constants[0]
	iterations = constants[1]
	grouping_N = constants[2]
	constants = constants[3:]

	swarm=[]#list of swarm particles

	#initialise the particles
	if load_data:
		swarm = pickle_read()
	else:
		for particle in range(N):
			swarm.append(Particle(min_p,max_p,constants))

	#distribute and calculate the value of the function at all of these points
	min_position = min_p
  
	for iteration in range(iterations):

		#calculate the function at the particle positions
		cost_results = multi.run([particle.position.data for particle in swarm])
		[swarm[i].set_cost(cost_results[i]) for i in range(len(swarm))]

		#update all the local extrema and decide the new global extrema
		min_position = sorted(swarm,key=lambda x: x.cost)[0].position
		logging.info("Iteration: %d, global min: %s"%(iteration," ".join([str(x) for x in min_position])))
		sed_file("best_so_far.sed",min_position)
    
		groups=grouping(swarm,grouping_N)
		for group in groups:
			group_position=sorted(group,key=lambda x: x.cost)[0].position

			for particle in group:
				particle.update(min_position,group_position)
	#save swarm to disk for safe keeping 
	pickle_write(swarm)


	p=sorted(swarm,key=lambda x: x.cost)[0].position
	sed_file("final.sed",p)
	print "Results:",
	return [math.sqrt(sum([i**2 for i in p])),p]

if __name__ == "__main__":
    #setup logging 
    logging.basicConfig(filename="swarm.log",level=logging.DEBUG)
    min_p=Vector([0,0])
    max_p=Vector([2,2])
    #constants=[23,500,1,0,2.8446,0,-0.3328]
    #constants=[60,2000,1,0,2.9708,0,-0.27]
    constants=[3,20,1,0,2.9708,0,-0.27]
    print "Running Siesta PSO with parameters %s" %str(constants)
    logging.info("Running Siesta PSO with parameters %s" %str(constants))
    #print run(my_function,min_p,max_p,constants,2)
    var_file=siesta.list_variables()
    min_p_list=[float(x[1]) for x in var_file]
    max_p_list=[float(x[2]) for x in var_file]
    min_p=Vector(min_p_list)
    max_p=Vector(max_p_list)
    print run(lambda x :siesta.siesta_function("_".join([str(y) for y in x]),x),min_p,max_p,constants,8)
    multi.poison()
#  ans=run(N,iterations,1,min_p,max_p,lambda x :siesta.siesta_function("_".join([str(y) for y in x]),x))[1]
#  print ans
#  out=open("final","w")
#  out.write(str(ans))
#  out.close()
