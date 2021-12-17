# SE 3313 2021 Lab 2

Two applications are implemented in this repository, `Reader` and `Writer`.

From the lab document:

> Writer is a (minimally) user-interactive application. It repeatedly asks if the user would like to create a new thread. As long as the user keeps answering “yes”, it then asks (for each new thread) what the thread wait time should be. The user enters some number of seconds (let’s call it N).
>
> The Writer then spawns a new thread with sleep time of N seconds. Each thread has the SAME job, which is to write some information to a shared memory object once every N seconds. The information to be written is thread Id, report Id (ie: how many times has this thread reported) and metric of how much time has passed since the last report. Each write operation overwrites what was previously in the shared memory object.
>
> This process continues, with the Writer spawning new threads every time the user says “yes”. In principle your system should accept an unlimited number of threads, but you shouldn’t need to test it for more than three or four. Once the user says “no”, the Writer should cancel the threads, wait for them to die, and exit.
>
> Reader has only one job, which is to monitor the contents of the shared memory location and report to the user. It does not need to accept user input, but rather runs for some fixed time, or until you kill it.

This version implements Writer and Reader **with** the use of semaphores.

## Demo

In the following demo, two writer threads are created with delays of 3s and 2s respectively.

Writer:

```
$ ./Writer
> I am a Writer
> Would you like to create a writer thread?
$ yes
> What is the delay time for this thread?
$ 3
> Would you like to create a writer thread?
$ yes
> What is the delay time for this thread?
$ 2
> Would you like to create a writer thread?
$ no
```

Reader:

```
$ ./Reader
I am a reader
> Report: 0 0 0
> Report: 1 0 2
> Report: 0 1 1
> Report: 1 1 1
> Report: 1 2 2
> Report: 0 2 0
> Report: 1 3 2
> Report: 0 3 1
> Report: 1 4 1
> Report: 1 5 2
> Report: 0 4 0
> Report: 1 6 2
> Report: 0 5 1
> Report: 1 7 1
> Report: 1 8 2
> Report: 0 6 0
> Report: 1 9 2
> Report: 0 7 1
> Report: 1 10 1
```

Filtering for thread 0's (thread with 3s delay) reports:

```
> Report: 0 0 0
> Report: 0 1 1
> Report: 0 2 0
> Report: 0 3 1
> Report: 0 4 0
> Report: 0 5 1
> Report: 0 6 0
> Report: 0 7 1
```

Filtering for thread 1's (thread with 2s delay) reports:

```
> Report: 1 0 2
> Report: 1 1 1
> Report: 1 2 2
> Report: 1 3 2
> Report: 1 4 1
> Report: 1 5 2
> Report: 1 6 2
> Report: 1 7 1
> Report: 1 8 2
> Report: 1 9 2
> Report: 1 10 1
```

No reports are missing.

In our semaphore approach, we created a read and write semaphore. These semaphores are used by the writer threads and the reader application are synchronized such that no two threads are accessing the shared resource at once.

In the writer application, writer threads are created by the main process. These writer threads enter an infinite loop. In each loop iteration, the writer thread waits for the write semaphore before entering its critical section. After writing (the threadId, reportId, and lastReport) to the shared resource, it signals the read semaphore.

In the reader application, there is an infinite while loop that continuously waits for the read semaphore signal. When the signal is received, the reader application enters its critical section and reads the shared resource (threadId, reportId, lastReport). After accessing the resource, the reader application signals the write semaphore. Recall that the writer application waits for the write signal in order to enter its critical section and begin writing to the shared resource.

The write and read semaphores are used to synchronize write and read tasks between the writer threads and reader application. These semaphors essentially block the writer threads and reader application from accessing their critical sections if another thread is using it.
