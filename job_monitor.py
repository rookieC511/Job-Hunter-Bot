import requests
import json
import os
import random
import datetime

# --- 配置区域 ---
PUSHPLUS_TOKEN = os.environ.get("PUSHPLUS_TOKEN")
DB_FILE = "jobs_db.json"

def fetch_mock_jobs():
    """模拟抓取职位数据"""
    print("正在模拟抓取美团职位...")
    # 模拟固定的职位
    jobs = [
        {"id": "1001", "name": "大模型算法实习生", "company": "美团-到家", "location": "上海"},
        {"id": "1002", "name": "自动驾驶规划算法", "company": "美团-无人车", "location": "北京"}
    ]
    # 模拟随机出现的新职位（为了测试通知功能）
    if random.random() > 0.5:
        new_id = str(random.randint(2000, 9999))
        jobs.append({
            "id": new_id, 
            "name": f"【新】多模态算法实习生-{new_id}", 
            "company": "美团-核心本地商业", 
            "location": "上海"
        })
    return jobs

def send_notification(new_jobs):
    """发送微信通知"""
    if not PUSHPLUS_TOKEN:
        print("⚠️ 未配置 PUSHPLUS_TOKEN，跳过发送")
        return

    title = f"捡漏啦！发现 {len(new_jobs)} 个新职位"
    content = "<h4>最新监测到的职位：</h4>"
    for job in new_jobs:
        content += f"<p><b>{job['name']}</b><br>部门：{job['company']} | 地点：{job['location']}</p><hr>"

    url = "http://www.pushplus.plus/send"
    data = {"token": PUSHPLUS_TOKEN, "title": title, "content": content, "template": "html"}
    requests.post(url, json=data)
    print("✅ 微信通知已发送！")

def main():
    # 1. 读取历史
    if os.path.exists(DB_FILE):
        with open(DB_FILE, 'r', encoding='utf-8') as f:
            old_ids = {job['id'] for job in json.load(f)}
    else:
        old_ids = set()

    # 2. 获取当前
    current_jobs = fetch_mock_jobs()
    
    # 3. 比对
    new_jobs = [job for job in current_jobs if job['id'] not in old_ids]

    # 4. 处理
    if new_jobs:
        print(f"发现 {len(new_jobs)} 个新职位！")
        send_notification(new_jobs)
        # 更新数据库
        with open(DB_FILE, 'w', encoding='utf-8') as f:
            json.dump(current_jobs, f, ensure_ascii=False, indent=2)
        # 告诉 GitHub Actions 有更新，需要提交代码
        if 'GITHUB_OUTPUT' in os.environ:
            with open(os.environ['GITHUB_OUTPUT'], 'a') as fh:
                print(f"STATUS=changed", file=fh)
    else:
        print("没有新职位。")

if __name__ == "__main__":
    main()
