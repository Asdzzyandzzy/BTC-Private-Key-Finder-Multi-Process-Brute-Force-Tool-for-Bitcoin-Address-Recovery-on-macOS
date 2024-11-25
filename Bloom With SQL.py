import hashlib
import os
import secp256k1
import base58
import bech32  # Bech32 library
import time
import multiprocessing
import math
import sqlite3  # 用于与 SQLite 数据库交互

# Define the ORDER of the SECP256k1 curve
ORDER = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

# Bloom Filter implementation in Python
class SimpleBloomFilter:
    def __init__(self, size, hash_count):
        self.size = size
        self.hash_count = hash_count
        self.bit_array = [0] * size

    def _hash(self, item, seed):
        result = hashlib.md5(f"{item}{seed}".encode()).hexdigest()
        return int(result, 16) % self.size

    def add(self, item):
        for i in range(self.hash_count):
            index = self._hash(item, i)
            self.bit_array[index] = 1

    def check(self, item):
        for i in range(self.hash_count):
            index = self._hash(item, i)
            if self.bit_array[index] == 0:
                return False
        return True

# Dynamically calculate Bloom Filter parameters
def calculate_bloom_parameters(address_count, false_positive_rate=0.01):
    if address_count == 0:
        return 1, 1  # Minimal size for empty files
    m = -int(address_count * (math.log(false_positive_rate) / (math.log(2) ** 2)))  # Bit array size
    k = max(1, int((m / address_count) * math.log(2)))  # Number of hash functions
    return m, k

# Load Bitcoin addresses into separate Bloom Filters and precise sets from SQL
def load_addresses_from_sql(db_path, false_positive_rate=0.01):
    categories = ['P2PKH', 'P2SH', 'Bech32']
    bloom_filters = {}
    precise_sets = {}

    # 连接 SQLite 数据库
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    for category in categories:
        # 查询该类别的地址
        cursor.execute("SELECT address FROM btc_addresses WHERE category = ?", (category,))
        addresses = [row[0] for row in cursor.fetchall()]
        address_count = len(addresses)

        # 根据地址数量动态计算 Bloom Filter 参数
        m, k = calculate_bloom_parameters(address_count, false_positive_rate)
        bloom_filter = SimpleBloomFilter(size=m, hash_count=k)
        precise_set = set(addresses)

        # 将地址加入 Bloom Filter 和精确集合
        for address in addresses:
            bloom_filter.add(address)

        bloom_filters[category] = bloom_filter
        precise_sets[category] = precise_set
        print(f"Category {category}: Loaded {address_count} addresses with Bloom Filter size {m} and {k} hash functions.")

    conn.close()
    return bloom_filters, precise_sets

# Convert a public key to different Bitcoin address formats
def public_key_to_addresses(public_key):
    # P2PKH
    sha256 = hashlib.sha256(public_key).digest()
    ripemd160 = hashlib.new('ripemd160', sha256).digest()
    p2pkh = base58.b58encode_check(b'\x00' + ripemd160).decode('utf-8')

    # P2SH (placeholder script hash)
    p2sh_script = hashlib.new('ripemd160', hashlib.sha256(b'\x00' + ripemd160).digest()).digest()
    p2sh = base58.b58encode_check(b'\x05' + p2sh_script).decode('utf-8')

    # Bech32 (SegWit native address)
    bech32_address = bech32.encode('bc', 0, ripemd160)

    return p2pkh, p2sh, bech32_address

# Core brute-force logic, testing random private keys against the Bloom Filters and precise sets
def try_private_keys_batch(num_keys, bloom_filters, precise_sets):
    bloom_checks = 0
    secondary_checks = 0

    for _ in range(num_keys):
        private_key_int = int.from_bytes(os.urandom(32), 'big')
        if private_key_int >= ORDER:
            continue  # Skip invalid private keys
        private_key_bytes = private_key_int.to_bytes(32, 'big')
        privkey = secp256k1.PrivateKey(private_key_bytes, raw=True)
        public_key = privkey.pubkey.serialize(compressed=False)  # Uncompressed public key

        # Generate P2PKH, P2SH, and Bech32 addresses
        p2pkh, p2sh, bech32_address = public_key_to_addresses(public_key)

        # Check each address against its respective Bloom Filter and precise set
        for category, address in zip(['P2PKH', 'P2SH', 'Bech32'], [p2pkh, p2sh, bech32_address]):
            bloom_checks += 1  # Increment total Bloom filter checks
            if bloom_filters[category].check(address):
                secondary_checks += 1  # Increment secondary check count
                if address in precise_sets[category]:
                    print(f"[Match Found] Address: {address} (Category: {category})")
                    print(f"[Private Key (Hex)] {private_key_bytes.hex()}")
                    return private_key_bytes.hex(), bloom_checks, secondary_checks
    return None, bloom_checks, secondary_checks

# Brute-force random private keys using multiprocessing
def find_matching_private_key(bloom_filters, precise_sets, total_processes=8, keys_per_process=100000):
    round_number = 0

    while True:
        start_time = time.time()
        with multiprocessing.Pool(processes=total_processes) as pool:
            results = pool.starmap(
                try_private_keys_batch,
                [(keys_per_process, bloom_filters, precise_sets) for _ in range(total_processes)]
            )

        total_bloom_checks = 0
        total_secondary_checks = 0
        match_found = None

        for result in results:
            private_key, bloom_checks, secondary_checks = result
            total_bloom_checks += bloom_checks
            total_secondary_checks += secondary_checks
            if private_key:
                match_found = private_key

        if match_found:
            print("[Match Found] A matching private key was found. Stopping all processes.")
            return match_found

        end_time = time.time()
        elapsed_time = end_time - start_time
        check_ratio = total_secondary_checks / total_bloom_checks if total_bloom_checks > 0 else 0

        print(f"Round {round_number + 1} completed. Time: {elapsed_time:.2f} seconds, Speed: {keys_per_process * total_processes * 13200000 / elapsed_time:.2f} keys/s.")
        print(f"Total Bloom Checks: {total_bloom_checks}, Total Secondary Checks: {total_secondary_checks}, Check Ratio: {check_ratio:.2%}")
        round_number += 1

def main():
    # SQL 数据库路径
    db_path = "/Users/zzy/Desktop/BTC_catch/addresses.db"

    print("Loading addresses into separate Bloom Filters from SQL database...")
    bloom_filters, precise_sets = load_addresses_from_sql(db_path)
    print(f"Bloom Filters initialized for categories: {list(bloom_filters.keys())}.")

    # Start brute-force search
    total_processes = multiprocessing.cpu_count()
    print(f"Using {total_processes} processes.")
    find_matching_private_key(bloom_filters, precise_sets, total_processes=total_processes, keys_per_process=100000)

if __name__ == "__main__":
    main()
