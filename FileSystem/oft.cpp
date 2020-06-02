#include "oft.h"

#include <algorithm>

namespace filesystem::components {
	OFTEntry::OFTEntry() :
		fpos(0), fd_index(-1),
		block_read(false), block_modified(false) {
	}

	int OFT::getOftIndex(int fd_index) {
		if (fd_index < 0 || fd_index > FD_OPENED_LIMIT)
			return -1;
		auto tail = entries_buf.begin() + FD_OPENED_LIMIT;
		auto it = std::find_if(entries_buf.begin(), tail,
			[fd_index](const OFTEntry& entry) {
				return entry.fd_index == fd_index;
			});

		if (it == tail)
			return -1;
		return it - entries_buf.begin();
	}

	OFTEntry* OFT::getFile(int oft_index) {
		return &entries_buf[oft_index];
	}

	int OFT::addFile(int fd_index)
	{
		//file exists or no space in oft
		if (oft_size == FD_OPENED_LIMIT || getOftIndex(fd_index) >= 0) {
			return -1;
		}
		OFTEntry new_file_entry;
		new_file_entry.fd_index = fd_index;

		for (int i = 0; i < FD_OPENED_LIMIT; i++) {
			if (entries_buf[i].fd_index == -1) {
				entries_buf[i] = new_file_entry;
				oft_size++;
				return i;
			}
		}
		return -1;
	}

	void OFT::removeOftEntry(int oft_index) {
		entries_buf[oft_index].fd_index = -1;
		entries_buf[oft_index].block_modified = 0;
		entries_buf[oft_index].block_read = 0;
		entries_buf[oft_index].fpos = 0;
		oft_size -= 1;
	}

	int OFT::getNumOFOpenFiles()
	{
		return oft_size;
	}
	int OFT::getFDIndexByOftIndex(int oft_index)
	{
		if (oft_index < 0 || oft_index >= FD_OPENED_LIMIT) {
			return -1;
		}
		return entries_buf[oft_index].fd_index;
	}
}

