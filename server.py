import Pyro4
import Queue as queue

class DispatcherQueue(object):
    def __init__(self):
        self.workqueue = queue.Queue()
        self.resultqueue = queue.Queue()
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

def setup():
	ns_host = "localhost"
	ns_port = 9090
	ns=Pyro4.naming.locateNS(host=ns_host, port=ns_port)

	daemon_host = "localhost"
	daemon_port = 6969 
	daemon=Pyro4.core.Daemon(host=daemon_host, port=daemon_port)

	dispatcher=DispatcherQueue()
	uri=daemon.register(dispatcher)
	ns.register("example.distributed.dispatcher", uri)
	print("Dispatcher is ready.")
	daemon.requestLoop()

if __name__ == "__main__":
	print "setup server"
	setup()		
