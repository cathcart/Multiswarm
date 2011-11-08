import time
import Pyro4
import server

def main():
	dispatcher = server.dispatcher_setup()
	jobs = range(10)
	[dispatcher.putWork(job) for job in jobs]

	while dispatcher.resultQueueSize() < len(jobs):
		time.sleep(1)

	results = []
	[results.append(dispatcher.getResult()) for i in range(len(jobs))]
	
	return results

if __name__ == "__main__":
	results = main()
	for r in results:
		print r
