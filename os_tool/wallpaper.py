import json
import logging
import subprocess

import argparse
import os
import ctypes
import time
import sys
import socket
import http.client
import urllib


def https_get(url):
    url_result = urllib.parse.urlparse(url)
    rhost = url_result.netloc
    rpath = '{}?{}'.format(url_result.path, url_result.query)
    conn = http.client.HTTPSConnection(rhost)
    payload = ''
    headers = {}
    conn.request("GET", rpath, payload, headers)
    res = conn.getresponse()
    return res.read()


def get_img(img_path, use_4k):
    """请求网页，获取当日图片"""
    # 获取每日必应
    url = 'https://cn.bing.com/HPImageArchive.aspx?format=js&idx=0&n=1'
    resp = https_get(url)
    j = json.loads(resp.decode("utf-8"))
    url2 = 'https://cn.bing.com' + j['images'][0]['url']
    if use_4k:
        # 获取图片 UHD
        url2 = url2.replace('_1920x1080', '_UHD')
    try:
        r = https_get(url2)
        with open(img_path, 'wb') as f:
            f.write(r)
    except BaseException as e:
        logging.error(e)


# def get_img_old(img_path, use_4k):
#     """请求网页，获取当日图片"""
#     # 获取每日必应
#     url = 'https://cn.bing.com/HPImageArchive.aspx?format=js&idx=0&n=1'
#     resp = requests.post(url)
#     j = resp.json()
#     url2 = 'https://cn.bing.com' + j['images'][0]['url']
#     if use_4k:
#         # 获取图片 UHD
#         url2 = url2.replace('_1920x1080', '_UHD')
#     try:
#         r = requests.get(url2)
#         with open(img_path, 'wb') as f:
#             f.write(r.content)
#     except BaseException as e:
#         logging.error(e)


def set_img_as_wallpaper(img_path):
    """设置图片绝对路径 img_path 所指向的图片为壁纸"""
    if sys.platform == 'win32':
        ctypes.windll.user32.SystemParametersInfoW(20, 0, img_path, 0)
    elif sys.platform == 'linux':
        # 获取当前桌面环境  
        desktop_env = os.environ.get('XDG_CURRENT_DESKTOP')
        logging.info(f'当前桌面环境: {desktop_env}')
        if desktop_env == 'GNOME':
            os.system(f'gsettings set org.gnome.desktop.background picture-uri "{img_path}"')
        # elif desktop_env == 'KDE':
        #     config_cmd = [
        #         "kwriteconfig6", "--file", "plasma-org.kde.plasma.desktop-appletsrc",
        #         "--group", "Containments", "--group", "2",
        #         "--group", "Wallpaper", "--group", "org.kde.image", "--group", "General",
        #         "--key", "Image", f"file://{img_path}"
        #     ]
        #     subprocess.run(config_cmd)
        #     subprocess.run(["plasmashell", "--replace", "&"], check=True)
        elif desktop_env == 'LXDE':
            os.system(f'pcmanfm --set-wallpaper="{img_path}"')
        elif desktop_env == 'XFCE':
            os.system(f'xfconf-query -c xfce4-desktop -p /backdrop/screen0/monitor0/workspace0/last-image -s "{img_path}"')
        elif desktop_env == 'MATE':
            os.system(f'gsettings set org.mate.background picture-filename "{img_path}"')
        elif desktop_env == 'Cinnamon':
            os.system(f'gsettings set org.cinnamon.desktop.background picture-uri "{img_path}"')
        elif desktop_env == 'Budgie':
            os.system(f'budgie-desktop --set-wallpaper="{img_path}"')
        elif desktop_env == 'Deepin':
            os.system(f'dde-desktop --set-wallpaper="{img_path}"')
        elif desktop_env == 'Unity':
            os.system(f'gsettings set com.canonical.Unity.Background picture-uri "{img_path}"')
        elif desktop_env == 'Deepin':
            os.system(f'dde-desktop --set-wallpaper="{img_path}"')
        else:
            logging.warning(f'当前桌面环境: {desktop_env} 不支持设置壁纸')


def isNetOK(testserver):
    s = socket.socket()
    s.settimeout(3)
    try:
        status = s.connect_ex(testserver)
        if status == 0:
            s.close()
            return True
        else:
            return False
    except Exception as e:
        return False


def isNetChainOK(testserver=('cn.bing.com', 443)):
    isOK = isNetOK(testserver)
    return isOK


def main(dir, p):
    if dir.startswith('~'):
        dir = os.path.expanduser(dir)
    # 等待时间
    try:
        wait = int(sys.argv[1]) if len(sys.argv) > 1 else 2
        wait = wait if wait > 0 else 0
    except ValueError as e:
        wait = 2
    # 获得图片文件名，包括后缀
    basename = "bingImage-%s.jpg" % time.strftime("%Y-%m-%d", time.localtime(time.time()))
    if not os.path.exists(dir):
        logging.info('文件夹[%s]不存在，重新建立' % dir)
        # os.mkdir(dir)
        os.makedirs(dir)
    # 拼接目录与文件名，得到图片路径
    file_path = os.path.join(dir, basename)
    use_4k = p == '4k'
    for i in range(300):
        if not os.path.isfile(file_path):
            # 根据网络状态判断是否需要延时请求
            if not isNetChainOK():
                time.sleep(wait)
                logging.info('internet is lost, wait %s' % wait)
                continue
            # 下载图片
            logging.info('start get img')
            get_img(file_path, use_4k)
            time.sleep(0.1)
        else:
            break
    for i in range(3):
        if os.path.isfile(file_path):
            # 文件小于4k，删除文件重新下载
            file_size = os.path.getsize(file_path)
            if file_size < 4096:
                os.remove(file_path)
                logging.info('delete because size[%s] < 4096' % file_size)
                time.sleep(5)
                continue
            # 设置壁纸
            logging.info('set img')
            set_img_as_wallpaper(file_path)
            break


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser()
    parser.add_argument('--dir', default='~/Pictures/bing', type=str, help='picture save dir')
    parser.add_argument('-q', choices=['4k', '1080', ], default='4k', help='picture quality')
    args = parser.parse_args()

    main(args.dir, args.q)
