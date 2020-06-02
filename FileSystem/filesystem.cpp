#include "filesystem.h"

#include <fstream>
#include <cmath>
#include <bitset>
#include "components/file_descriptor.h"
#include "utils/disk_utils.h"
#include "utils/errors.h"
#include "fs_config.h"
#include <string>
#include <cstring>

namespace filesystem {
	using namespace config;
	using namespace std;
	using namespace errors;

	FileSystem::FileSystem() {
		loadFS(SYSTEM_PATH);
	}

	FileSystem::~FileSystem(){
		_closeAllFiles();
	}

	FileDescriptor FileSystem::_getDescriptorByIndex(int fd_index) {
		// compute the descriptor offset
		int bytes = sizeof(std::bitset<DISC_BLOCKS_NUM>) + sizeof(components::FileDescriptor)*fd_index;
		int read_block_idx = bytes/BLOCK_SIZE, shift = bytes % BLOCK_SIZE;
		FileDescriptor fd;

		disk_utils::RawDiskReader fin(&ios, read_block_idx, shift);
		fin.read(&fd, sizeof(FileDescriptor));
		return fd;
	}

	/*
		Save filesystem data to disk: write bitmap,
		directory descriptor,empty file descriptors.
	*/
	void FileSystem::_initFileSystem() {
		disk_utils::RawDiskWriter fout(&ios, 0, 0);

		// mark first k first bits as occupied
		int range = (1 << SYSTEM_BLOCKS_NUM) - 1;
		std::bitset<DISC_BLOCKS_NUM> free_blocks_set(range);
		fout.write(&free_blocks_set, sizeof(std::bitset<DISC_BLOCKS_NUM>));

		// write directory descriptor to the disk
		FileDescriptor f_dir;
		f_dir.file_length = 0;
		fout.write(&f_dir, sizeof(FileDescriptor));

		//write remaining empty descriptors to the disk
		FileDescriptor f_descriptor;
		for (int i = 0; i < FD_CREATED_LIMIT; ++i)
			fout.write(&f_descriptor, sizeof(FileDescriptor));
		fout.flush();

		oft.addFile(0);
	}

	void FileSystem::_restoreFileSystem()
	{
		FileDescriptor dir_fd = _getDescriptorByIndex(0);
		oft.addFile(0);
	}

	int FileSystem::_readFromFile(OFTEntry* f_entry, const FileDescriptor& fd, void* write_ptr, int bytes) {
        // Check if file has enough bytes to read
        if (fd.file_length - f_entry->fpos < bytes) {
            bytes = fd.file_length - f_entry->fpos;
        }
        int count_bytes = bytes;

        char* write_to = static_cast<char*>(write_ptr);
        int arr_block_idx = f_entry->fpos/BLOCK_SIZE, shift = f_entry->fpos % BLOCK_SIZE;

        if(f_entry->read_block_arr_idx != arr_block_idx){
            if(f_entry->block_modified) {
                ios.write_block(fd.arr_block_num[f_entry->read_block_arr_idx],f_entry->read_write_buffer);
                f_entry->block_modified = false;
            }
            f_entry->block_read = false;
            f_entry->read_block_arr_idx = -1;
        }

        if (shift || f_entry->block_modified) {
            if (!f_entry->block_read) {
                // if block isn't read yet, read the respective block
                ios.read_block(fd.arr_block_num[arr_block_idx], f_entry->read_write_buffer);
                f_entry->block_read = true; // block isn't modified for sure
                f_entry->read_block_arr_idx = arr_block_idx;
            }
            int prefix_size = min(BLOCK_SIZE-shift, bytes);
            memcpy(write_to, f_entry->read_write_buffer + shift, prefix_size);
            write_to += prefix_size; bytes -= prefix_size;

            f_entry->fpos += prefix_size;
            shift = (shift + prefix_size) % BLOCK_SIZE;
            if(shift) {
                // bytes < BLOCK_SIZE - shift
                return count_bytes;
            }

            if (f_entry->block_modified) {
                // write the buffer into the appropriate block on disk (if modified),
                ios.write_block(fd.arr_block_num[arr_block_idx], f_entry->read_write_buffer);
                f_entry->block_modified = false;
            }
            arr_block_idx += 1;
            f_entry->block_read = false; f_entry->read_block_arr_idx = -1;
        }

        // Left bytes to read
        while (bytes >= BLOCK_SIZE) {
            // Here we may use external call where we pass f_entry->read_write_buffer
            ios.read_block(fd.arr_block_num[arr_block_idx], f_entry->read_write_buffer);
            f_entry->fpos += BLOCK_SIZE; f_entry->read_block_arr_idx = arr_block_idx;
            f_entry->block_read = true; arr_block_idx += 1;

            memcpy(write_to, f_entry->read_write_buffer, BLOCK_SIZE);
            write_to += BLOCK_SIZE; bytes -= BLOCK_SIZE;
        }

        if (bytes) {
            // read remaining portion and buffer
            ios.read_block(fd.arr_block_num[arr_block_idx], f_entry->read_write_buffer);
            memcpy(write_to, f_entry->read_write_buffer, bytes);
            f_entry->fpos += bytes; f_entry->block_read = true;
            f_entry->read_block_arr_idx = arr_block_idx;
        }
        return count_bytes;
	}

    int FileSystem::_writeToFile(OFTEntry *entry, FileDescriptor &fd, void *read_ptr, int bytes) {
        // before reading/writing blocks, we must ensure the file can store requsted bytes
        // and allocate the necessary bytes
        if (bytes + entry->fpos > BLOCK_SIZE * MAX_FILE_BLOCKS) {
            bytes = BLOCK_SIZE * MAX_FILE_BLOCKS - entry->fpos;
        }

        int num_of_bytes_written = 0;

        char *read_from = static_cast<char *>(read_ptr);
        int arr_block_idx = entry->fpos / BLOCK_SIZE, offset = entry->fpos % BLOCK_SIZE;
        int tmp_file_length = fd.file_length;

        while (bytes + offset > BLOCK_SIZE) {
            int bytes_to_alloc = max(0, BLOCK_SIZE - offset - fd.file_length + entry->fpos);
            if (_reserveBytesForFile(&fd, bytes_to_alloc) == RetStatus::OK) {
                if (entry->read_block_arr_idx != arr_block_idx) {
                    if(entry->block_modified){
                        ios.write_block(fd.arr_block_num[entry->read_block_arr_idx],entry->read_write_buffer);
                        entry->block_modified = false;
                    }
                    entry->block_read = false;
                    entry->read_block_arr_idx = -1;
                }
                if(!entry->block_read){
                    ios.read_block(fd.arr_block_num[arr_block_idx], entry->read_write_buffer);
                    entry->block_read = true;
                    entry->read_block_arr_idx = arr_block_idx;
                }

                memcpy(entry->read_write_buffer + offset, read_from, BLOCK_SIZE - offset);
                num_of_bytes_written += BLOCK_SIZE - offset;
                bytes -= BLOCK_SIZE - offset;
                entry->fpos += BLOCK_SIZE - offset;
                read_from += BLOCK_SIZE - offset;
                offset = 0;

                ios.write_block(fd.arr_block_num[arr_block_idx], entry->read_write_buffer);
                arr_block_idx++;
                entry->block_modified = false;
                entry->block_read = false;
                if (entry->fpos > fd.file_length) {
                    fd.file_length = entry->fpos;
                }
            } else {
                break;
            }
        }

        int bytes_to_alloc = max(0, bytes - fd.file_length + entry->fpos);
        if (_reserveBytesForFile(&fd, bytes_to_alloc) == RetStatus::OK) {
            if (entry->read_block_arr_idx != arr_block_idx) {
                if(entry->block_modified){
                    ios.write_block(fd.arr_block_num[entry->read_block_arr_idx],entry->read_write_buffer);
                    entry->block_modified = false;
                }
                entry->block_read = false;
                entry->read_block_arr_idx = -1;
            }
            if(!entry->block_read){
                ios.read_block(fd.arr_block_num[arr_block_idx], entry->read_write_buffer);
                entry->block_read = true;
                entry->read_block_arr_idx = arr_block_idx;
            }
            memcpy(entry->read_write_buffer + offset, read_from, bytes);
            num_of_bytes_written += bytes;
            if (bytes == BLOCK_SIZE) {
                ios.write_block(fd.arr_block_num[arr_block_idx], entry->read_write_buffer);
                entry->block_modified = false;
                entry->block_read = true;
            } else {
                entry->block_read = true;
                entry->block_modified = true;
            }
            entry->fpos += bytes;
        }

        if (entry->fpos > tmp_file_length) {
            fd.file_length = entry->fpos;
            int fd_shift =
                    sizeof(std::bitset<DISC_BLOCKS_NUM>) + sizeof(components::FileDescriptor) * entry->fd_index;
            int fd_block_idx = fd_shift / BLOCK_SIZE;
            int fd_offset = fd_shift % BLOCK_SIZE;
            disk_utils::RawDiskWriter fout(&ios, fd_block_idx, fd_offset);
            fout.write(&fd, sizeof(FileDescriptor));
        }

        return num_of_bytes_written;
    }

	int FileSystem::_reserveBytesForFile(FileDescriptor* fd, int bytes)
	{
		//check if file can store requsted bytes
		if (fd->file_length + bytes <= BLOCK_SIZE * MAX_FILE_BLOCKS) {
			int num_of_occupied_blocks = (fd->file_length + BLOCK_SIZE - 1) / BLOCK_SIZE;
			int available_allocated_bytes = num_of_occupied_blocks * BLOCK_SIZE - fd->file_length;
			bytes -= available_allocated_bytes;
			//calculate num of new blocks that we need
			int num_of_new_blocks = (bytes + BLOCK_SIZE - 1) / BLOCK_SIZE;

			if (bytes < 0 || num_of_new_blocks == 0) {
				// No need to read the bitset, add any blocks
				return RetStatus::OK;
			}

			std::bitset<DISC_BLOCKS_NUM> free_blocks_set;
			disk_utils::RawDiskReader fin(&ios, 0, 0);
			fin.read(&free_blocks_set, sizeof(std::bitset<DISC_BLOCKS_NUM>));

			vector<int>free_blocks_idx;
			for (int i = SYSTEM_BLOCKS_NUM; i < DISC_BLOCKS_NUM; i++) {
				if (free_blocks_idx.size() == num_of_new_blocks) {
					break;
				}
				else if (free_blocks_set[i] == 0) {
					free_blocks_idx.push_back(i);
				}
			}
			//if we found all blocks that we need - reserve it
			if (free_blocks_idx.size() == num_of_new_blocks) {
				for (int i : free_blocks_idx) {
					fd->arr_block_num[num_of_occupied_blocks++] = i;
					free_blocks_set[i] = 1;
				}
				disk_utils::RawDiskWriter fout(&ios, 0, 0);
				fout.write(&free_blocks_set, sizeof(std::bitset<DISC_BLOCKS_NUM>));
				return RetStatus::OK;
			}
			else {
				return RetStatus::FAIL;
			}
		}
		else {
			return RetStatus::FAIL;
		}
	}

	int FileSystem::read(int oft_index, void* main_mem_ptr, int bytes) {
		int fd_index = oft.getFDIndexByOftIndex(oft_index);
		if (bytes <= 0 || fd_index == -1) {
			return RetStatus::FAIL;
		}
		OFTEntry* file_entry = oft.getFile(oft_index);
		FileDescriptor fd = _getDescriptorByIndex(fd_index);
		return _readFromFile(file_entry, fd, main_mem_ptr, bytes);
	}

	int FileSystem::write(int oft_index, void* main_mem_ptr, int bytes) {
		int fd_index = oft.getFDIndexByOftIndex(oft_index);
		if (bytes <= 0 || fd_index == -1) {
			return RetStatus::FAIL;
		}
		OFTEntry* file_entry = oft.getFile(oft_index);
		FileDescriptor fd = _getDescriptorByIndex(fd_index);
		return _writeToFile(file_entry, fd, main_mem_ptr, bytes);
	}

	std::pair<DirectoryEntry, int> FileSystem::_findFileInDirectory(const char* filename)
	{
		OFTEntry* dir_oft_entry = oft.getFile(0);
		FileDescriptor dir_fd = _getDescriptorByIndex(0);
		_lseek(dir_oft_entry,dir_fd, 0);
		int num_of_files_in_dir = dir_fd.file_length / sizeof(DirectoryEntry);
		int dir_entry_idx = 0;
		for (int i = 0; i < num_of_files_in_dir; i++) {
			DirectoryEntry cur_dir_entry;
			_readFromFile(dir_oft_entry, dir_fd, &cur_dir_entry, sizeof(DirectoryEntry));
			if (std::strncmp(cur_dir_entry.filename, filename, MAX_FILENAME_LENGTH) == 0) {
				dir_entry_idx = i;
				return std::make_pair(cur_dir_entry, dir_entry_idx);
			}
		}
		return std::make_pair(DirectoryEntry(), -1);
	}

	bool FileSystem::_fileExists(const char* filename)
	{
		ifstream fin(filename);
		if (fin.is_open()) {
			fin.close();
			return true;
		}
		return false;
	}

	void FileSystem::_closeAllFiles(){
		int oft_size = oft.getNumOFOpenFiles();
		if (oft_size == 0) {
			return;
		}
		for (int i = oft_size - 1; i >= 0; i--) {
			OFTEntry* file_entry = oft.getFile(i);
			close(file_entry->fd_index);
		}
	}

	int FileSystem::_lseek(OFTEntry* file_entry, const FileDescriptor& fd, int pos)
	{
		if (file_entry != nullptr) {
			if (pos < 0 || pos > fd.file_length) {
				return RetStatus::FAIL;
			}
			file_entry->fpos = pos;
			return RetStatus::OK;
		}
		else {
			return RetStatus::FAIL;
		}
	}

	int FileSystem::createFile(const char* filename)
	{
		FileDescriptor dir_fd = _getDescriptorByIndex(0);
		int num_files_created = dir_fd.file_length / sizeof(DirectoryEntry);
		if (num_files_created == FD_CREATED_LIMIT || _findFileInDirectory(filename).second != -1)
			return RetStatus::FAIL;

		// compute the offset before looking for empty descriptor
		int bytes = sizeof(std::bitset<DISC_BLOCKS_NUM>) + sizeof(components::FileDescriptor);
		int block_idx = bytes / BLOCK_SIZE, offset = bytes % BLOCK_SIZE;
		disk_utils::RawDiskReader fin(&ios, block_idx, offset);

		FileDescriptor free_fd;
		int free_fd_index = 0;
		for (int i = 0; i < FD_CREATED_LIMIT; ++i) {
			fin.read(&free_fd, sizeof(components::FileDescriptor));

			if (free_fd.file_length == -1) {
				// file descriptor isn't occupied
				free_fd_index = i + 1;
				free_fd.file_length = 0;
				break;
			}
		}
		if (!free_fd_index) {
			// zero free file descriptors found
			return RetStatus::FAIL;
		}

		DirectoryEntry new_entry(free_fd_index, filename);

		OFTEntry* dir = oft.getFile(0);
		_lseek(dir, _getDescriptorByIndex(0), num_files_created * sizeof(DirectoryEntry));

		if (_writeToFile(dir, dir_fd, &new_entry, sizeof(DirectoryEntry))) {
			bytes = sizeof(std::bitset<DISC_BLOCKS_NUM>) + sizeof(components::FileDescriptor)*free_fd_index;
			int free_fd_block_idx = bytes / BLOCK_SIZE;
			int free_fd_offset = bytes % BLOCK_SIZE;
			disk_utils::RawDiskWriter fout(&ios, free_fd_block_idx, free_fd_offset);
			fout.write(&free_fd, sizeof(FileDescriptor));
			return RetStatus::OK;
		}
		else {
			return RetStatus::FAIL;
		}
	}

	int FileSystem::destroyFile(const char* filename)
	{
		std::pair<DirectoryEntry, int> dir_entry_info = _findFileInDirectory(filename);
		DirectoryEntry file_dir_entry = dir_entry_info.first;
		//if not found with such filename in directory or file is open
		if (dir_entry_info.second == -1 || oft.getOftIndex(file_dir_entry.fd_index) != -1) {
			return RetStatus::FAIL;
		}

		//free occupied disk blocks in bitmap
		std::bitset<DISC_BLOCKS_NUM> free_blocks_set;
		disk_utils::RawDiskReader fin(&ios, 0, 0);
		fin.read(&free_blocks_set, sizeof(free_blocks_set));
		bool bitset_is_modified = false;

		FileDescriptor fd = _getDescriptorByIndex(file_dir_entry.fd_index);
		int num_of_occupied_blocks = (fd.file_length + BLOCK_SIZE - 1) / BLOCK_SIZE;
		if (num_of_occupied_blocks) {
			for (int i = 0; i < num_of_occupied_blocks; i++) {
				free_blocks_set[fd.arr_block_num[i]] = 0;
			}
			bitset_is_modified = true;
		}

		//free occupied file descriptor
		int bytes = sizeof(std::bitset<DISC_BLOCKS_NUM>) + sizeof(components::FileDescriptor)*file_dir_entry.fd_index;
		int block_idx = bytes / BLOCK_SIZE, offset = bytes % BLOCK_SIZE;
		disk_utils::RawDiskWriter fout(&ios, block_idx, offset);

		FileDescriptor empty_fd;
		fout.write(&empty_fd, sizeof(FileDescriptor));
		fout.flush();

		//remove file entry from directory(swap last dir entry and entry of file which should be destroyed. Then decrease dir length)
		OFTEntry* dir_oft = oft.getFile(0);
		FileDescriptor dir_fd = _getDescriptorByIndex(0);
		int last_dir_entry_offset = dir_fd.file_length - sizeof(DirectoryEntry);
		_lseek(dir_oft, dir_fd, last_dir_entry_offset);
		DirectoryEntry last_dir_entry;
		_readFromFile(dir_oft, dir_fd, &last_dir_entry, sizeof(DirectoryEntry));
		int remove_file_offset = sizeof(DirectoryEntry) * dir_entry_info.second;
		_lseek(dir_oft, dir_fd, remove_file_offset);
		_writeToFile(dir_oft, dir_fd, &last_dir_entry, sizeof(DirectoryEntry));
		dir_fd.file_length -= sizeof(DirectoryEntry);

		//update directory descriptor
		int dir_length_before_destr = dir_fd.file_length + sizeof(DirectoryEntry);
		int num_of_dir_disk_blocks = (dir_length_before_destr + BLOCK_SIZE - 1) / BLOCK_SIZE;
		int free_space_in_dir = (num_of_dir_disk_blocks * BLOCK_SIZE) - dir_fd.file_length;
		//free disk dir blocks if we have empty
		while (free_space_in_dir >= BLOCK_SIZE) {
			free_space_in_dir -= BLOCK_SIZE;
			free_blocks_set[dir_fd.arr_block_num[num_of_dir_disk_blocks - 1]] = 0;
			num_of_dir_disk_blocks--;
			bitset_is_modified = true;
		}

		if (bitset_is_modified) {
			disk_utils::RawDiskWriter f(&ios, 0, 0);
			f.write(&free_blocks_set, sizeof(free_blocks_set));
			f.write(&dir_fd, sizeof(FileDescriptor));
		}
		else {
			bytes = sizeof(std::bitset<DISC_BLOCKS_NUM>);
			block_idx = bytes / BLOCK_SIZE;
			offset = bytes % BLOCK_SIZE;
			disk_utils::RawDiskWriter f(&ios, block_idx, offset);
			f.write(&dir_fd, sizeof(FileDescriptor));
		}

		return RetStatus::OK;
	}

	int FileSystem::lseek(int oft_index, int pos)
	{
		int fd_index = oft.getFDIndexByOftIndex(oft_index);
		if (fd_index == -1) {
			return RetStatus::FAIL;
		}
		OFTEntry* file_entry = oft.getFile(oft_index);
		FileDescriptor fd = _getDescriptorByIndex(fd_index);
		return _lseek(file_entry, fd, pos);
	}

	int FileSystem::open(const char* filename)
	{
		std::pair<DirectoryEntry, int> file = _findFileInDirectory(filename);
		if (file.second == -1) {
			return -1;
		}
		int fd_index = file.first.fd_index;
		int oft_index = oft.addFile(fd_index);
		return oft_index;
	}

	int FileSystem::close(int oft_index)
	{
		int fd_index = oft.getFDIndexByOftIndex(oft_index);
		if (fd_index == -1) {
			return RetStatus::FAIL;
		}
		FileDescriptor fd = _getDescriptorByIndex(fd_index);
		OFTEntry *file_entry = oft.getFile(oft_index);
		if (file_entry->block_modified) {
			ios.write_block(fd.arr_block_num[file_entry->fpos/BLOCK_SIZE], file_entry->read_write_buffer);
		} // todo
		oft.removeOftEntry(oft_index);
		return RetStatus::OK;
	}

	vector<std::string> FileSystem::getAllDirectoryFiles()
	{
		vector<std::string> filenames;
		OFTEntry* dir_oft_entry = oft.getFile(0);
		FileDescriptor dir_fd = _getDescriptorByIndex(0);
        _lseek(dir_oft_entry,dir_fd,0);
		int num_of_files_in_dir = dir_fd.file_length / sizeof(DirectoryEntry);
		for (int i = 0; i < num_of_files_in_dir; i++) {
			DirectoryEntry cur_dir_entry;
			_readFromFile(dir_oft_entry, dir_fd, &cur_dir_entry, sizeof(DirectoryEntry));
			FileDescriptor fd = _getDescriptorByIndex(cur_dir_entry.fd_index);
			std::string s(cur_dir_entry.filename);
			s.push_back(' ');
			s += std::to_string(fd.file_length);
			filenames.push_back(s);
		}
		return filenames;
	}

	int FileSystem::saveFS(const char* filename)
	{
		_closeAllFiles();
		ios.save_system_state(filename);
		return RetStatus::OK;
	}

	int FileSystem::loadFS(const char* filename)
	{
		//save current disk state
		_closeAllFiles();
		//init new disk state
		ios.init(DISC_BLOCKS_NUM, BLOCK_SIZE, filename);
		if (_fileExists(filename)) {
			_restoreFileSystem();
			return 1;
		}else {
			_initFileSystem();
			return 2;
		}
	}
}
