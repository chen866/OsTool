import os
import subprocess
import sys

# browser_tool
# 1. multi5 启动五个浏览器
# 2. start0 启动某一个序号的浏览器
# 3. closeall 关闭所有chrome进程


if __name__ == "__main__":
    # 目录
    user_home = os.path.expanduser("~")
    chrome_paths = [
        # windows
        os.path.join(user_home, r"AppData\Local\Google\Chrome\Application\chrome.exe"),
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    ]
    process_name = "chrome.exe"
    data_dir = os.path.expanduser("~/Documents/浏览器数据")
    dir_name = "b{i}"
    # 浏览器位置
    chrome_path = None
    for p in chrome_paths:
        if os.path.exists(p):
            chrome_path = p
            break
    if chrome_path is None:
        raise FileNotFoundError("browser executable not found")
    # 解析参数1
    arg1 = sys.argv[1]
    if arg1.startswith("multi"):
        # 启动浏览器，并指定用户文件夹
        browsers_num = int(arg1.split("multi")[1])
        for n in range(browsers_num):
            _dir = os.path.join(data_dir, dir_name.format(i=n))
            if not os.path.isdir(_dir):
                os.makedirs(_dir)
            command = "{} --user-data-dir={}".format(chrome_path, _dir)
            subprocess.Popen(command)
    elif arg1.startswith("start"):
        # 启动第n个浏览器, 从0开始
        n = int(arg1.split("start")[1])
        data_path = os.path.join(data_dir, dir_name.format(i=n))
        if not os.path.isdir(data_path):
            os.makedirs(data_path)
        command = "{} --user-data-dir={}".format(chrome_path, data_path)
        subprocess.Popen(command)
    elif arg1 == "closeall":
        # 关闭所有chrome进程
        for i in range(3):
            subprocess.Popen("taskkill /IM chrome.exe")
    else:
        raise ValueError(f"参数错误: {arg1}")
