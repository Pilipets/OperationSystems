#pragma once

#include "../fs_config.h"
namespace filesystem::io {
    class IOSystemInterface;
}
namespace filesystem::disk_utils {
	using namespace config;
    class RawDiskStream {
    public:
        RawDiskStream(io::IOSystemInterface* ios, int block_idx, int shift);
    protected:
        char block_buf[BLOCK_SIZE];
        io::IOSystemInterface* ios;
        int block_idx, shift;
        bool block_read;
    };

    class RawDiskWriter : public RawDiskStream {
    public:
        RawDiskWriter(io::IOSystemInterface* ios, int block_idx, int shift);
		~RawDiskWriter();
        void flush();
        void write(void* read_ptr, int bytes);
    };

    class RawDiskReader : public RawDiskStream {
    public:
        RawDiskReader(io::IOSystemInterface* ios, int block_idx, int shift);

        void read(void* write_ptr, int bytes);
        void clear();
    };
}