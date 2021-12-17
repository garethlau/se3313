#include <iostream>
#include <time.h>
#include <vector>
#include <string>

#include "thread.h"
#include "SharedObject.h"
#include "constants.hpp"
#include "Semaphore.h"

class NonBlockingWriterThread : public Thread
{
public:
	int thread_num;
	int delay;
	bool flag;

	NonBlockingWriterThread(int in, int delay) : Thread(8 * 1000)
	{
		this->thread_num = in;
		this->delay = delay;
	}

	virtual long ThreadMain(void) override
	{

		int report_id = 0;
		// create shared resource to write to
		Shared<constants::Resource> sharedMemory(constants::SHARED_MEMORY_NAME);

		// create semaphores
		Semaphore *writeSem = new Semaphore(constants::WRITE_SEM_NAME);
		Semaphore *readSem = new Semaphore(constants::READ_SEM_NAME);

		while (true)
		{
			sleep(this->delay);
			// get current time
			time_t curr_time = time(NULL);

			// wait for the resource to be available to be written to
			writeSem->Wait();

			// write information to shared memory
			if (sharedMemory->thread_id == -1)
			{
				sharedMemory->time_since_last_report = 0;
			}
			else
			{
				sharedMemory->time_since_last_report = curr_time - sharedMemory->last_report_time;
			}
			sharedMemory->thread_id = this->thread_num;
			sharedMemory->report_id = report_id;
			sharedMemory->last_report_time = curr_time;

			// signal to processes waiting to read the resource that it is ready
			readSem->Signal();

			// increment this threads report id
			report_id++;

			if (flag)
			{
				break;
			}
		}
	}
};

int main(void)
{
	std::cout << "I am a Writer" << std::endl;
	int thread_num = 0;
	// initialize vector to keep track of thread pointers
	std::vector<NonBlockingWriterThread *> threads;
	// create shared resource, designate this thread as the owner of the shared resources
	Shared<constants::Resource> sharedMemory(constants::SHARED_MEMORY_NAME, true);
	sharedMemory->thread_id = -1;

	// create semaphores for write and read actions
	Semaphore *writeSem = new Semaphore(constants::WRITE_SEM_NAME, 1, true);
	Semaphore *readSem = new Semaphore(constants::READ_SEM_NAME, 0, true); // set initial state to 0, prevent read before something is written

	while (true)
	{
		std::string user_input = "";
		std::cout << "Would you like to create a writer thread?" << std::endl;
		std::cin >> user_input;

		if (user_input == "no")
		{
			// loop through pointers
			for (int i = 0; i < threads.size(); i++)
			{
				// set the flag to true, causing the thread to exit the main while loop
				NonBlockingWriterThread *thread = threads[i];
				thread->flag = true;
				delete thread;
			}

			return 0;
		}
		else if (user_input == "yes")
		{
			int delay;
			std::cout << "What is the delay time for this thread?" << std::endl;
			std::cin >> delay;
			NonBlockingWriterThread *thread = NULL;
			thread = new NonBlockingWriterThread(thread_num, delay);
			threads.push_back(thread);
			thread_num++;
		}
		else
		{
			std::cout << "Unrecognized command" << std::endl;
		}
	}
}