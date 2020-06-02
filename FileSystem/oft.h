#pragma once

#include <array>
#include "fs_config.h"

namespace filesystem::components {
	using namespace config;
	struct OFTEntry {
		OFTEntry();
		char read_write_buffer[BLOCK_SIZE];
		int fpos, fd_index, read_block_arr_idx = -1;
		bool block_read, block_modified;
	};

	class OFT {
	public:
		int getOftIndex(int fd_index);
		int addFile(int fd_index);

		OFTEntry* getFile(int oft_index);
		void removeOftEntry(int oft_index);

		int getNumOFOpenFiles();
		int getFDIndexByOftIndex(int oft_index);
	private:
		int oft_size = 0;
		std::array<OFTEntry, FD_OPENED_LIMIT> entries_buf;
	};
}