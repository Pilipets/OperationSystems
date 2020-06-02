#pragma once

#include "IOSystem.h"
#include "io_config.h"

namespace filesystem::io {
	using namespace io::config;
	class LBASystem : public IOSystemInterface {
	private:
		bool _check_config();
		void _save_system_state() override;
		void _restore_system_state() override;
	public:
		LBASystem();
		~LBASystem();
		void init(int blocks_num, int block_len, const char *system_state_path);

		void read_block(int block_idx, char *copy_to_ptr) override;
		void write_block(int block_idx, char *copy_from_ptr) override;

	protected:
		int _blocks_num;
		int _block_len;
		char _ldisk[MAX_BLOCKS_NUM][MAX_BLOCK_SIZE];
	};
}