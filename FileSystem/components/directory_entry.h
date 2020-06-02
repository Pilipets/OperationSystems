#pragma once

#include "../fs_config.h"
#include <string.h>

namespace filesystem::components {
	using namespace config;
	struct DirectoryEntry {
		DirectoryEntry() = default;
		DirectoryEntry(int fd_index, const char* filename_ptr) :
			fd_index(fd_index) {
			strncpy(this->filename, filename_ptr, MAX_FILENAME_LENGTH);
		}
		char filename[MAX_FILENAME_LENGTH];
		int fd_index = -1;
	};
}
