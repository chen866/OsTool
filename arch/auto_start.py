import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

current_executer = sys.executable
cwd = os.getcwd()

jobs = [
    dict(args=["/usr/bin/clash-verge"]),
    dict(args=[current_executer, os.path.join(cwd, "arch/timer.py")], cwd=cwd),
]


with ThreadPoolExecutor(max_workers=10) as executor:
    tasks = [executor.submit(lambda: subprocess.Popen(**x)) for x in jobs]
    # 等待所有任务完成
    [task.result() for task in tasks]
    executor.shutdown(wait=True)
