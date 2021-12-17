#include "constants.hpp"
#include "socket.h"
#include "thread.h"
#include <iostream>
#include <signal.h>
#include <stdlib.h>
#include <time.h>

using namespace Sync;

Socket *socket_ptr = NULL;

// Handler to gracefully exit on SIGINT
void sigIntHandler(sig_atomic_t s) {
  if (socket_ptr != NULL) {
    socket_ptr->Close();
  }
  exit(1);
}

int main(void) {
  // Welcome the user
  std::cout << "SE3313 Lab 3 Client\n";

  // Bind SIGINT to sigIntHandler
  signal(SIGINT, sigIntHandler);

  // Create our socket
  Socket socket("127.0.0.1", constants::PORT);
  socket_ptr = &socket;

  try {
    socket.Open();
  } catch (...) {
    std::cerr << "Unable to connect to the server. Please ensure there is an "
                 "active server running before starting a client.\n";
    return 1;
  }

  while (true) {
    std::string userInput;
    std::cout << "Enter a string you'd like the server to transform:\n";
    std::getline(std::cin, userInput);

    // If client enters the termination command, we exit the loop
    if (userInput == constants::CLIENT_TERMINATION_COMMAND) {
      break;
    }

    socket.Write(ByteArray(userInput));
    ByteArray data;
    socket.Read(data);
    // Print out the received message
    std::cout << data.ToString() << "\n";
  }

  socket.Close();
  return 0;
}
