import atexit
import random
import sqlite3
import os
from datetime import time

DB_FILE = "data.db"


def get_db_connection():
    """
    获取数据库连接，确保线程安全

    返回:
        sqlite3.Connection: 数据库连接对象
    """
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row  # 启用行工厂，支持字典式访问
    return conn


def init_db():
    """
    初始化数据库及所有表结构

    创建用户表、任务表、商店表，并初始化默认用户

    返回:
        bool: 是否是新创建的数据库文件
    """
    created = not os.path.exists(DB_FILE)
    conn = get_db_connection()
    c = conn.cursor()

    # 用户表：存储用户基本信息
    c.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE,           -- 用户名，唯一
        xp INTEGER DEFAULT 0,       -- 经验值
        level INTEGER DEFAULT 1,    -- 等级
        coins INTEGER DEFAULT 0,    -- 金币数量
        platinum_coins INTEGER DEFAULT 0  -- 铂金币数量
    )
    """)

    # 任务表：存储单次任务信息
    c.execute("""
    CREATE TABLE IF NOT EXISTS tasks(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,            -- 关联用户ID
        name TEXT,                  -- 任务名称
        xp_reward INTEGER,          -- 经验奖励
        platinum_reward INTEGER DEFAULT 0,  -- 铂金币奖励
        completed INTEGER DEFAULT 0,-- 完成状态：0未完成，1已完成
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    """)

    # 商店表：存储可兑换奖励
    c.execute("""
    CREATE TABLE IF NOT EXISTS rewards(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,            -- 关联用户ID
        name TEXT,                  -- 奖励名称
        price INTEGER,              -- 所需金币/铂金币
        currency_type TEXT DEFAULT 'coins',  -- 货币类型：'coins'(金币) 或 'platinum'(铂金币)
        completed INTEGER DEFAULT 0,-- 兑换状态：0未兑换，1已兑换
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    """)

    conn.commit()

    # 迁移：为现有用户添加 platinum_coins 列（如果不存在）
    try:
        c.execute("SELECT platinum_coins FROM users LIMIT 1")
    except sqlite3.OperationalError:
        # 列不存在，需要添加
        c.execute("ALTER TABLE users ADD COLUMN platinum_coins INTEGER DEFAULT 0")
        conn.commit()
        print("已添加 platinum_coins 列到 users 表")

    # 迁移：为现有任务添加 platinum_reward 列（如果不存在）
    try:
        c.execute("SELECT platinum_reward FROM tasks LIMIT 1")
    except sqlite3.OperationalError:
        c.execute("ALTER TABLE tasks ADD COLUMN platinum_reward INTEGER DEFAULT 0")
        conn.commit()
        print("已添加 platinum_reward 列到 tasks 表")

    # 迁移：为现有奖励添加 currency_type 列（如果不存在）
    try:
        c.execute("SELECT currency_type FROM rewards LIMIT 1")
    except sqlite3.OperationalError:
        c.execute("ALTER TABLE rewards ADD COLUMN currency_type TEXT DEFAULT 'coins'")
        conn.commit()
        print("已添加 currency_type 列到 rewards 表")

    # 初始化默认用户
    for uname in ["玖", "未"]:
        c.execute("SELECT id FROM users WHERE name=?", (uname,))
        if c.fetchone() is None:
            c.execute("INSERT INTO users(name, xp, level, coins, platinum_coins) VALUES(?,?,?,?,?)",
                      (uname, 0, 1, 0, 0))
    conn.commit()
    conn.close()
    return created


def get_users():
    """
    获取所有用户信息

    返回:
        list: 包含所有用户数据的列表
    """
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT id, name, xp, level, coins, platinum_coins FROM users")
    rows = c.fetchall()
    conn.close()
    return rows


def get_user(user_id):
    """
    获取指定用户的信息

    参数:
        user_id (int): 用户ID

    返回:
        sqlite3.Row: 用户数据行，找不到返回None
    """
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT id, name, xp, level, coins, platinum_coins FROM users WHERE id=?", (user_id,))
    row = c.fetchone()
    conn.close()
    return row


def update_user(user_id, xp=None, level=None, coins=None, platinum_coins=None):
    """
    更新用户数据

    参数:
        user_id (int): 要更新的用户ID
        xp (int, optional): 新的经验值
        level (int, optional): 新的等级
        coins (int, optional): 新的金币数量
        platinum_coins (int, optional): 新的铂金币数量
    """
    conn = get_db_connection()
    c = conn.cursor()
    updates = []
    params = []

    # 动态构建更新语句
    if xp is not None:
        updates.append("xp=?")
        params.append(xp)
    if level is not None:
        updates.append("level=?")
        params.append(level)
    if coins is not None:
        updates.append("coins=?")
        params.append(coins)
    if platinum_coins is not None:
        updates.append("platinum_coins=?")
        params.append(platinum_coins)

    if updates:
        params.append(user_id)
        query = f"UPDATE users SET {', '.join(updates)} WHERE id=?"
        c.execute(query, params)
        conn.commit()

    conn.close()


def add_task(user_id, name, xp_reward, platinum_reward=0):
    """
    为用户添加新任务

    参数:
        user_id (int): 用户ID
        name (str): 任务名称
        xp_reward (int): 任务经验奖励
        platinum_reward (int): 铂金币奖励（默认为0）
    """
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("INSERT INTO tasks(user_id, name, xp_reward, platinum_reward) VALUES(?,?,?,?)",
              (user_id, name, xp_reward, platinum_reward))
    conn.commit()
    conn.close()


def get_tasks(user_id):
    """
    获取指定用户的所有任务

    参数:
        user_id (int): 用户ID

    返回:
        list: 用户的任务列表，按完成状态和ID排序
    """
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT id, name, xp_reward, platinum_reward, completed FROM tasks WHERE user_id=? ORDER BY completed, id", (user_id,))
    rows = c.fetchall()
    conn.close()
    return rows


def complete_task(task_id):
    """
    完成任务并发放奖励，处理升级逻辑

    参数:
        task_id (int): 要完成的任务ID

    返回:
        dict: 包含奖励详情和升级信息的字典，失败返回None
    """
    conn = get_db_connection()
    c = conn.cursor()

    # 查询任务信息
    c.execute("SELECT user_id, xp_reward, platinum_reward, completed FROM tasks WHERE id=?", (task_id,))
    t = c.fetchone()
    if t is None:
        conn.close()
        return None

    user_id, xp_reward, task_platinum_reward, completed = t
    if completed:
        conn.close()
        return None

    # 标记任务已完成
    c.execute("UPDATE tasks SET completed=1 WHERE id=?", (task_id,))

    # 获取用户当前数据
    c.execute("SELECT xp, level, coins, platinum_coins FROM users WHERE id=?", (user_id,))
    u = c.fetchone()
    if u is None:
        conn.commit()
        conn.close()
        return None

    cur_xp, level, coins, platinum_coins = u
    new_xp = cur_xp + xp_reward
    old_level = level  # 记录原始等级

    # 添加任务完成时的铂金币奖励
    platinum_coins += task_platinum_reward

    # 计算升级所需经验
    xp_needed = get_xp_required_for_level(level)
    gained_coins = 0
    gained_platinum = task_platinum_reward  # 初始化为任务奖励的铂金币
    leveled = 0
    level_up_rewards = []

    # 处理可能的连续升级
    while new_xp >= xp_needed:
        new_xp -= xp_needed
        level += 1
        leveled += 1

        # 计算升级金币奖励（带随机性）
        base_reward = xp_needed
        min_multiplier = 0.8
        max_multiplier = 1.5
        random_multiplier = random.uniform(min_multiplier, max_multiplier)
        reward = int(base_reward * random_multiplier)

        coins += reward
        gained_coins += reward

        # 每2级奖励1个铂金币
        if level % 2 == 0:
            platinum_coins += 1
            gained_platinum += 1

        # 记录升级详情
        level_up_rewards.append({
            "from_level": level - 1,
            "to_level": level,
            "base_reward": base_reward,
            "random_multiplier": round(random_multiplier, 2),
            "actual_reward": reward,
            "platinum_reward": 1 if level % 2 == 0 else 0
        })

        # 计算下一级所需经验
        xp_needed = get_xp_required_for_level(level)

    # 更新用户数据
    c.execute("UPDATE users SET xp=?, level=?, coins=?, platinum_coins=? WHERE id=?",
              (new_xp, level, coins, platinum_coins, user_id))
    conn.commit()
    conn.close()

    return {
        "user_id": user_id,
        "xp": xp_reward,
        "leveled": leveled,
        "coins_gained": gained_coins,
        "platinum_gained": gained_platinum,
        "new_level": level,
        "new_xp": new_xp,
        "level_up_details": level_up_rewards
    }


# 商店相关函数
def add_reward(user_id, name, price, currency_type='coins'):
    """
    为用户添加可兑换奖励

    参数:
        user_id (int): 用户ID
        name (str): 奖励名称
        price (int): 所需货币数量
        currency_type (str): 货币类型，'coins'(金币) 或 'platinum'(铂金币)
    """
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("INSERT INTO rewards(user_id, name, price, currency_type) VALUES(?,?,?,?)",
              (user_id, name, price, currency_type))
    conn.commit()
    conn.close()


def get_rewards(user_id):
    """
    获取用户的所有奖励

    返回:
        list: 奖励列表，每项包含 (id, name, price, currency_type, completed)
    """
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT id, name, price, currency_type, completed FROM rewards WHERE user_id=? ORDER BY completed, id", (user_id,))
    rows = c.fetchall()
    conn.close()
    return rows


def redeem_reward(reward_id):
    """
    兑换奖励，扣除相应货币（金币或铂金币）

    返回:
        dict: 操作结果和剩余货币信息
    """
    conn = get_db_connection()
    c = conn.cursor()

    c.execute("SELECT user_id, price, currency_type, completed FROM rewards WHERE id=?", (reward_id,))
    r = c.fetchone()
    if r is None:
        conn.close()
        return {"success": False, "reason": "reward_not_found"}

    user_id, price, currency_type, completed = r
    if completed:
        conn.close()
        return {"success": False, "reason": "already_redeemed"}

    c.execute("SELECT coins, platinum_coins FROM users WHERE id=?", (user_id,))
    u = c.fetchone()
    if u is None:
        conn.close()
        return {"success": False, "reason": "user_not_found"}

    coins, platinum_coins = u

    # 根据货币类型检查余额并扣除
    if currency_type == 'platinum':
        if platinum_coins < price:
            conn.close()
            return {"success": False, "reason": "not_enough_platinum"}

        # 扣除铂金币
        new_platinum = platinum_coins - price
        c.execute("UPDATE rewards SET completed=1 WHERE id=?", (reward_id,))
        c.execute("UPDATE users SET platinum_coins=? WHERE id=?", (new_platinum, user_id))
        conn.commit()
        conn.close()

        return {
            "success": True,
            "currency_type": "platinum",
            "remaining_platinum": new_platinum,
            "remaining_coins": coins
        }
    else:  # 默认为金币
        if coins < price:
            conn.close()
            return {"success": False, "reason": "not_enough_coins"}

        # 扣除金币
        new_coins = coins - price
        c.execute("UPDATE rewards SET completed=1 WHERE id=?", (reward_id,))
        c.execute("UPDATE users SET coins=? WHERE id=?", (new_coins, user_id))
        conn.commit()
        conn.close()

        return {
            "success": True,
            "currency_type": "coins",
            "remaining_coins": new_coins,
            "remaining_platinum": platinum_coins
        }


def delete_reward(reward_id):
    """删除奖励"""
    try:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("DELETE FROM rewards WHERE id=?", (reward_id,))
        conn.commit()
        affected = c.rowcount
        conn.close()
        return affected > 0
    except Exception:
        return False


# 开发者工具函数
def add_user(name):
    """添加新用户"""
    if not name:
        return {"success": False, "reason": "empty_name"}
    conn = get_db_connection()
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users(name, xp, level, coins, platinum_coins) VALUES(?,?,?,?,?)", (name, 0, 1, 0, 0))
        conn.commit()
        uid = c.lastrowid
        conn.close()
        return {"success": True, "id": uid}
    except sqlite3.IntegrityError:
        conn.close()
        return {"success": False, "reason": "user_exists"}


def delete_user(user_id):
    """删除用户及其相关数据"""
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("DELETE FROM tasks WHERE user_id=?", (user_id,))
    c.execute("DELETE FROM users WHERE id=?", (user_id,))
    conn.commit()
    affected = c.rowcount
    conn.close()
    return affected > 0


def clear_data_file_and_reinit():
    """
    彻底清空数据文件并重新初始化系统

    用于开发者重置整个应用状态
    """
    try:
        import gc
        gc.collect()  # 强制垃圾回收释放资源

        if os.path.exists(DB_FILE):
            try:
                os.remove(DB_FILE)
            except PermissionError:
                # 如果文件被占用，使用重命名方式
                temp_name = f"{DB_FILE}.old.{int(time.time())}"
                try:
                    os.rename(DB_FILE, temp_name)
                    print(f"原数据库文件已重命名为: {temp_name}")

                    # 在后台线程中尝试删除旧文件
                    def cleanup_old_file(filename):
                        import time
                        time.sleep(2)
                        try:
                            if os.path.exists(filename):
                                os.remove(filename)
                                print(f"已清理旧文件: {filename}")
                        except:
                            pass

                    import threading
                    threading.Thread(target=cleanup_old_file, args=(temp_name,), daemon=True).start()

                except Exception as rename_error:
                    print(f"重命名文件也失败: {rename_error}")
                    return False

        # 重新初始化所有系统
        init_db()
        from repeat_tasks import init_repeat_tasks
        from gacha_fixed import init_gacha_system

        init_repeat_tasks()
        init_gacha_system()

        print("数据库已成功清空并重新初始化")
        return True

    except Exception as e:
        print(f"清空数据失败: {e}")
        return False


def delete_task(task_id):
    """删除任务"""
    try:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("DELETE FROM tasks WHERE id=?", (task_id,))
        conn.commit()
        affected = c.rowcount
        conn.close()
        return affected > 0
    except Exception:
        return False


def get_xp_required_for_level(level):
    """
    计算指定等级升级所需经验值

    使用线性增长公式：100 + (等级-1) * 19

    参数:
        level (int): 当前等级

    返回:
        int: 升级所需经验值
    """
    return int(100 + ((level - 1) * 19))


# 铂金币相关函数
PLATINUM_TO_GOLD_RATE = 100  # 1铂金币 = 100金币


def exchange_platinum_to_gold(user_id, platinum_amount):
    """
    将铂金币兑换为金币

    参数:
        user_id (int): 用户ID
        platinum_amount (int): 要兑换的铂金币数量

    返回:
        dict: 操作结果
    """
    if platinum_amount <= 0:
        return {"success": False, "reason": "invalid_amount"}

    conn = get_db_connection()
    c = conn.cursor()

    c.execute("SELECT coins, platinum_coins FROM users WHERE id=?", (user_id,))
    u = c.fetchone()
    if u is None:
        conn.close()
        return {"success": False, "reason": "user_not_found"}

    coins, platinum_coins = u

    if platinum_coins < platinum_amount:
        conn.close()
        return {"success": False, "reason": "not_enough_platinum"}

    # 执行兑换
    new_platinum = platinum_coins - platinum_amount
    gold_gained = platinum_amount * PLATINUM_TO_GOLD_RATE
    new_coins = coins + gold_gained

    c.execute("UPDATE users SET coins=?, platinum_coins=? WHERE id=?",
              (new_coins, new_platinum, user_id))
    conn.commit()
    conn.close()

    return {
        "success": True,
        "platinum_spent": platinum_amount,
        "gold_gained": gold_gained,
        "remaining_platinum": new_platinum,
        "new_gold": new_coins
    }


def add_platinum_coins(user_id, amount):
    """
    为用户添加铂金币

    参数:
        user_id (int): 用户ID
        amount (int): 要添加的铂金币数量

    返回:
        bool: 是否成功
    """
    if amount <= 0:
        return False

    conn = get_db_connection()
    c = conn.cursor()

    c.execute("SELECT platinum_coins FROM users WHERE id=?", (user_id,))
    u = c.fetchone()
    if u is None:
        conn.close()
        return False

    new_platinum = u[0] + amount
    c.execute("UPDATE users SET platinum_coins=? WHERE id=?", (new_platinum, user_id))
    conn.commit()
    conn.close()

    return True