import Pyro4
import Queue as queue
import time
import logging

class DispatcherQueue(object):
    def __init__(self):
        self.workqueue = queue.Queue()
        self.resultqueue = queue.Queue()
	self.no_clients = 0
	self.death = 0
	#setup logging
	logging.basicConfig(filename="dispatcher.log",level=logging.DEBUG)
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
	logging.info("%d clients attached to the server" % self.no_clients)
	return self.no_clients
    def checkout(self):
	self.no_clients -= 1
	logging.info("%d clients attached to the server" % self.no_clients)
    def Poison(self):
	logging.info("Adding Poison to queue")
	[self.putWork((i,"Poison")) for i in range(self.no_clients)]
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
	server_setup("parsons01",9090,"parsons01",6969)		
