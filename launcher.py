#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bilibili Followers Fetcher - 交互式启动器
同时支持源码版 (bilibili_followers_fetcher.py) 和 exe 版 (bilibili_followers_fetcher.exe)
"""

import os
import sys
import subprocess


def get_runner_path():
    """自动检测当前目录下的主程序"""
    # 打包为 exe 时用 sys.executable，源码运行时用 __file__
    if getattr(sys, "frozen", False):
        base = os.path.dirname(sys.executable)
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    py_path = os.path.join(base, "bilibili_followers_fetcher.py")
    exe_path = os.path.join(base, "bilibili_followers_fetcher.exe")
    if getattr(sys, "frozen", False):
        # 已打包为 exe → 优先找 .exe
        if os.path.isfile(exe_path):
            return exe_path
        if os.path.isfile(py_path):
            return py_path
    else:
        # 源码运行 → 优先找 .py
        if os.path.isfile(py_path):
            return py_path
        if os.path.isfile(exe_path):
            return exe_path
    return None


def build_cmd(runner, uid, delay, concurrent, fmt, filt, no_sort):
    """根据选择的配置构建命令行参数"""
    cmd = [sys.executable, runner] if runner.endswith(".py") else [runner]
    if uid:
        cmd.extend(["--uid", uid])
    cmd.extend(["--delay", delay])
    cmd.extend(["--concurrent", concurrent])
    if fmt == "json":
        cmd.extend(["--format", "json"])
    elif fmt == "html":
        cmd.extend(["--format", "html"])
    # both 是默认值，不传
    if filt == "none":
        cmd.extend(["--filter", "none"])
    elif filt == "avatar":
        cmd.extend(["--filter", "avatar"])
    elif filt == "bili":
        cmd.extend(["--filter", "bili"])
    # both 是默认值，不传
    if no_sort:
        cmd.append("--no-sort")
    return cmd


def show_help():
    """显示帮助信息"""
    print("=" * 50)
    print("    帮助信息 - Bilibili Followers Fetcher")
    print("=" * 50)
    print()
    print("可用参数：")
    print()
    print("  --format, -f  json / html / both")
    print("                导出格式（默认：both）")
    print("  --filter      none / avatar / bili / both")
    print("                过滤选项（默认：both）")
    print("  --no-sort     不按关注时间排序")
    print("  --uid         指定要查询的B站用户UID")
    print("  --delay       请求间最大延迟秒数 0.1~3.0（默认 1.0）")
    print("  --concurrent  粉丝统计阶段最大并发数 1~10（默认 3）")
    print()
    print("示例：")
    print("  launcher.exe --uid 1360948564")
    print("  launcher.exe --uid 1360948564 --delay 0.2 --concurrent 5")
    print("  python launcher.py --uid 1360948564")
    print()


def show_config(uid, delay, concurrent, fmt, filt, no_sort):
    """显示当前配置摘要"""
    parts = []
    parts.append(f"delay={delay}")
    parts.append(f"concurrent={concurrent}")
    parts.append(f"format={'both' if not fmt else fmt}")
    parts.append(f"filter={'both' if not filt else filt}")
    if no_sort:
        parts.append("no-sort")
    if uid:
        print(f"  UID: {uid}")
    print(f"  参数: {', '.join(parts)}")


def custom_config():
    """自定义配置流程，返回配置元组"""
    print()
    print("--- 自定义配置（直接回车=使用默认值）---")
    print()

    uid = input("目标 UID（默认=查询自己）: ").strip()

    delay = input("请求间隔 delay [0.1-3.0]（默认 1.0）: ").strip()
    if not delay:
        delay = "1.0"

    concurrent = input("并发数 [1-10]（默认 3）: ").strip()
    if not concurrent:
        concurrent = "3"

    print()
    print("输出格式：")
    print("  1. 仅 JSON")
    print("  2. 仅 HTML")
    print("  3. 两者都输出 [默认]")
    fmt_choice = input("请选择 [1-3]（回车=两者）: ").strip()
    fmt = ""
    if fmt_choice == "1":
        fmt = "json"
    elif fmt_choice == "2":
        fmt = "html"
    # 否则 fmt="" 表示 both（不传 --format 参数）

    print()
    print("过滤选项：")
    print("  1. 不过滤 (none)")
    print("  2. 过滤默认头像 (avatar)")
    print("  3. 过滤 bili_ 开头 (bili)")
    print("  4. 都过滤 [默认] (both)")
    filt_choice = input("请选择 [1-4]（回车=都过滤）: ").strip()
    filt = ""
    if filt_choice == "1":
        filt = "none"
    elif filt_choice == "2":
        filt = "avatar"
    elif filt_choice == "3":
        filt = "bili"
    # 否则 filt="" 表示 both（不传 --filter 参数）

    print()
    sort_choice = input("按粉丝数降序排序？[y/N]（回车=排序）: ").strip().lower()
    no_sort = sort_choice == "n"

    return uid, delay, concurrent, fmt, filt, no_sort


def main():
    runner = get_runner_path()
    if runner is None:
        print("错误：未找到 bilibili_followers_fetcher.exe 或 bilibili_followers_fetcher.py")
        print("请将本程序放在 bilibili_followers_fetcher 所在目录下运行。")
        input("\n按回车键退出...")
        sys.exit(1)

    # 检测运行模式
    is_py = runner.endswith(".py")
    mode_label = "源码版" if is_py else "exe版"

    # 配置参数（默认值）
    uid = ""
    delay = "1.0"
    concurrent = "3"
    fmt = ""
    filt = ""
    no_sort = False

    while True:
        os.system("cls" if os.name == "nt" else "clear")
        print("=" * 50)
        print(f"   Bilibili Followers Fetcher - 交互启动器 ({mode_label})")
        print("=" * 50)
        print()
        print("  1. 快速模式    (delay=0.2, concurrent=5)")
        print("  2. 均衡模式    (delay=1.0, concurrent=3) [默认]")
        print("  3. 保守模式    (delay=2.0, concurrent=1)")
        print("  4. 自定义配置")
        print("  5. 帮助信息")
        print("  0. 退出")
        print()
        print("当前配置：")
        show_config(uid, delay, concurrent, fmt, filt, no_sort)
        print()

        choice = input("请选择 [0-5]（直接回车=运行当前配置）: ").strip()

        if choice == "0":
            print("退出程序。")
            break
        elif choice == "1":
            delay = "0.2"
            concurrent = "5"
            print("已选择快速模式")
        elif choice == "2":
            delay = "1.0"
            concurrent = "3"
            print("已选择均衡模式")
        elif choice == "3":
            delay = "2.0"
            concurrent = "1"
            print("已选择保守模式")
        elif choice == "4":
            uid, delay, concurrent, fmt, filt, no_sort = custom_config()
        elif choice == "5":
            show_help()
            input("\n按回车键返回菜单...")
            continue
        elif choice == "":
            pass  # 直接运行当前配置
        else:
            print("无效输入，使用当前配置运行。")

        # 构建并运行命令
        cmd = build_cmd(runner, uid, delay, concurrent, fmt, filt, no_sort)
        print()
        print("=" * 50)
        print("  运行命令:", " ".join(cmd))
        print("=" * 50)
        print()

        ret = subprocess.run(cmd)
        print()
        if ret.returncode == 0:
            print(f"[完成] 程序已成功运行 (返回码: {ret.returncode})")
        else:
            print(f"[错误] 程序运行出错 (返回码: {ret.returncode})")

        input("\n按回车键返回菜单...")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n程序已手动中断。")
        sys.exit(0)
    except Exception as e:
        print(f"程序运行时出错: {e}")
        sys.exit(1)