#include <iostream>
#include "input_reader.h"

int main(int argc, char* argv[]) {
	filesystem::InputReader inputReader;
	inputReader.start(argc, argv);
	return 0;
}