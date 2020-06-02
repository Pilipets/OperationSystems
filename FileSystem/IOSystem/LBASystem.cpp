#include "LBASystem.h"

#include <assert.h>
#include <stdio.h>
#include <string.h>

namespace filesystem::io {
	bool LBASystem::_check_config() {
		return _block_len > 0 && _block_len <= MAX_BLOCK_SIZE
			&& _blocks_num > 0 && _blocks_num <= MAX_BLOCKS_NUM;
	}

	LBASystem::LBASystem() :
		_blocks_num(0), _block_len(0) {
	}

	void LBASystem::init(int blocks_num, int block_len, const char *system_state_path) {
		_blocks_num = blocks_num; _block_len = block_len;
		assert(_check_config());

		IOSystemInterface::_init(system_state_path);
	}

	LBASystem::~LBASystem() {
		_clean_up();
	}


	void LBASystem::read_block(int block_idx, char *copy_to_ptr) {
		assert(block_idx >= 0 && block_idx < _blocks_num && copy_to_ptr);

		memcpy(copy_to_ptr, _ldisk[block_idx], sizeof(char) * _block_len);
	}

	void LBASystem::write_block(int block_idx, char *copy_from_ptr) {
		assert(block_idx >= 0 && block_idx < _blocks_num && copy_from_ptr);

		memcpy(_ldisk[block_idx], copy_from_ptr, sizeof(char) * _block_len);
	}

	void LBASystem::_save_system_state() {
		FILE *file_ptr;
		assert(file_ptr = fopen(_system_state_path, "wb"));

		for (size_t i = 0; i < _blocks_num; ++i) {
			fwrite(_ldisk[i], _block_len, 1, file_ptr);
		}
		fclose(file_ptr);
	}

	void LBASystem::_restore_system_state() {
		FILE *file_ptr;
		assert(file_ptr = fopen(_system_state_path, "rb"));

		for (size_t i = 0; i < _blocks_num; ++i) {
			fread(_ldisk[i], _block_len, 1, file_ptr);
		}
		fclose(file_ptr);
	}
} // namespace filesystem::io