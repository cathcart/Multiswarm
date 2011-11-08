import Pyro4
import Queue as queue
import time

class DispatcherQueue(object):
    def __init__(self):
        self.workqueue = queue.Queue()
        self.resultqueue = queue.Queue()
	self.no_clients = 0
	self.death = 0
    def putWork(self, item):
        self.workqueue.put(item)
    def getWork(self, timeout=5):
        return self.workqueue.get(block=True, timeout=timeout)
    def putResult(self, item):
        self.resultqueue.put(item)
    def getResult(self, timeout=5):
        return self.resultqueue.get(block=True, timeout=timeout)
    def workQueueSize(self):
        return self.workqueue.qsize()
    def resultQueueSize(self):
        return self.resultqueue.qsize()
    def checkin(self):
	self.no_clients += 1
	return self.no_clients
	print "%d clients attached to the server" % self.no_clients
    def checkout(self):
	self.no_clients -= 1
	print "%d clients attached to the server" % self.no_clients
    def Poison(self):
	[self.putWork((i,"Poison")) for i in range(self.no_clients)]
	self.death = 1

def ns_setup(ns_host = "localhost", ns_port = 9090):
	ns_host = "localhost"
	ns_port = 9090
	return Pyro4.naming.locateNS(host=ns_host, port=ns_port)

def dispatcher_setup(ns_host = "localhost", ns_port = 9090):
	ns = ns_setup(ns_host = "localhost", ns_port = 9090)

	uri = ns.lookup("dispatcher")
	return Pyro4.Proxy(uri)

def server_setup(ns_host = "localhost", ns_port = 9090,daemon_host = "localhost", daemon_port = 6969):

	ns = ns_setup(ns_host, ns_port)

	daemon = Pyro4.core.Daemon(host=daemon_host, port=daemon_port)

	dispatcher = DispatcherQueue()
	uri = daemon.register(dispatcher)
	ns.register("dispatcher", uri)
	print("Dispatcher is ready.")
	daemon.requestLoop(lambda: not dispatcher.death)

if __name__ == "__main__":
	print "setup server"
	server_setup()		
