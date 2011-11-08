import Pyro4
import sleep

def function(x):
	return x**2

def setup():
	ns_host = "localhost"
	ns_port = 9090
	ns = Pyro4.naming.locateNS(host=ns_host, port=ns_port)

	uri = ns.lookup("dispatcher")
	return Pyro4.Proxy(uri)

def client(dispatcher):
	while True:
		while dispatcher.workQueueSize() == 0:
			time.sleep(1)

		job = dispatcher.getWork()
		result = function(job)
		dispatcher.putResult(result)

if __name__ == "__main__":
	dispatcher = setup()
	client(dispatcher)
