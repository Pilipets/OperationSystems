#include "../IOSystem/LBASystem.h"
#include "../IOSystem/io_config.h"

#include <cassert>
#include <cstring>
#include <set>
#include <iostream>
using namespace filesystem;
using namespace std;
using namespace io::config;

void test1() {
    // filesystem not initialized
    io::LBASystem ios_lba;
}

void test2() {
    io::LBASystem ios_lba;
    // path to file don't exist
    // ios_lba.init(1, 1, "dummy_path/");
    // file don't exist, new one is created
    ios_lba.init(1, 1, "dummy.txt");
}

void test3() {
    io::LBASystem ios_lba;
    // ios_lba.init(MAX_BLOCKS_NUM+1, MAX_BLOCK_SIZE + 1, "state.txt");
    // ios_lba.init(-1, -1, "dummy.txt"); // file exists
    // ios_lba.init(-1, -1, "dummy2.txt"); // file not exists
}


class TestIOSystem : public io::LBASystem {
public:
    int getBlocksNum() {
        return _blocks_num;
    }
    int getBlocksSize() {
        return _block_len;
    }
    auto getDisk() {
        return &_ldisk;
    }
    bool operator== (const TestIOSystem& other) {
        return _block_len == other._block_len &&_blocks_num == other._blocks_num
            && memcmp(&_ldisk, &other._ldisk, sizeof(_ldisk)) == 0;
    }
};

void test4() {
    char write_buf[MAX_BLOCK_SIZE] = {0};
    char read_buf[MAX_BLOCK_SIZE] = {0};

    char msg[] = "THis is a simple message";
    memcpy(write_buf, msg, sizeof(msg));

    char msg2[] = "20 len msg";
    memcpy(write_buf + sizeof(msg), msg2, sizeof(msg2));

    set<int> write_to_idx;
    // empty fs after writing/reading state
    {
        TestIOSystem ios;
        ios.init(MAX_BLOCKS_NUM, MAX_BLOCK_SIZE, "data2.txt");
        int block_num = 5 + rand() % (MAX_BLOCKS_NUM-10)/2;
        for(int i = 0; i < block_num; ++i) {
            int block_idx = rand() % MAX_BLOCKS_NUM;
            ios.write_block(block_idx, write_buf);
            write_to_idx.insert(block_idx);

            ios.read_block(block_idx, read_buf);
            assert (memcmp(read_buf, write_buf, sizeof(read_buf)) == 0);
        }
    }
    TestIOSystem new_ios;
    new_ios.init(MAX_BLOCKS_NUM, MAX_BLOCK_SIZE, "data2.txt");

    for (int index : write_to_idx) {
        new_ios.read_block(index, read_buf);
        assert (memcmp(read_buf, write_buf, sizeof(read_buf)) == 0);
    }
}

int main() {
    test4();
    return 0;
}