"""
A file for the testing of the python threading module

Author: Mitchell Crawford
ENGG2800 Sem1, 2021

"""

import queue
import threading
import time

# variables
exitFlag = 0


class CreateThread(threading.Thread):
    def __init__(self, threadID, threadName, threadQ):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.threadName = threadName
        self.threadQ = threadQ

    def run(self):
        print(f'starting thread {self.threadName} [ID: {self.threadID}]\n')
        data_processing(self.threadName, self.threadQ)
        print(f'Exiting thread {self.threadName}')

"""
    def print_things(self, threadName, counter):
        while counter:
            if exitFlag:
                threadName.exit()
            time.sleep(2)
            print(f'This is count number {counter} [Name: {self.threadName}]\n')
            counter -= 1
"""

def data_processing(threadName, threadQ):
    while not exitFlag:
        queue_lock.acquire()
        if not work_queue.empty():
            data = threadQ.get()
            queue_lock.release()
            print(f'Processing {threadName}, {data}')
        else:
            queue_lock.release()
        time.sleep(0.5)

threads_list = ["Thread-1", "Thread-2"]
thread_names = ["1", "2", "3", "4", "5"]
queue_lock = threading.Lock()
work_queue = queue.Queue(10)
threads = []
thread_ID = 1

# Create threads
for tName in threads_list:
    thread = CreateThread(thread_ID, tName, work_queue)
    thread.start()
    threads.append(thread)
    thread_ID += 1

# Fill the queue
queue_lock.acquire()
for word in thread_names:
    work_queue.put(word)
queue_lock.release()

# Waiting for queue to be empty
while not work_queue.empty():
    pass

# Notify the threads to exit now
exitFlag = 1

# Wait for all threads to complete
for t in threads:
    t.join()
print(">> Main thread ending <<")