#include "input_reader.h"
#include "utils/errors.h"
#include <fstream>      // std::ifstream

namespace filesystem {
	using namespace errors;

	void InputReader::start(int argc, char* argv[])
	{
		std::istream *in=&std::cin;
		if (argc == 2) {
			in = new std::ifstream(argv[1]);
		}
		while (true)
		{
			std::string str;
			std::getline(*in, str);
			if (argc == 2) {
				if (str.size() == 0) exit(0);
				std::cout << str << std::endl;
			}

			std::istringstream ss(str);
			std::string command; 
			if (ss >> command)
			{
				if (command == "cr") {
					std::string name;
					if (!(ss >> name) || name.length() > MAX_FILENAME_LENGTH - 1 || name.length() == 0 || !ss.eof()) {
						_incorrectSyntax();
					}
					else {
						if (fs.createFile(name.c_str()) == RetStatus::OK) {
							std::cout << "file " << name << " created" << std::endl;
						}
						else {
							_error();
						}		
					}
				}
				else if (command == "de") {
					std::string name;
					if (!(ss >> name) || !ss.eof()) {
						_incorrectSyntax();
					}
					else {
						if (fs.destroyFile(name.c_str()) == RetStatus::OK) {
							std::cout << "file " << name << " destroyed" << std::endl;
						}
						else {
							_error();
						}
					}
				}
				else if (command == "op") {
					std::string name;
					if (!(ss >> name) || !ss.eof()) {
						_incorrectSyntax();
					}
					else {
						int oft_index = fs.open(name.c_str());
						if (oft_index != -1) {
							std::cout << "file " << name << " opened, index = " << oft_index << std::endl;
						}
						else {
							_error();
						}
					}
				}
				else if (command == "cl") {
					int oft_index;
					if (!(ss >> oft_index) || !ss.eof()) {
						_incorrectSyntax();
					}
					else {
						if (fs.close(oft_index) == RetStatus::OK) {
							std::cout << "file " << oft_index << " closed" <<  std::endl;
						}
						else {
							_error();
						}
					}
				}
				else if (command == "rd") {
					int oft_index, count;
					if (!(ss >> oft_index, ss >> count) || !ss.eof()) {
						_incorrectSyntax();
					}
					else {
						char* char_to_read = new char[count];
						int count_read = fs.read(oft_index, char_to_read, count);
						if (count_read != RetStatus::FAIL) {
							std::cout << count_read << " bytes read: ";
							for (int i = 0; i < count_read; i++) {
								std::cout << char_to_read[i];
							}
							std::cout << std::endl;
						}
						else {
							_error();
						}
						delete[] char_to_read;
					}
				}
				else if (command == "wr") {
					int oft_index, count;
					char c;
					if (!(ss >> oft_index, ss >> c, ss >> count) || !ss.eof()) {
						_incorrectSyntax();
					}
					else {
						char* char_to_write = new char[count];
						std::fill(char_to_write, char_to_write + count, c);
						int count_write = fs.write(oft_index, char_to_write, count);
						if (count_write != RetStatus::FAIL) {
							std::cout << count_write << " bytes written" << std::endl;
						}
						else {
							_error();
						}
						delete[] char_to_write;
					}
				}
				else if (command == "sk") {
					int oft_index, pos;
					if (!(ss >> oft_index, ss >> pos) || !ss.eof()) {
						_incorrectSyntax();
					}
					else {
						if (fs.lseek(oft_index, pos) == RetStatus::OK) {
							std::cout << "current position is " << pos << std::endl;
						}
						else {
							_error();
						}
					}
				}
				else if (command == "dr") {
					std::vector<std::string> filenames = fs.getAllDirectoryFiles();
					if (filenames.empty()) {
						std::cout << "directory is empty" << std::endl;
					}
					for (size_t i = 0; i < filenames.size(); i++) {
						std::cout << filenames[i] << std::endl;
					}
				}
				else if (command == "in") {
					std::string filename;
					if (!(ss >> filename) || !ss.eof()) {
						_incorrectSyntax();
					}
					else {
						if (fs.loadFS(filename.c_str()) == 1) {
							std::cout << "disk restored" << std::endl;
						}
						else {
							std::cout << "disk initialized" << std::endl;
						}
					}
				}
				else if (command == "sv") {
					std::string filename;
					if (!(ss >> filename) || !ss.eof()) {
						_incorrectSyntax();
					}
					else {
						if (fs.saveFS(filename.c_str()) == RetStatus::OK) {
							std::cout << "disk saved" << std::endl;
						}
						else {
							_error();
						}
					}
				}
				else {
					std::cout << '\'' << command << "' is not recognized as an internal or external command,operable program or batch file.\n";
				}
			}
		}
		
		
	}

	void InputReader::_incorrectSyntax()
	{
		std::cout << "The syntax of the command is incorrect." << std::endl;
	}

	void InputReader::_error()
	{
		std::cout << "error" << std::endl;
	}
}