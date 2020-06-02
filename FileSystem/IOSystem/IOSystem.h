#pragma once

namespace filesystem::io {
	class IOSystemInterface {
	private:
		virtual void _save_system_state() = 0;
		virtual void _restore_system_state() = 0;
	protected:
		bool _file_exists(const char *path) const;
		void _init(const char* _system_state_path);
		void _clean_up();
	public:
		IOSystemInterface();

		/* Copies the logical disk block i into memory starting from the
		 * address specified by the pointer p. The number of characters copied
		 * equals to the logical block length. */
		virtual void read_block(int i, char *p) = 0;

		/* Copies the number of characters corresponding to the logical block length,
		 * starting from the memory address specified by the pointer p, into
		 * the logical disk block i. */
		virtual void write_block(int i, char *p) = 0;

		void save_system_state(const char* filename);
	protected:
		const char* _system_state_path;
	};
} // namespace filesystem::io
