#include "CHSSystem.h"

#define loop(x,n) for(int x = 0; x < n; ++x)

#include <assert.h>
#include <string.h>
#include <stdio.h>

namespace filesystem::io {
	bool CHSSystem::_check_config() {
		return c > 0 && c <= C_MAX && t > 0 && t <= T_MAX
			&& s > 0 && s <= S_MAX && b > 0 && b <= B_MAX;
	}

	CHSSystem::chs_idx CHSSystem::lba_to_chs(int logical_block_idx) {
		assert(logical_block_idx >= 0 && logical_block_idx < MAX_BLOCKS_NUM);

		int c_idx = logical_block_idx / (2 * t * s);    // LBA / (HPC * SPT)
		int h_idx = (logical_block_idx / s) % (2 * t);  // (LBA / SPT) % HPC
		int s_idx = logical_block_idx % s + 1;          // (LBA % SPT) + 1
		return { c_idx, h_idx, s_idx };
	}


	CHSSystem::CHSSystem() :
		c(0), t(0), s(0), b(0) {
	}
	CHSSystem::~CHSSystem() {
		_clean_up();
	}

	void CHSSystem::init(int c, int t, int s, int b, const char * system_state_path) {
		this->c = c; this->s = s; this->t = t; this->b = b;
		assert(_check_config());

		IOSystemInterface::_init(system_state_path);
	}

	void CHSSystem::read_block(int block_idx, char * copy_to_ptr) {
		// map logical to physical, read physical
		assert(copy_to_ptr);

		auto[c_idx, h_idx, s_idx] = lba_to_chs(block_idx);
		memcpy(copy_to_ptr, _ldisk[c_idx][h_idx / 2][s_idx - 1], sizeof(char) * b);
	}

	void CHSSystem::write_block(int block_idx, char * copy_from_ptr) {
		// map logical to physical, write physical
		assert(copy_from_ptr);

		auto[c_idx, h_idx, s_idx] = lba_to_chs(block_idx);
		memcpy(_ldisk[c_idx][h_idx / 2][s_idx - 1], copy_from_ptr, sizeof(char) * b);
	}

	void CHSSystem::_save_system_state() {
		FILE *file_ptr;
		assert(file_ptr = fopen(_system_state_path, "wb"));

		fwrite(_ldisk, sizeof(_ldisk), 1, file_ptr);
		fclose(file_ptr);
	}

	void CHSSystem::_restore_system_state() {
		FILE *file_ptr;
		assert(file_ptr = fopen(_system_state_path, "rb"));

		fwrite(_ldisk, sizeof(_ldisk), 1, file_ptr);
		fclose(file_ptr);
	}
}
