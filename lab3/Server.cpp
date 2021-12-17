#include "constants.hpp"
#include "socketserver.h"
#include "thread.h"
#include <algorithm>
#include <list>
#include <stdlib.h>
#include <time.h>
#include <vector>

using namespace Sync;

class WorkerThread : public Thread {
private:
  Socket &socket;

  // Transforms an input string by making it all caps
  std::string transformData(std::string toTransform) {
    std::for_each(toTransform.begin(), toTransform.end(),
                  [](char &c) { c = toupper(c); });
    return toTransform;
  }

public:
  WorkerThread(Socket &socket) : socket(socket) {}

  ~WorkerThread() {}

  // Read from the socket, transform the data, and write it back
  virtual long ThreadMain() {
    while (true) {
      ByteArray data;
      socket.Read(data);
      ByteArray transformedData(transformData(data.ToString()));
      socket.Write(transformedData);
    }
  }
};

// This thread handles the server operations
class ServerThread : public Thread {
private:
  SocketServer &server;

public:
  ServerThread(SocketServer &server) : server(server) {}

  ~ServerThread() {}

  virtual long ThreadMain() {
    while (true) {
      // Wait for a client socket connection
      Socket *newConnection = new Socket(server.Accept());
      WorkerThread *workerThread = new WorkerThread(*newConnection);
    }
  }
};

int main(void) {
  std::cout << "SE3313 Lab 3 Server\n";

  // Create our server
  SocketServer server(constants::PORT);
  // Need a thread to perform server operations
  ServerThread serverThread(server);

  std::cout << "Press enter to gracefully terminate the server.\n";
  // Wait for user input before proceeding
  std::cin.get();

  // Shut down and clean up the server
  server.Shutdown();
}
