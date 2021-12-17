#include <iostream>
#include <time.h>
#include <string>

#include "SharedObject.h"
#include "constants.hpp"
#include "Semaphore.h"

int main(void)
{
	std::cout << "I am a reader" << std::endl;

	Shared<constants::Resource> sharedMemory(constants::SHARED_MEMORY_NAME);

	// create write and read semaphores
	Semaphore *writeSem = new Semaphore(constants::WRITE_SEM_NAME);
	Semaphore *readSem = new Semaphore(constants::READ_SEM_NAME);

	while (true)
	{

		// wait for the resource to be available to read
		readSem->Wait();

		int thread_id = sharedMemory->thread_id;
		int report_id = sharedMemory->report_id;
		int time_since_last_report = sharedMemory->time_since_last_report;

		// siganal to processes waiting to write to the resource that it is now available
		writeSem->Signal();

		if (thread_id != -1)
		{
			std::cout << "Report: " + std::to_string(thread_id) + " " + std::to_string(report_id) + " " + std::to_string(time_since_last_report) << std::endl;
		}
	}
}
