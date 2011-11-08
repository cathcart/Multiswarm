import Pyro4
import time
import server
import siesta
import logging

def function(x):
	return x**2

def client(dispatcher):
	client_id = dispatcher.checkin()
	dispatcher.add_log("hello from %d-client"%client_id)
	while True:
		while dispatcher.workQueueSize() == 0:
			
			time.sleep(1)

		(id, job) = dispatcher.getWork()

		if job == "Poison":
			dispatcher.add_log("%d-client taking poison"%client_id)
			dispatcher.checkout()
			break

		#print "got job:",
		dispatcher.add_log("%d-client has job: %s"%(client_id,str(job)))
		#result = function(job)
		result = siesta.siesta_function("_".join([str(y) for y in job]),job)
		dispatcher.add_log("%d-client with job: %s has result: %s"%(client_id,str(job),str(result)))
		#print result
		dispatcher.putResult((id,result))

if __name__ == "__main__":
	dispatcher = server.dispatcher_setup("parsons01",9090)
	client(dispatcher)
