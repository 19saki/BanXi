import sqlite3
import random
from db import get_db_connection

# 概率配置常量
DEFAULT_RATES = {6: 0.02, 5: 0.08, 4: 0.50, 3: 0.40}  # 各星级基础概率
DEFAULT_REFUND = {6: 1000, 5: 500, 4: 200, 3: 100}  # 重复奖品返还金币


def init_gacha_tables():
    """
    初始化抽卡系统所需的数据表

    创建奖品表、抽卡记录表和用户统计表
    """
    conn = get_db_connection()
    c = conn.cursor()

    # 奖品表：存储所有可抽到的物品
    c.execute("""
    CREATE TABLE IF NOT EXISTS gacha_items(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,          -- 奖品名称
        star INTEGER NOT NULL,       -- 星级（3-6星）
        description TEXT,            -- 奖品描述
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # 抽卡记录表：记录用户每次抽卡结果
    c.execute("""
    CREATE TABLE IF NOT EXISTS gacha_records(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,    -- 用户ID
        item_id INTEGER NOT NULL,    -- 奖品ID
        draw_time TEXT DEFAULT CURRENT_TIMESTAMP,  -- 抽卡时间
        FOREIGN KEY(user_id) REFERENCES users(id),
        FOREIGN KEY(item_id) REFERENCES gacha_items(id)
    )
    """)

    # 用户统计表：用于保底机制计算
    c.execute("""
    CREATE TABLE IF NOT EXISTS gacha_stats(
        user_id INTEGER PRIMARY KEY,
        no_six_star_count INTEGER DEFAULT 0,  -- 连续未出六星次数
        pity_rate REAL DEFAULT 0.0,           -- 保底概率加成
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    """)

    conn.commit()

    # 如果奖池为空，添加默认奖品
    c.execute("SELECT COUNT(*) FROM gacha_items")
    count = c.fetchone()[0]

    if count == 0:
        default_items = [
            # 六星物品（稀有）
            ("出去睡觉", 6, "嗯,就是可以立刻找一天和小未出去睡大床"),
            ("小裙子代金券", 6, "可以最多代200块~"),
            ("罗小黑的小手办一个", 6, "手办你得到了恭喜你!"),

            # 五星物品（史诗）
            ("蟹蟹!!!参与!!!", 5, "请你吃螃蟹!哈哈哈哈!!!"),
            ("请你喝库迪~", 5, "咖啡咖啡咖啡咖啡"),
            ("罗小黑的小卡片", 5, "很好的小卡片,让你旋转"),

            # 四星物品（稀有）
            ("谢谢参与!!!", 4, "这个是很认真的蟹蟹参与!!!"),
            ("谢谢参与!!!", 4, "这个是很认真的蟹蟹参与!!!"),
            ("谢谢参与!!!", 4, "这个是很认真的蟹蟹参与!!!"),
            ("谢谢参与!!!", 4, "这个是很认真的蟹蟹参与!!!"),
            ("谢谢参与!!!", 4, "这个是很认真的蟹蟹参与!!!"),



            # 三星物品（普通）
            ("谢谢参与", 3, "是的就是蟹蟹参与"),
            ("谢谢参与", 3, "是的就是蟹蟹参与"),
            ("谢谢参与", 3, "是的就是蟹蟹参与"),
            ("谢谢参与", 3, "是的就是蟹蟹参与"),
            ("谢谢参与", 3, "是的就是蟹蟹参与"),


        ]

        for name, star, desc in default_items:
            c.execute("INSERT INTO gacha_items(name, star, description) VALUES(?,?,?)",
                      (name, star, desc))

    conn.commit()


def add_gacha_item(name, star, description=""):
    """向奖池添加新奖品"""
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("INSERT INTO gacha_items(name, star, description) VALUES(?,?,?)",
              (name, star, description))
    conn.commit()


def get_gacha_items():
    """获取奖池所有奖品，按星级和ID排序"""
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT id, name, star, description FROM gacha_items ORDER BY star DESC, id")
    rows = c.fetchall()
    return rows


def get_user_gacha_stats(user_id):
    """
    获取用户抽卡统计信息

    返回:
        dict: 包含保底计数和概率加成的字典
    """
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT no_six_star_count, pity_rate FROM gacha_stats WHERE user_id=?", (user_id,))
    row = c.fetchone()

    if row is None:
        return {"no_six_star_count": 0, "pity_rate": 0.0}
    else:
        return {"no_six_star_count": row[0], "pity_rate": row[1]}


def get_user_gacha_records(user_id, limit=10):
    """
    获取用户最近的抽卡记录

    参数:
        user_id (int): 用户ID
        limit (int): 返回记录数量限制

    返回:
        list: 抽卡记录列表
    """
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("""
        SELECT gr.draw_time, gi.name, gi.star, gi.description 
        FROM gacha_records gr 
        JOIN gacha_items gi ON gr.item_id = gi.id 
        WHERE gr.user_id=? 
        ORDER BY gr.draw_time DESC 
        LIMIT ?
    """, (user_id, limit))
    rows = c.fetchall()
    return rows


def user_owns_item(user_id, item_id):
    """检查用户是否已拥有某个奖品（用于重复判断）"""
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM gacha_records WHERE user_id=? AND item_id=?", (user_id, item_id))
    count = c.fetchone()[0]
    return count > 0


def draw_gacha(user_id):
    """
    执行单次抽卡操作

    使用事务确保操作的原子性，包含保底机制和重复返还

    返回:
        dict: 抽卡结果详情
    """
    conn = get_db_connection()

    try:
        # 开始事务
        conn.execute("BEGIN IMMEDIATE")

        # 检查用户和金币
        user = conn.execute(
            "SELECT id, name, xp, level, coins FROM users WHERE id=?",
            (user_id,)
        ).fetchone()

        if not user:
            conn.rollback()
            return {"success": False, "reason": "user_not_found"}

        coins = user[4]
        if coins < 600:  # 单抽需要600金币
            conn.rollback()
            return {"success": False, "reason": "not_enough_coins"}

        # 扣除金币
        coins -= 600
        conn.execute("UPDATE users SET coins=? WHERE id=?", (coins, user_id))

        # 获取抽卡统计（保底信息）
        stats = conn.execute(
            "SELECT no_six_star_count, pity_rate FROM gacha_stats WHERE user_id=?",
            (user_id,)
        ).fetchone()

        if stats:
            no_six_star_count, pity_rate = stats[0], stats[1]
        else:
            no_six_star_count, pity_rate = 0, 0.0

        # 计算当前概率（含保底加成）
        current_rates = DEFAULT_RATES.copy()
        current_rates[6] += pity_rate  # 应用保底概率加成

        # 调整概率保持总和为1
        total_other = sum(current_rates[s] for s in [3, 4, 5])
        if total_other > 0:
            scale = (1 - current_rates[6]) / total_other
            for star in [3, 4, 5]:
                current_rates[star] *= scale

        # 执行抽卡随机
        rand_val = random.random()
        cumulative = 0
        selected_star = 3  # 默认三星

        # 从高星到低星判断
        for star in [6, 5, 4, 3]:
            cumulative += current_rates[star]
            if rand_val <= cumulative:
                selected_star = star
                break

        # 从对应星级的奖品中随机选择
        items = conn.execute(
            "SELECT id, name, description FROM gacha_items WHERE star=?",
            (selected_star,)
        ).fetchall()

        if not items:
            conn.rollback()
            return {"success": False, "reason": "no_items_in_star"}

        selected_item = random.choice(items)
        item_id, item_name, item_desc = selected_item

        # 记录抽卡结果
        conn.execute(
            "INSERT INTO gacha_records(user_id, item_id) VALUES(?,?)",
            (user_id, item_id)
        )

        # 更新保底统计
        new_count = no_six_star_count + 1
        new_pity = pity_rate

        if selected_star == 6:
            # 抽到六星，重置保底
            new_count = 0
            new_pity = 0.0
        elif new_count >= 50:
            # 连续50次未出六星，增加保底概率
            new_pity = min(1.0, pity_rate + 0.02)

        conn.execute(
            """INSERT OR REPLACE INTO gacha_stats(user_id, no_six_star_count, pity_rate) 
               VALUES(?,?,?)""",
            (user_id, new_count, new_pity)
        )

        # 检查是否重复获得
        ownership = conn.execute(
            "SELECT COUNT(*) as count FROM gacha_records WHERE user_id=? AND item_id=?",
            (user_id, item_id)
        ).fetchone()

        is_duplicate = ownership[0] > 1
        refund_coins = 0

        # 重复获得则返还部分金币
        if is_duplicate:
            refund_coins = DEFAULT_REFUND[selected_star]
            coins += refund_coins
            conn.execute("UPDATE users SET coins=? WHERE id=?", (coins, user_id))

        # 提交事务
        conn.commit()

        return {
            "success": True,
            "item": {
                "id": item_id,
                "name": item_name,
                "star": selected_star,
                "description": item_desc
            },
            "is_duplicate": is_duplicate,
            "refund_coins": refund_coins,
            "remaining_coins": coins,
            "pity_info": {
                "no_six_star_count": new_count,
                "pity_rate": new_pity
            }
        }

    except Exception as e:
        conn.rollback()
        print(f"抽卡错误: {e}")
        return {"success": False, "reason": f"database_error: {str(e)}"}


def draw_gacha_10(user_id):
    """
    执行十连抽卡

    优化版：先检查金币，然后批量执行10次抽卡
    """
    conn = get_db_connection()

    try:
        conn.execute("BEGIN IMMEDIATE")

        # 先检查用户金币是否足够
        user = conn.execute(
            "SELECT coins FROM users WHERE id=?",
            (user_id,)
        ).fetchone()

        if not user:
            conn.rollback()
            return {"success": False, "reason": "user_not_found"}

        coins = user[0]
        if coins < 6000:  # 十连需要6000金币
            conn.rollback()
            return {"success": False, "reason": "not_enough_coins"}

        # 一次性扣除6000金币
        coins -= 6000
        conn.execute("UPDATE users SET coins=? WHERE id=?", (coins, user_id))

        # 获取当前抽卡统计
        stats = conn.execute(
            "SELECT no_six_star_count, pity_rate FROM gacha_stats WHERE user_id=?",
            (user_id,)
        ).fetchone()

        if stats:
            no_six_star_count, pity_rate = stats[0], stats[1]
        else:
            no_six_star_count, pity_rate = 0, 0.0

        results = []
        total_refund = 0
        current_coins = coins

        # 执行10次抽卡
        for i in range(10):
            # 计算当前概率（含保底）
            current_rates = DEFAULT_RATES.copy()
            current_rates[6] += pity_rate

            # 调整概率保持总和为1
            total_other = sum(current_rates[s] for s in [3, 4, 5])
            if total_other > 0:
                scale = (1 - current_rates[6]) / total_other
                for star in [3, 4, 5]:
                    current_rates[star] *= scale

            # 抽卡
            rand_val = random.random()
            cumulative = 0
            selected_star = 3

            for star in [6, 5, 4, 3]:
                cumulative += current_rates[star]
                if rand_val <= cumulative:
                    selected_star = star
                    break

            # 获取奖品
            items = conn.execute(
                "SELECT id, name, description FROM gacha_items WHERE star=?",
                (selected_star,)
            ).fetchall()

            if not items:
                continue  # 跳过这次抽卡

            selected_item = random.choice(items)
            item_id, item_name, item_desc = selected_item

            # 记录抽卡
            conn.execute(
                "INSERT INTO gacha_records(user_id, item_id) VALUES(?,?)",
                (user_id, item_id)
            )

            # 更新统计
            new_count = no_six_star_count + 1
            new_pity = pity_rate

            if selected_star == 6:
                new_count = 0
                new_pity = 0.0
            elif new_count >= 50:
                new_pity = min(1.0, pity_rate + 0.02)

            no_six_star_count = new_count
            pity_rate = new_pity

            # 检查重复
            ownership = conn.execute(
                "SELECT COUNT(*) FROM gacha_records WHERE user_id=? AND item_id=?",
                (user_id, item_id)
            ).fetchone()

            is_duplicate = ownership[0] > 1
            refund_coins = 0

            if is_duplicate:
                refund_coins = DEFAULT_REFUND[selected_star]
                current_coins += refund_coins
                total_refund += refund_coins

            results.append({
                "item": {
                    "id": item_id,
                    "name": item_name,
                    "star": selected_star,
                    "description": item_desc
                },
                "is_duplicate": is_duplicate,
                "refund_coins": refund_coins
            })

        # 更新最终金币和统计
        conn.execute("UPDATE users SET coins=? WHERE id=?", (current_coins, user_id))
        conn.execute(
            """INSERT OR REPLACE INTO gacha_stats(user_id, no_six_star_count, pity_rate) 
               VALUES(?,?,?)""",
            (user_id, no_six_star_count, pity_rate)
        )

        conn.commit()

        return {
            "success": True,
            "draws": results,
            "total_refund": total_refund,
            "remaining_coins": current_coins,
            "pity_info": {
                "no_six_star_count": no_six_star_count,
                "pity_rate": pity_rate
            }
        }

    except Exception as e:
        conn.rollback()
        print(f"十连抽错误: {e}")
        return {"success": False, "reason": f"database_error: {str(e)}"}


def delete_gacha_item(item_id):
    """删除抽卡奖品"""
    conn = get_db_connection()
    c = conn.cursor()
    try:
        c.execute("DELETE FROM gacha_items WHERE id=?", (item_id,))
        conn.commit()
        affected = c.rowcount
        return affected > 0
    except Exception:
        return False


def init_gacha_system():
    """初始化抽卡系统（兼容性函数）"""
    init_gacha_tables()