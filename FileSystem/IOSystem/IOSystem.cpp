#include "IOSystem.h"
// #define NDEBUG
#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>


namespace filesystem::io {
	bool IOSystemInterface::_file_exists(const char *path) const {
		struct stat buffer;
		return (stat(path, &buffer) == 0);
	}
	void IOSystemInterface::_init(const char * system_state_path) {
		assert(system_state_path);
		_system_state_path = system_state_path;

		if (_file_exists(_system_state_path)) {
			_restore_system_state();
		}
	}
	void IOSystemInterface::_clean_up()
	{
		if (!_system_state_path)
			return;
		_save_system_state();
	}
	IOSystemInterface::IOSystemInterface() :
		_system_state_path(nullptr) {
	}
	void IOSystemInterface::save_system_state(const char * filename) {
		_system_state_path = filename;
		_save_system_state();
	}
} // namespace filesystem::io