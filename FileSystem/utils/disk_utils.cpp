#include "disk_utils.h"

#include <algorithm>
#include <string.h>
using std::min;

#include "../IOSystem/IOSystem.h"

namespace filesystem::disk_utils {
    RawDiskStream::RawDiskStream(io::IOSystemInterface* ios, int block_idx, int shift) :
        ios(ios), block_idx(block_idx), shift(shift), block_read(false) {
    }

    RawDiskWriter::RawDiskWriter(io::IOSystemInterface* ios, int block_idx, int shift) :
        RawDiskStream(ios, block_idx, shift) {
    }

	RawDiskWriter::~RawDiskWriter() {
		if (block_read) {
			ios->write_block(block_idx, block_buf);
		}
	}

    void RawDiskWriter::flush() {
		if (block_read) {
			ios->write_block(block_idx, block_buf);
			block_read = false;
		}
    }

    void RawDiskWriter::write(void* read_ptr, int bytes) {
        char* read_from = static_cast<char*>(read_ptr);
		if (shift) {
			if (!block_read) {
				ios->read_block(block_idx, block_buf);
				block_read = true;
			}
            int prefix_size = min(BLOCK_SIZE-shift, bytes);
			memcpy(block_buf+shift, read_from, prefix_size);

            shift = (shift + prefix_size) % BLOCK_SIZE;
            if(shift) {
                // bytes < BLOCK_SIZE - shift
                return;
            }

            read_from += prefix_size; bytes -= prefix_size;
			ios->write_block(block_idx, block_buf);
            block_idx += 1; block_read = false;
		}

        while (bytes >= BLOCK_SIZE) {
            ios->write_block(block_idx, read_from);
			block_idx += 1;
            read_from += BLOCK_SIZE; bytes -= BLOCK_SIZE;
        }

        if (bytes) {
			ios->read_block(block_idx, block_buf);
            block_read = true;
            memcpy(block_buf, read_from, bytes);
            shift = bytes;
        }
    }

    RawDiskReader::RawDiskReader(io::IOSystemInterface* ios, int block_idx, int shift) :
        RawDiskStream(ios, block_idx, shift) {
    }

    void RawDiskReader::clear() {
        block_read = false;
    }
    
    void RawDiskReader::read(void* write_ptr, int bytes) {
        char* write_to = static_cast<char*>(write_ptr);
		if (shift) {
            if (!block_read) {
                ios->read_block(block_idx, block_buf);
                block_read = true;
            }
            int prefix_size = min(BLOCK_SIZE-shift, bytes);
			memcpy(write_to, block_buf + shift, prefix_size);

            shift = (shift + prefix_size) % BLOCK_SIZE;
            if(shift) {
                // bytes < BLOCK_SIZE - shift
                return;
            }

            write_to += prefix_size; bytes -= prefix_size;
            block_idx += 1; block_read = false;
		}

        while (bytes >= BLOCK_SIZE) {
            ios->read_block(block_idx, write_to);
			block_idx += 1;
            write_to += BLOCK_SIZE; bytes -= BLOCK_SIZE;
        }

        if (bytes) {
            ios->read_block(block_idx, block_buf);
            block_read = true;
            memcpy(write_to, block_buf, bytes);
            shift = bytes;
        }
    }
}