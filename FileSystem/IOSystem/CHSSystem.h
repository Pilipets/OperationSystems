#pragma once

#include <tuple>

#include "IOSystem.h"
#include "io_config.h"

namespace filesystem::io {
	using namespace io::config;
	class CHSSystem : public IOSystemInterface {
	private:
		bool _check_config();
		void _save_system_state() override;
		void _restore_system_state() override;
		typedef std::tuple<int, int, int> chs_idx;
		chs_idx lba_to_chs(int logical_block_idx);
	public:
		CHSSystem();
		~CHSSystem();
		void init(int c, int t, int s, int b, const char *system_state_path);

		void read_block(int block_idx, char *copy_to_ptr) override;
		void write_block(int block_idx, char *copy_from_ptr) override;

	private:
		int c, t, s, b;
		char _ldisk[C_MAX][T_MAX][S_MAX][B_MAX];
	};
}