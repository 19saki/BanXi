import random
import sqlite3  # 导入 SQLite 数据库模块
import os  # 用于文件操作

DB_FILE = "data.db"  # 数据库文件名


# -------------------------
# 初始化数据库及表结构
# -------------------------
def init_db():
    # 判断数据库是否存在，如果不存在则标记为新创建
    created = not os.path.exists(DB_FILE)
    conn = sqlite3.connect(DB_FILE)  # 连接数据库
    c = conn.cursor()  # 创建游标

    # 创建用户表，保存玩家信息
    c.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE,         -- 用户名唯一
        xp INTEGER DEFAULT 0,     -- 经验值
        level INTEGER DEFAULT 1,  -- 等级
        coins INTEGER DEFAULT 0   -- 金币
    )
    """)

    # 创建任务表，保存用户任务信息
    c.execute("""
    CREATE TABLE IF NOT EXISTS tasks(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,           -- 关联用户ID
        name TEXT,                 -- 任务名称
        xp_reward INTEGER,         -- 完成任务获得经验值
        completed INTEGER DEFAULT 0, -- 是否完成，0未完成，1已完成
        created_at TEXT DEFAULT CURRENT_TIMESTAMP, -- 创建时间
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    """)

    # 创建商店表，保存可购买物品
    c.execute("""
    CREATE TABLE IF NOT EXISTS rewards(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,           -- 关联用户ID
        name TEXT,                 -- 奖励名称
        price INTEGER,             -- 兑换所需金币（保持与原来商店相同的字段名）
        completed INTEGER DEFAULT 0, -- 是否兑换，0未兑换，1已兑换
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    """)

    conn.commit()  # 提交创建表操作

    # 初始化默认用户 "玖" 和 "未"
    for uname in ["玖", "未"]:
        c.execute("SELECT id FROM users WHERE name=?", (uname,))
        if c.fetchone() is None:
            c.execute("INSERT INTO users(name, xp, level, coins) VALUES(?,?,?,?)",
                      (uname, 0, 1, 0))
    conn.commit()
    conn.close()
    return created  # 返回是否新创建数据库


# -------------------------
# 获取所有用户
# -------------------------
def get_users():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT id, name, xp, level, coins FROM users")
    rows = c.fetchall()
    conn.close()
    return rows


# -------------------------
# 获取指定用户
# -------------------------
def get_user(user_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT id, name, xp, level, coins FROM users WHERE id=?", (user_id,))
    row = c.fetchone()
    conn.close()
    return row


# -------------------------
# 更新用户数据
# -------------------------
def update_user(user_id, xp=None, level=None, coins=None):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    if xp is not None:
        c.execute("UPDATE users SET xp=? WHERE id=?", (xp, user_id))
    if level is not None:
        c.execute("UPDATE users SET level=? WHERE id=?", (level, user_id))
    if coins is not None:
        c.execute("UPDATE users SET coins=? WHERE id=?", (coins, user_id))
    conn.commit()
    conn.close()


# -------------------------
# 添加任务
# -------------------------
def add_task(user_id, name, xp_reward):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO tasks(user_id, name, xp_reward) VALUES(?,?,?)", (user_id, name, xp_reward))
    conn.commit()
    conn.close()


# -------------------------
# 获取指定用户的任务列表
# -------------------------
def get_tasks(user_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT id, name, xp_reward, completed FROM tasks WHERE user_id=? ORDER BY completed, id", (user_id,))
    rows = c.fetchall()
    conn.close()
    return rows


# -------------------------
# 完成任务逻辑
# -------------------------
def complete_task(task_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    # 查询任务信息
    c.execute("SELECT user_id, xp_reward, completed FROM tasks WHERE id=?", (task_id,))
    t = c.fetchone()
    if t is None:  # 任务不存在
        conn.close()
        return None

    user_id, xp_reward, completed = t
    if completed:  # 已完成的任务不再处理
        conn.close()
        return None

    # 标记任务已完成
    c.execute("UPDATE tasks SET completed=1 WHERE id=?", (task_id,))

    # 获取用户当前数据
    c.execute("SELECT xp, level, coins FROM users WHERE id=?", (user_id,))
    u = c.fetchone()
    if u is None:
        conn.commit()
        conn.close()
        return None

    cur_xp, level, coins = u
    new_xp = cur_xp + xp_reward
    # 添加调试信息
    # print(f"DEBUG: 当前等级 {level}, 获得经验 {xp_reward}, 总经验 {new_xp}")

    # 第一个修改点
    xp_needed = int(100 * (1.19 ** (level - 1)))
    # print(f"DEBUG: 升级到 {level + 1} 需要 {xp_needed} XP")
    gained_coins = 0
    leveled = 0
    level_up_rewards = []  # 记录每次升级的详细信息

    # 升级循环：如果经验超过当前等级所需，提升等级
    while new_xp >= xp_needed:
        new_xp -= xp_needed
        level += 1
        leveled += 1

        # 修改：每次升级获得随机金币（升级所需经验值的 80% ~ 150%）
        base_reward = xp_needed  # 基础奖励 = 升级所需经验值
        min_multiplier = 0.8  # 下限 80%
        max_multiplier = 1.5  # 上限 150%

        # 生成随机倍数
        random_multiplier = random.uniform(min_multiplier, max_multiplier)
        reward = int(base_reward * random_multiplier)

        coins += reward
        gained_coins += reward

        # 记录这次升级的详细信息
        level_up_rewards.append({
            "from_level": level - 1,
            "to_level": level,
            "base_reward": base_reward,
            "random_multiplier": round(random_multiplier, 2),
            "actual_reward": reward
        })

        xp_needed = int(100 * (1.19 ** (level - 1)))
        # print(f"DEBUG: 升级到 {level + 1} 需要 {xp_needed} XP")

    # 更新用户数据
    c.execute("UPDATE users SET xp=?, level=?, coins=? WHERE id=?", (new_xp, level, coins, user_id))
    conn.commit()
    conn.close()

    # 返回任务完成结果
    return {
        "user_id": user_id,
        "xp": xp_reward,
        "leveled": leveled,
        "coins_gained": gained_coins,
        "new_level": level,
        "new_xp": new_xp,
        "level_up_details": level_up_rewards  # 新增：包含每次升级的详细信息
    }


# -------------------------
# 商店操作
# -------------------------
def add_reward(user_id, name, price):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO rewards(user_id, name, price) VALUES(?,?,?)", (user_id, name, price))
    conn.commit()
    conn.close()


def get_rewards(user_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT id, name, price, completed FROM rewards WHERE user_id=? ORDER BY completed, id", (user_id,))
    rows = c.fetchall()
    conn.close()
    return rows


def redeem_reward(reward_id):
    """兑换奖励（替换原来的purchase_item）"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    # 查询奖励信息
    c.execute("SELECT user_id, price, completed FROM rewards WHERE id=?", (reward_id,))
    r = c.fetchone()
    if r is None:
        conn.close()
        return {"success": False, "reason": "reward_not_found"}

    user_id, price, completed = r
    if completed:
        conn.close()
        return {"success": False, "reason": "already_redeemed"}

    # 查询用户金币
    c.execute("SELECT coins FROM users WHERE id=?", (user_id,))
    u = c.fetchone()
    if u is None:
        conn.close()
        return {"success": False, "reason": "user_not_found"}

    coins = u[0]

    # 检查金币是否足够
    if coins < price:
        conn.close()
        return {"success": False, "reason": "not_enough_coins"}

    # 扣除金币并标记为已兑换
    coins -= price
    c.execute("UPDATE rewards SET completed=1 WHERE id=?", (reward_id,))
    c.execute("UPDATE users SET coins=? WHERE id=?", (coins, user_id))
    conn.commit()
    conn.close()

    return {"success": True, "remaining": coins}


def delete_reward(reward_id):
    """删除奖励"""
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("DELETE FROM rewards WHERE id=?", (reward_id,))
        conn.commit()
        affected = c.rowcount
        conn.close()
        return affected > 0
    except Exception:
        return False


# -------------------------
# 开发者辅助函数
# -------------------------
def add_user(name):
    if not name:
        return {"success": False, "reason": "empty_name"}
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users(name, xp, level, coins) VALUES(?,?,?,?)", (name, 0, 1, 0))
        conn.commit()
        uid = c.lastrowid  # 获取新用户ID
        conn.close()
        return {"success": True, "id": uid}
    except sqlite3.IntegrityError:
        conn.close()
        return {"success": False, "reason": "user_exists"}


def delete_user(user_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("DELETE FROM tasks WHERE user_id=?", (user_id,))  # 删除用户所有任务
    c.execute("DELETE FROM users WHERE id=?", (user_id,))  # 删除用户
    conn.commit()
    affected = c.rowcount
    conn.close()
    return affected > 0


def clear_data_file_and_reinit():
    try:
        if os.path.exists(DB_FILE):
            os.remove(DB_FILE)  # 删除数据库文件
        init_db()  # 重新初始化
        return True
    except Exception:
        return False


def delete_task(task_id):
    """删除指定任务"""
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("DELETE FROM tasks WHERE id=?", (task_id,))
        conn.commit()
        affected = c.rowcount
        conn.close()
        return affected > 0
    except Exception:
        return False


def get_xp_required_for_level(level):
    """获取指定等级升级所需经验值"""
    return int(100 + ((level-1) * 19))
