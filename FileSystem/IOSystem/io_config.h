#pragma once

namespace filesystem::io::config {
	// mapping is simple - one logical block per one physical
	// CHS https://www.partitionwizard.com/help/what-is-chs.html
	const int T_MAX = 6;    // tracks per cylinder - number of platters - half of number of heads per cylinder
	const int C_MAX = 32;   // cylinder number - number of tracks per platter
	const int S_MAX = 35;   // sectors per track
	const int B_MAX = 72;   // bytes per sector

	// LBA
	const int MAX_BLOCK_SIZE = 128;  // maximum size of logical block
	const int MAX_BLOCKS_NUM = 128;  // maximum amount of logical blocks
}

