import Pyro4
import time
import server
import siesta
import logging
import Queue

def function(x):
	return x**2

def client(dispatcher):
	client_id = dispatcher.checkin()
	dispatcher.add_log("hello from %d-client"%client_id)
	while True:
		while dispatcher.workQueueSize() == 0:
			
			time.sleep(1)

		try:
			(id, job) = dispatcher.getWork()
		except Queue.Empty:
			dispatcher.add_log("%d-client has problem getting item from queue"%(client_id))

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
		try:
			dispatcher.putResult((id,result))
		except Queue.Full:
			dispatcher.add_log("%d-client has problem adding items to the queue"%(client_id))

if __name__ == "__main__":
	dispatcher = server.dispatcher_setup("parsons01",9090)
	client(dispatcher)
