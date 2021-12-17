#include <string>

namespace constants
{
    const std::string SHARED_MEMORY_NAME = "sharedMemory";
    const std::string WRITE_SEM_NAME = "writeSemaphore";
    const std::string READ_SEM_NAME = "readSemaphore";

    struct Resource
    {
        int thread_id;
        int report_id;
        time_t last_report_time;
        int time_since_last_report;
    };

}