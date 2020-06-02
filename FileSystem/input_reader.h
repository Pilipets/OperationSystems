#pragma once
#include <iostream>
#include <string>
#include <sstream> 
#include "filesystem.h"

namespace filesystem {

    class InputReader
    {
    public:
        void start(int argc, char* argv[]);
    
    private:
        void _incorrectSyntax();
        void _error();
        FileSystem fs;
    };

}


