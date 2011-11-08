import Pyro4
import time
import server

def function(x):
	return x**2

def client(dispatcher):
	dispatcher.checkin()
	while True:
		while dispatcher.workQueueSize() == 0:
			print "sleeping"
			time.sleep(1)

		job = dispatcher.getWork()

		if job == "Poison":
			print "%d-client taking poison"
			break

		print "got job:",
		print job,
		result = function(job)
		print result
		dispatcher.putResult(result)

if __name__ == "__main__":
	dispatcher = server.dispatcher_setup()
	client(dispatcher)
