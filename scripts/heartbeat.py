#!/usr/bin/env python3
"""心跳脚本：每个节点的 Muse 用 cron 定时运行。

用法：python3 scripts/heartbeat.py <节点名>
做三件事：数自己 inbox 的未读、找正在做的任务、更新 heartbeat.md。
"""
import sys
import re
import datetime
from pathlib import Path

try:
    from zoneinfo import ZoneInfo
    TZ = ZoneInfo("Asia/Shanghai")
except Exception:
    TZ = datetime.timezone(datetime.timedelta(hours=8))  # 兜底：UTC+8

ROOT = Path(__file__).resolve().parent.parent

def main():
    if len(sys.argv) != 2:
        print("用法：python3 scripts/heartbeat.py <节点名>")
        sys.exit(1)
    node = sys.argv[1]
    now = datetime.datetime.now(TZ).strftime("%Y-%m-%d %H:%M")  # 强制北京时间

    # inbox 未读：未勾选且 @到我的行
    unread = 0
    inbox = ROOT / "nodes" / node / "inbox.md"
    if inbox.exists():
        for line in inbox.read_text(encoding="utf-8").splitlines():
            if line.startswith("- [ ]") and f"@{node}" in line:
                unread += 1

    # 正在做的任务：认领者是我、状态为 claimed/in_progress 的任务卡
    doing = []
    tasks_dir = ROOT / "tasks"
    if tasks_dir.exists():
        for f in tasks_dir.glob("T-*.md"):
            text = f.read_text(encoding="utf-8")
            m_owner = re.search(r"-\s*认领者\s*[:：]\s*(\S+)", text)
            m_state = re.search(r"-\s*状态\s*[:：]\s*(\S+)", text)
            if not m_owner or not m_state:
                print(f"警告：{f.name} 缺少 认领者/状态 字段，跳过")
                continue
            if m_owner.group(1).strip() == node \
                    and m_state.group(1).strip() in ("claimed", "in_progress"):
                doing.append(f.stem)

    hb = ROOT / "nodes" / node / "heartbeat.md"
    hb.write_text(
        f"# {node} 心跳\n\n"
        f"- 最后检查：{now}\n"
        f"- inbox 未读：{unread}\n"
        f"- 正在做：{', '.join(doing) if doing else '无'}\n"
        f"- 状态：在线\n",
        encoding="utf-8",
    )
    print(f"[{now}] {node}: inbox 未读 {unread}，进行中任务 {doing if doing else '无'}")

if __name__ == "__main__":
    main()
