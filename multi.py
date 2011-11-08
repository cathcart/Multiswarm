import time
import Pyro4
import server

def main():
	dispatcher = server.dispatcher_setup()
	jobs = range(10)
	[dispatcher.putWork((i,jobs[i])) for i in range(len(jobs))]

	while dispatcher.resultQueueSize() < len(jobs):
		time.sleep(1)

	results = []
	[results.append(dispatcher.getResult()) for i in range(len(jobs))]

	#ensure results are returned in the same order they're put into the queue
	return [y[1] for y in sorted(results,key=lambda x: x[0])]

if __name__ == "__main__":
	results = main()
	dispatcher = server.dispatcher_setup()
	dispatcher.Poison()
	for r in results:
		print r
