#pragma once

#include <memory>
#include <utility>
#include <vector>

#include "oft.h"
#include "IOSystem/LBASystem.h"
#include "components/file_descriptor.h"
#include "components/directory_entry.h"

namespace filesystem {
	using namespace config;
	using namespace components;
	class FileSystem {
	private:
		void _initFileSystem();
		void _restoreFileSystem();

		FileDescriptor _getDescriptorByIndex(int fd_index);
		int _readFromFile(OFTEntry* entry, const FileDescriptor& fd, void* write_ptr, int bytes);
		int _writeToFile(OFTEntry* entry, FileDescriptor& fd, void* read_ptr, int bytes);
		int _reserveBytesForFile(FileDescriptor* fd, int bytes);
		std::pair<DirectoryEntry, int> _findFileInDirectory(const char* filename);
		bool _fileExists(const char* filename);
		void _closeAllFiles();
		int _lseek(OFTEntry* entry, const FileDescriptor& fd, int pos);
	public:
		FileSystem();
		~FileSystem();

		int createFile(const char* filename);
		int destroyFile(const char* filename);
		int read(int oft_index, void* main_mem_ptr, int bytes);
		int write(int oft_index, void* main_mem_ptr, int bytes);
		int lseek(int oft_index, int pos);
		int open(const char* filename);
		int close(int oft_index);

		std::vector<std::string> getAllDirectoryFiles();
		int saveFS(const char* filename);
		int loadFS(const char* filename);
	private:
		io::LBASystem ios;
		OFT oft;
	};
}