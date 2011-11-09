import Pyro4
import Queue as queue
import time
import logging

class DispatcherQueue(object):
    def __init__(self):
        self.workqueue = queue.Queue()
        self.resultqueue = queue.Queue()
	self.no_clients = queue.Queue()
	self.death = 0
	#setup logging
	FORMAT="%(asctime)s %(message)s"
	logging.basicConfig(filename="dispatcher.log",level=logging.DEBUG, format=FORMAT)
    def putWork(self, item):
        self.workqueue.put(item)
	self.add_log("Putting work from queue")
	self.add_log("There are now %d+1 items in the work queue"%self.workqueue.qsize())
    def getWork(self, timeout=5):
	self.add_log("Getting work from queue")
	self.add_log("There are now %d-1 items in the work queue"%self.workqueue.qsize())
        return self.workqueue.get(block=True, timeout=timeout)
    def putResult(self, item):
	self.add_log("Putting results in queue")
	self.add_log("There are now %d+1 items in the result queue"%self.resultqueue.qsize())
        self.resultqueue.put(item)
    def getResult(self, timeout=5):
        return self.resultqueue.get(block=True, timeout=timeout)
    def workQueueSize(self):
        return self.workqueue.qsize()
    def resultQueueSize(self):
        return self.resultqueue.qsize()
    def checkin(self):
	self.no_clients.put(1)
	id = self.no_clients.qsize()
	logging.info("%d clients attached to the server" % id)
	return id
    def checkout(self):
	g = self.no_clients.get()
	id = self.no_clients.qsize()
	logging.info("%d clients attached to the server" % id)
    def Poison(self):
	logging.info("Adding Poison to queue")
	id = self.no_clients.qsize()
	[self.putWork((i,"Poison")) for i in range(id)]
    def add_log(self,x):
	logging.info(x)

def ns_setup(ns_host = "localhost", ns_port = 9090):
#	ns_host = "localhost"
#	ns_port = 9090
	return Pyro4.naming.locateNS(host=ns_host, port=ns_port)

def dispatcher_setup(ns_host = "localhost", ns_port = 9090):
	ns = ns_setup(ns_host,ns_port)

	uri = ns.lookup("dispatcher")
	return Pyro4.Proxy(uri)

def server_setup(ns_host = "localhost", ns_port = 9090,daemon_host = "localhost", daemon_port = 6969):

	ns = ns_setup(ns_host, ns_port)

	daemon = Pyro4.core.Daemon(host=daemon_host, port=daemon_port)

	dispatcher = DispatcherQueue()
	uri = daemon.register(dispatcher)
	ns.register("dispatcher", uri)


	logging.info("Dispatcher is ready with nameserver on %s:%d"%(ns_host,ns_port))
	daemon.requestLoop(lambda: not dispatcher.death)

if __name__ == "__main__":
	server_setup()
