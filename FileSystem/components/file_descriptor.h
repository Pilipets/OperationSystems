#pragma once

#include "../fs_config.h"

namespace filesystem::components {
	using namespace config;
	struct FileDescriptor {
		int file_length = -1;
		int arr_block_num[MAX_FILE_BLOCKS];
	};
}
