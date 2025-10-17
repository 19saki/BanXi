import sqlite3
from db import get_db_connection

# -------------------------
# 初始化重复任务表
# -------------------------
def init_repeat_tasks_table():
    conn = get_db_connection()
    c = conn.cursor()

    # 创建重复任务表
    c.execute("""
    CREATE TABLE IF NOT EXISTS repeat_tasks(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        name TEXT,
        xp_reward INTEGER,
        max_completions INTEGER,
        current_completions INTEGER DEFAULT 0,
        completed INTEGER DEFAULT 0,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    """)

    conn.commit()

    # 检查是否已有重复任务，如果没有则添加默认任务
    c.execute("SELECT COUNT(*) FROM repeat_tasks")
    count = c.fetchone()[0]

    if count == 0:
        # 为每个用户添加默认的重复任务
        users = c.execute("SELECT id FROM users").fetchall()

        default_tasks = [
            # 格式: (任务名称, 经验奖励, 最大完成次数)
            ("0点前睡", 90, 1),  # 每日一次
            ("9点前进入学习", 190, 1),  # 每日一次
            ("一个番茄钟认真学习", 90, 0),  # 无限次
            ("一个番茄钟普通学习", 50, 0),  # 每日一次
        ]

        for user_id, in users:
            for name, xp_reward, max_completions in default_tasks:
                c.execute("""
                    INSERT INTO repeat_tasks(user_id, name, xp_reward, max_completions) 
                    VALUES(?,?,?,?)
                """, (user_id, name, xp_reward, max_completions))

        conn.commit()
        print(f"已为 {len(users)} 个用户添加 {len(default_tasks)} 个默认重复任务")
    conn.close()

# -------------------------
# 添加重复任务
# -------------------------
def add_repeat_task(user_id, name, xp_reward, max_completions=0):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("""
        INSERT INTO repeat_tasks(user_id, name, xp_reward, max_completions) 
        VALUES(?,?,?,?)
    """, (user_id, name, xp_reward, max_completions))
    conn.commit()
    conn.close()

# -------------------------
# 获取指定用户的重复任务列表
# -------------------------
def get_repeat_tasks(user_id):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("""
        SELECT id, name, xp_reward, max_completions, current_completions, completed 
        FROM repeat_tasks 
        WHERE user_id=? 
        ORDER BY completed, id
    """, (user_id,))
    rows = c.fetchall()
    conn.close()
    return rows

# -------------------------
# 完成重复任务逻辑
# -------------------------
def complete_repeat_task(task_id):
    import random
    from db import get_user, update_user, get_xp_required_for_level  # 添加导入

    conn = get_db_connection()
    c = conn.cursor()

    # 查询任务信息
    c.execute("""
        SELECT user_id, name, xp_reward, max_completions, current_completions, completed 
        FROM repeat_tasks WHERE id=?
    """, (task_id,))
    t = c.fetchone()

    if t is None:
        conn.close()
        return None

    user_id, name, xp_reward, max_completions, current_completions, completed = t

    if completed:
        conn.close()
        return None

    # 更新完成次数
    new_completions = current_completions + 1
    new_completed = 0

    if max_completions > 0 and new_completions >= max_completions:
        new_completed = 1

    c.execute("""
        UPDATE repeat_tasks 
        SET current_completions=?, completed=? 
        WHERE id=?
    """, (new_completions, new_completed, task_id))

    # 获取用户当前数据
    c.execute("SELECT xp, level, coins FROM users WHERE id=?", (user_id,))
    u = c.fetchone()
    if u is None:
        conn.commit()
        conn.close()
        return None

    cur_xp, level, coins = u
    new_xp = cur_xp + xp_reward

    # 修复：使用线性增长公式
    xp_needed = get_xp_required_for_level(level)
    gained_coins = 0
    leveled = 0
    level_up_rewards = []

    while new_xp >= xp_needed:
        new_xp -= xp_needed
        level += 1
        leveled += 1

        base_reward = xp_needed
        min_multiplier = 0.8
        max_multiplier = 1.5
        random_multiplier = random.uniform(min_multiplier, max_multiplier)
        reward = int(base_reward * random_multiplier)

        coins += reward
        gained_coins += reward

        level_up_rewards.append({
            "from_level": level - 1,
            "to_level": level,
            "base_reward": base_reward,
            "random_multiplier": round(random_multiplier, 2),
            "actual_reward": reward
        })

        # 修复：使用线性增长公式计算下一级所需经验
        xp_needed = get_xp_required_for_level(level)

    c.execute("UPDATE users SET xp=?, level=?, coins=? WHERE id=?", (new_xp, level, coins, user_id))
    conn.commit()
    conn.close()

    return {
        "user_id": user_id,
        "task_name": name,
        "xp": xp_reward,
        "leveled": leveled,
        "coins_gained": gained_coins,
        "new_level": level,
        "new_xp": new_xp,
        "completion_count": new_completions,
        "max_completions": max_completions,
        "is_fully_completed": new_completed,
        "level_up_details": level_up_rewards
    }

# -------------------------
# 删除重复任务
# -------------------------
def delete_repeat_task(task_id):
    try:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("DELETE FROM repeat_tasks WHERE id=?", (task_id,))
        conn.commit()
        affected = c.rowcount
        conn.close()
        return affected > 0
    except Exception:
        return False
# -------------------------
# 初始化表（在应用启动时调用）
# -------------------------
def init_repeat_tasks():
    init_repeat_tasks_table()

def complete_repeat_task_multiple_times(task_id, times):
        """
        多次完成重复任务
        """
        import random
        from db import get_user, update_user, get_xp_required_for_level

        conn = get_db_connection()
        c = conn.cursor()

        # 查询任务信息
        c.execute("""
            SELECT user_id, name, xp_reward, max_completions, current_completions, completed 
            FROM repeat_tasks WHERE id=?
        """, (task_id,))
        t = c.fetchone()

        if t is None:
            conn.close()
            return None

        user_id, name, xp_reward, max_completions, current_completions, completed = t

        if completed:
            conn.close()
            return None

        # 检查最大完成次数限制
        if max_completions > 0:
            available_times = max_completions - current_completions
            if times > available_times:
                times = available_times  # 限制为最大可用次数

        if times <= 0:
            conn.close()
            return None

        # 更新完成次数
        new_completions = current_completions + times
        new_completed = 0

        if max_completions > 0 and new_completions >= max_completions:
            new_completed = 1
            times = max_completions - current_completions  # 调整实际完成次数

        c.execute("""
            UPDATE repeat_tasks 
            SET current_completions=?, completed=? 
            WHERE id=?
        """, (new_completions, new_completed, task_id))

        # 获取用户当前数据
        c.execute("SELECT xp, level, coins FROM users WHERE id=?", (user_id,))
        u = c.fetchone()
        if u is None:
            conn.commit()
            conn.close()
            return None

        cur_xp, level, coins = u
        total_xp_gained = xp_reward * times
        new_xp = cur_xp + total_xp_gained

        # 计算升级逻辑
        xp_needed = get_xp_required_for_level(level)
        gained_coins = 0
        leveled = 0
        level_up_rewards = []

        while new_xp >= xp_needed:
            new_xp -= xp_needed
            level += 1
            leveled += 1

            base_reward = xp_needed
            min_multiplier = 0.8
            max_multiplier = 1.5
            random_multiplier = random.uniform(min_multiplier, max_multiplier)
            reward = int(base_reward * random_multiplier)

            coins += reward
            gained_coins += reward

            level_up_rewards.append({
                "from_level": level - 1,
                "to_level": level,
                "base_reward": base_reward,
                "random_multiplier": round(random_multiplier, 2),
                "actual_reward": reward
            })

            xp_needed = get_xp_required_for_level(level)

        c.execute("UPDATE users SET xp=?, level=?, coins=? WHERE id=?", (new_xp, level, coins, user_id))
        conn.commit()
        conn.close()

        return {
            "user_id": user_id,
            "task_name": name,
            "times_completed": times,
            "total_xp": total_xp_gained,
            "xp_per_completion": xp_reward,
            "leveled": leveled,
            "coins_gained": gained_coins,
            "new_level": level,
            "new_xp": new_xp,
            "completion_count": new_completions,
            "max_completions": max_completions,
            "is_fully_completed": new_completed,
            "level_up_details": level_up_rewards
        }