"""通过 SQLite 保存会话状态，并演示版本冲突、用户隔离和重新读取。"""

import json
import sqlite3
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path
from tempfile import TemporaryDirectory


class StateConflict(RuntimeError):
    pass


# 每条记录保存所属用户、版本和 JSON 状态。调用方负责提供已经验证的用户标识。
class StateStore:
    def __init__(self, path="data/ai_state.sqlite3"):
        self.path = str(path)
        Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        # closing 负责关闭连接；内层连接上下文负责事务提交或回滚。
        with closing(sqlite3.connect(self.path)) as con, con:
            con.execute("""CREATE TABLE IF NOT EXISTS states (
                state_key TEXT PRIMARY KEY,
                owner_id TEXT NOT NULL,
                revision INTEGER NOT NULL,
                payload_json TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )""")

    @staticmethod
    def encode(payload):
        if not isinstance(payload, dict):
            raise ValueError("状态顶层必须为对象")
        # 按 UTF-8 编码后的字节数限制大小，中文占用的字节数可能多于字符数。
        raw = json.dumps(payload, ensure_ascii=False, allow_nan=False)
        if len(raw.encode("utf-8")) > 1_000_000:
            raise ValueError("单条状态过大，应拆分历史与工具结果")
        return raw

    # 新记录从版本 0 开始，后续保存会递增版本号。
    def create(self, state_key, owner_id, payload):
        if not state_key or not owner_id:
            raise ValueError("记录标识与身份不能为空")
        raw = self.encode(payload)
        with closing(sqlite3.connect(self.path)) as con, con:
            con.execute("INSERT INTO states VALUES (?, ?, 0, ?, ?)", (
                state_key, owner_id, raw, datetime.now(timezone.utc).isoformat()
            ))
        return 0

    # 同时按记录标识和所属用户查找，返回状态与保存时要用的版本号。
    def load(self, state_key, owner_id):
        with closing(sqlite3.connect(self.path)) as con:
            row = con.execute(
                "SELECT revision, payload_json FROM states WHERE state_key=? AND owner_id=?",
                (state_key, owner_id),
            ).fetchone()
        if row is None:
            raise LookupError("记录不存在或无权访问")
        return {"revision": row[0], "payload": json.loads(row[1])}

    def save(self, state_key, owner_id, expected_revision, payload):
        if type(expected_revision) is not int or expected_revision < 0:
            raise ValueError("版本号必须为非负整数")
        raw = self.encode(payload)
        with closing(sqlite3.connect(self.path)) as con, con:
            # 把旧版本号放进 WHERE，同一条 SQL 同时完成版本检查与更新。
            cursor = con.execute("""UPDATE states SET revision=revision+1,
                payload_json=?, updated_at=?
                WHERE state_key=? AND owner_id=? AND revision=?""", (
                raw, datetime.now(timezone.utc).isoformat(),
                state_key, owner_id, expected_revision,
            ))
            # 没有更新到记录就拒绝覆盖，由调用方重新读取和判断。
            if cursor.rowcount != 1:
                raise StateConflict("状态已变化、记录不存在或无权更新；需重新读取")
        return expected_revision + 1

    # 删除也要匹配读取时的版本，防止用过期状态删掉已更新的记录。
    def delete(self, state_key, owner_id, expected_revision):
        with closing(sqlite3.connect(self.path)) as con, con:
            cursor = con.execute(
                "DELETE FROM states WHERE state_key=? AND owner_id=? AND revision=?",
                (state_key, owner_id, expected_revision),
            )
            if cursor.rowcount != 1:
                raise StateConflict("删除失败，需重新验证身份与当前版本")


# 演示使用临时数据库，便于观察提交、冲突与隔离。
def main():
    with TemporaryDirectory(dir=Path(__file__).resolve().parent) as folder:
        db = Path(folder) / "state.sqlite3"
        store = StateStore(db)
        key, owner = "chat:demo", "verified-user-1"
        store.create(key, owner, {"turns": [], "status": "active"})
        snapshot = store.load(key, owner)
        payload = snapshot["payload"]
        # 实际应用只在模型回答完整成功后追加这一轮。
        payload["turns"].append({"user": "什么是 API？", "assistant": "程序之间的调用接口。"})
        # 使用读取时的版本提交，并保留返回的新版本用于后续操作。
        revision = store.save(key, owner, snapshot["revision"], payload)

        reopened = StateStore(db)  # 换一个实例，从磁盘重新读取。
        print(reopened.load(key, owner)["payload"]["turns"])
        try:
            reopened.save(key, owner, 0, {"turns": []})
        except StateConflict:
            print("旧版本写入被拒绝")
        try:
            reopened.load(key, "another-user")
        except LookupError:
            print("其他用户无法读取")
        reopened.delete(key, owner, revision)


if __name__ == "__main__":
    main()
