import hashlib
import struct

#Bitcoin Blockchain protocol
#Bitcoin uses Little-Endien
magic_num_size = 4
block_size = 4
version_size = 4
block_header_size = 80
sha256_size = 32
merkle_root_size = 32
time_stamp_size = 4
difficulty_size = 4
nonce_size = 4
tx_version_size = 4
witness_flag_size = 2 # optional data
# in_count = vli(1, 9) 1-9 bytes
# transaction_counter = vli(1, 9) 1-9 bytes

txout_index_size = 4
# txin_script_length = vli(1, 9) 1-9 bytes
sequence_number_size = 4
value_size = 8
lock_time_size = 4
#--------------------------

def read_little_endian(f, bytes):
    bytes = f.read(bytes)
    return bytes[::-1]

def hexify_bytes(bytes):
    return bytes.hex().upper()

#read variable-length integer https://bitcointalk.org/index.php?topic=32849.msg410480#msg410480
def read_vli(f):
    var_int = ord(f.read(1))
    if var_int <= 0xfc:
        return var_int
    if var_int == 0xfd:
        return unpack_one("<xH",  f.read(2))
    if var_int == 0xfe:
        return unpack_one("<xI", f.read(4))
    if var_int == 0xff:
        return unpack_one("<xQ", f.read(8))

class BlockHeader:
    def read(self, f):
        #Compute blockheader hash - SHA256(SHA256(block_header)) with OPENSSL
        bytes = f.read(block_header_size)
        #SHA family uses Big-Endian format
        hash = hashlib.new('sha256', bytes).digest()
        bytes = hashlib.new('sha256', bytes).digest()
        self.cur_block_hash = hexify_bytes(bytes[::-1]) # Back to Little-Endian format bytes[::-1]
        f.seek(-block_header_size, 1)
        print('cur_block_hash=', )

        #Version
        bytes = f.read(version_size)
        self.version_number = unpack_one('<I', bytes)

        #Previous-block hash
        self.previous_block_hash = hexify_bytes(read_little_endian(f, sha256_size))

        #Merkle-root
        self.merkle_root = hexify_bytes(read_little_endian(f, merkle_root_size))

        #Timestamp, difficulty, nonce
        self.time_stamp = unpack_one('<I', f.read(time_stamp_size))
        self.difficulty = unpack_one('<I', f.read(difficulty_size))
        self.nonce = unpack_one('<I', f.read(nonce_size))

class Transaction:
    class InputTx:
        def read(self, f):
            #Previous Transaction hash
            self.pre_tx_hash = hexify_bytes(read_little_endian(f, sha256_size))

            #Previous Txout-index
            self.txout_index = unpack_one('<I', f.read(txout_index_size))

            #Txin-script length
            self.script_length = read_vli(f)

            #Read txin-script
            self.script = hexify_bytes(f.read(self.script_length))

            #Sequence number
            self.sequence_number = unpack_one('<I', f.read(sequence_number_size))

    class OutputTx:
        def read(self, f):
            #value non negative integer giving the number of Satoshis(BTC/10^8) to be transfered
            self.value = unpack_one('<Q', f.read(value_size))

            #Txout-script length
            self.script_length = read_vli(f)

            #Read txout-script
            self.script = hexify_bytes(f.read(self.script_length))

    def read(self, f):
        #TX version number
        self.tx_version = unpack_one('<i', f.read(tx_version_size))

        #Witness flag that might be absent 2 bytes(0x0001 if present)
        flag = unpack_one('>h', f.read(witness_flag_size))

        #Witness flag is missed
        if flag != 1:
            self.witness_flag = False
            f.seek(-witness_flag_size, 1)
        else:
            self.witness_flag = True

        #In counter, variable length integer
        self.in_count = read_vli(f)

        #Read all input transactions
        for _ in range(self.in_count):
            inTx = Transaction.InputTx()
            inTx.read(f)
            
        #Out counter, variable length integer
        self.out_count = read_vli(f)

        #Read all output transactions
        for _ in range(self.in_count):
            outTx = Transaction.OutputTx()
            outTx.read(f)

        # Witnesses	A list of witnesses, 1 for each input, omitted if flag above is missing
        if self.witness_flag:
            for i in range(self.in_count):
                witness_len = read_vli(f)
                for j in range(witness_len):
                    witness_item_len = read_vli()
                    witness_data = hexify_bytes(f.read(witness_item_len))


        #Lock-time if non-zero and sequence numbers are < 0xFFFFFFFF: block height or timestamp when transaction is final
        self.lock_time = unpack_one('<I', f.read(lock_time_size))

class Block:
    def read(self, f):
        #Magic number
        self.magic_number = unpack_one('<I', f.read(magic_num_size))

        #Block size
        self.block_size = unpack_one('<I', f.read(block_size))
        print('Block size= ', hex(self.magic_number))

        #Transaction counter
        header = BlockHeader()
        header.read(f)
        
        #Transaction_counter - variable length(1-9 bytes)
        self.transaction_counter = read_vli(f)
        for _ in range(self.transaction_counter):
            tx = Transaction()
            tx.read(f)        