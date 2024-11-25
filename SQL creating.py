import sqlite3
import os

# 定义全局数据库路径
DB_PATH = "/Users/zzy/Desktop/BTC_catch/addresses.db"

# Step 1: 创建数据库和表
def create_database():
    # 确保数据库路径的目录存在
    db_dir = os.path.dirname(DB_PATH)
    os.makedirs(db_dir, exist_ok=True)

    conn = sqlite3.connect(DB_PATH)  # 连接数据库（如果不存在会自动创建）
    cursor = conn.cursor()

    # 创建地址表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS btc_addresses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            address TEXT UNIQUE NOT NULL
        )
    """)

    conn.commit()
    conn.close()
    print(f"Database and table created successfully at: {DB_PATH}")

# Step 2: 批量导入数据
def import_addresses_to_db(filenames):
    conn = sqlite3.connect(DB_PATH)  # 确保路径一致
    cursor = conn.cursor()

    # 定义地址类别
    categories = ['P2PKH', 'P2SH', 'Bech32']

    for category, filename in zip(categories, filenames):
        print(f"Importing {category} addresses from {filename}...")

        try:
            # 打开文件并逐行读取
            with open(filename, "r") as file:
                addresses = [(category, line.strip()) for line in file]

            # 批量插入，忽略重复数据
            cursor.executemany("""
                INSERT OR IGNORE INTO btc_addresses (category, address)
                VALUES (?, ?)
            """, addresses)

        except FileNotFoundError:
            print(f"File {filename} not found. Skipping...")
        except Exception as e:
            print(f"Error importing from {filename}: {e}")

    conn.commit()
    conn.close()
    print("All addresses imported successfully.")

# Step 3: 查询地址
def query_address(address):
    conn = sqlite3.connect(DB_PATH)  # 确保路径一致
    cursor = conn.cursor()

    # 查询地址是否存在以及类别
    cursor.execute("SELECT category FROM btc_addresses WHERE address = ?", (address,))
    result = cursor.fetchone()

    conn.close()

    if result:
        print(f"Address {address} found in category: {result[0]}")
    else:
        print(f"Address {address} not found in the database.")

# Step 4: 主函数入口
def main():
    # 替换为你的地址文件路径
    filenames = [
        "/Users/zzy/Desktop/BTC_catch/p2pkh_addresses.txt",
        "/Users/zzy/Desktop/BTC_catch/p2sh_addresses.txt",
        "/Users/zzy/Desktop/BTC_catch/bech32_addresses.txt"
    ]

    # 创建数据库和表
    create_database()

    # 导入地址数据
    import_addresses_to_db(filenames)

    # 测试查询功能
    test_address = "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"  # 示例地址
    query_address(test_address)

if __name__ == "__main__":
    main()
