import Pyro4
import time
import server
import siesta

def function(x):
	return x**2

def client(dispatcher):
	dispatcher.checkin()
	while True:
		while dispatcher.workQueueSize() == 0:
			print "sleeping"
			time.sleep(1)

		(id, job) = dispatcher.getWork()

		if job == "Poison":
			print "%d-client taking poison"
			dispatcher.checkout()
			break

		print "got job:",
		print job,
		result = function(job)
		#result = siesta.siesta_function("_".join([str(y) for y in job]),job)
		print result
		dispatcher.putResult((id,result))

if __name__ == "__main__":
	dispatcher = server.dispatcher_setup()
	client(dispatcher)
