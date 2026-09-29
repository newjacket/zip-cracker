#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ZIP压缩包密码恢复工具
支持：字典攻击、掩码攻击、字符集暴力破解（短密码）
多进程加速，进度实时显示

⚠️  合法用途声明：本工具仅用于恢复自己遗忘密码的压缩包，
   禁止用于破解他人加密文件、窃取数据等非法用途。
   使用者需自行承担法律责任。
"""

import sys
import os
import time
import argparse
import itertools
import multiprocessing as mp
from queue import Empty

try:
    import pyzipper
except ImportError:
    try:
        import zipfile as pyzipper
    except ImportError:
        print("[错误] 请先安装 pyzipper: pip install pyzipper")
        sys.exit(1)


# ============================================================
# 密码生成器
# ============================================================

CHARSET_PRESETS = {
    'digits': '0123456789',
    'lower': 'abcdefghijklmnopqrstuvwxyz',
    'upper': 'ABCDEFGHIJKLMNOPQRSTUVWXYZ',
    'letters': 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ',
    'alphanum': '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ',
    'all': '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!@#$%^&*()_+-=[]{}|;:,.<>?/~`',
}


def mask_generator(mask):
    """
    掩码攻击生成器
    掩码规则：
      ?d = 数字 (0-9)
      ?l = 小写字母 (a-z)
      ?u = 大写字母 (A-Z)
      ?s = 特殊符号
      ?a = 全部可打印字符
      ?l?u = 大小写字母
      其他字符 = 固定字符
    示例：
      pass?d?d?d?d  ->  pass0000 ~ pass9999
      ?l?l?l123     ->  aaa123 ~ zzz123
    """
    char_map = {
        'd': CHARSET_PRESETS['digits'],
        'l': CHARSET_PRESETS['lower'],
        'u': CHARSET_PRESETS['upper'],
        's': '!@#$%^&*()_+-=[]{}|;:,.<>?/~`',
        'a': CHARSET_PRESETS['all'],
    }

    # 解析掩码
    parts = []
    i = 0
    while i < len(mask):
        if mask[i] == '?' and i + 1 < len(mask):
            key = mask[i + 1]
            if key in char_map:
                parts.append(char_map[key])
                i += 2
                continue
        parts.append(mask[i])
        i += 1

    # 生成所有组合
    for combo in itertools.product(*parts):
        yield ''.join(combo)


def brute_generator(charset, min_len, max_len):
    """字符集暴力生成器"""
    for length in range(min_len, max_len + 1):
        for combo in itertools.product(charset, repeat=length):
            yield ''.join(combo)


def dict_generator(dict_file):
    """字典生成器"""
    with open(dict_file, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            pwd = line.strip()
            if pwd:
                yield pwd


# ============================================================
# 密码验证（Worker进程）
# ============================================================

def worker_try_passwords(task_queue, result_queue, zip_path, stop_event):
    """工作进程：批量尝试密码"""
    try:
        while not stop_event.is_set():
            try:
                batch = task_queue.get(timeout=1.0)
            except Empty:
                break

            if batch is None:
                break

            found = None
            for pwd in batch:
                if stop_event.is_set():
                    break
                try:
                    with pyzipper.AESZipFile(zip_path) as zf:
                        zf.setpassword(pwd.encode('utf-8'))
                        # 尝试读取第一个文件的一小段数据来验证密码
                        for info in zf.infolist():
                            with zf.open(info) as f:
                                f.read(1)
                            break
                    found = pwd
                    break
                except (RuntimeError, Exception):
                    continue

            if found:
                result_queue.put(('found', found))
                stop_event.set()
            else:
                result_queue.put(('progress', len(batch)))
    except KeyboardInterrupt:
        pass
    except Exception as e:
        result_queue.put(('error', str(e)))


# ============================================================
# 主程序
# ============================================================

def estimate_combinations(mode, mask, charset, min_len, max_len, dict_file):
    """估算密码组合总数"""
    if mode == 'dict':
        try:
            with open(dict_file, 'r', encoding='utf-8', errors='ignore') as f:
                return sum(1 for _ in f)
        except:
            return 0
    elif mode == 'mask':
        total = 1
        char_map = {
            'd': 10, 'l': 26, 'u': 26, 's': 32, 'a': 94,
        }
        i = 0
        while i < len(mask):
            if mask[i] == '?' and i + 1 < len(mask) and mask[i + 1] in char_map:
                total *= char_map[mask[i + 1]]
                i += 2
            else:
                i += 1
        return total
    else:  # brute
        total = 0
        for l in range(min_len, max_len + 1):
            total += len(charset) ** l
        return total


def format_number(n):
    """格式化大数字"""
    if n >= 1e12:
        return f"{n/1e12:.2f}万亿"
    elif n >= 1e8:
        return f"{n/1e8:.2f}亿"
    elif n >= 1e4:
        return f"{n/1e4:.2f}万"
    else:
        return str(n)


def main():
    parser = argparse.ArgumentParser(
        description='ZIP压缩包密码恢复工具（仅用于恢复自己的压缩包密码）',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例：
  # 1. 字典攻击（推荐，效率最高）
  python zip_cracker.py -f secret.zip -m dict -d passwords.txt

  # 2. 掩码攻击（知道密码部分结构时）
  python zip_cracker.py -f secret.zip -m mask -k "pass?d?d?d?d"

  # 3. 纯数字暴力破解（1-6位）
  python zip_cracker.py -f secret.zip -m brute -c digits --min 1 --max 6

  # 4. 大小写字母+数字暴力破解（1-4位）
  python zip_cracker.py -f secret.zip -m brute -c alphanum --min 1 --max 4

掩码规则：?d=数字 ?l=小写 ?u=大写 ?s=符号 ?a=全部
        """
    )
    parser.add_argument('-f', '--file', required=True, help='压缩包文件路径')
    parser.add_argument('-m', '--mode', choices=['dict', 'mask', 'brute'],
                        default='dict', help='攻击模式：dict=字典, mask=掩码, brute=暴力')
    parser.add_argument('-d', '--dict', help='字典文件路径（dict模式）')
    parser.add_argument('-k', '--mask', help='掩码字符串（mask模式）')
    parser.add_argument('-c', '--charset', default='digits',
                        choices=list(CHARSET_PRESETS.keys()),
                        help='字符集预设（brute模式）')
    parser.add_argument('--custom-charset', help='自定义字符集（brute模式，覆盖-c）')
    parser.add_argument('--min', type=int, default=1, help='最小密码长度（brute模式）')
    parser.add_argument('--max', type=int, default=6, help='最大密码长度（brute模式）')
    parser.add_argument('-w', '--workers', type=int, default=mp.cpu_count(),
                        help='工作进程数（默认=CPU核心数）')
    parser.add_argument('-b', '--batch', type=int, default=500,
                        help='每批密码数量（影响进度更新频率）')

    args = parser.parse_args()

    # 检查文件
    if not os.path.exists(args.file):
        print(f"[错误] 文件不存在: {args.file}")
        sys.exit(1)

    # 确定字符集
    charset = args.custom_charset if args.custom_charset else CHARSET_PRESETS[args.charset]

    # 估算组合数
    total = estimate_combinations(args.mode, args.mask, charset, args.min, args.max, args.dict)

    print("=" * 60)
    print("  ZIP压缩包密码恢复工具")
    print("=" * 60)
    print(f"  目标文件: {args.file}")
    print(f"  攻击模式: {args.mode}")
    print(f"  工作进程: {args.workers}")
    if total > 0:
        print(f"  密码组合: {format_number(total)} ({total:,})")
        if total > 100_000_000_000:
            print(f"  ⚠️  组合数过大，纯暴力破解预计需要极长时间，建议使用字典或掩码模式")
    print("=" * 60)

    # 模式参数检查
    if args.mode == 'dict' and not args.dict:
        print("[错误] 字典模式需要指定 -d 字典文件路径")
        sys.exit(1)
    if args.mode == 'mask' and not args.mask:
        print("[错误] 掩码模式需要指定 -k 掩码字符串")
        sys.exit(1)

    # 生成密码迭代器
    if args.mode == 'dict':
        pwd_iter = dict_generator(args.dict)
    elif args.mode == 'mask':
        pwd_iter = mask_generator(args.mask)
    else:
        pwd_iter = brute_generator(charset, args.min, args.max)

    # 多进程设置
    task_queue = mp.Queue(maxsize=args.workers * 4)
    result_queue = mp.Queue()
    stop_event = mp.Event()

    workers = []
    for _ in range(args.workers):
        p = mp.Process(
            target=worker_try_passwords,
            args=(task_queue, result_queue, args.file, stop_event)
        )
        p.daemon = True
        p.start()
        workers.append(p)

    # 主进程：分发任务 + 收集进度
    start_time = time.time()
    tried = 0
    found_pwd = None
    batch = []

    print("\n[开始破解] 按 Ctrl+C 可随时停止\n")

    try:
        for pwd in pwd_iter:
            if stop_event.is_set():
                break
            batch.append(pwd)
            if len(batch) >= args.batch:
                task_queue.put(batch)
                batch = []

            # 收集进度
            while not result_queue.empty():
                try:
                    msg_type, msg_data = result_queue.get_nowait()
                    if msg_type == 'found':
                        found_pwd = msg_data
                        break
                    elif msg_type == 'progress':
                        tried += msg_data
                    elif msg_type == 'error':
                        print(f"\n[Worker错误] {msg_data}")
                except Empty:
                    break

            if found_pwd:
                break

            # 进度显示
            if tried > 0 and tried % (args.batch * 10) == 0:
                elapsed = time.time() - start_time
                speed = tried / elapsed if elapsed > 0 else 0
                pct = (tried / total * 100) if total > 0 else 0
                eta = (total - tried) / speed if speed > 0 else 0
                print(f"\r  进度: {tried:,}/{total:,} ({pct:.1f}%) | "
                      f"速度: {speed:,.0f}/秒 | "
                      f"已用: {elapsed:.0f}秒 | "
                      f"预计剩余: {eta/60:.1f}分钟", end='', flush=True)

        # 发送最后一批
        if batch and not stop_event.is_set():
            task_queue.put(batch)

        # 等待所有任务完成
        while not stop_event.is_set():
            time.sleep(0.1)
            # 检查是否所有worker都空闲
            if task_queue.empty():
                all_idle = True
                for p in workers:
                    if p.is_alive():
                        all_idle = False
                        break
                if all_idle:
                    break

            while not result_queue.empty():
                try:
                    msg_type, msg_data = result_queue.get_nowait()
                    if msg_type == 'found':
                        found_pwd = msg_data
                        stop_event.set()
                    elif msg_type == 'progress':
                        tried += msg_data
                except Empty:
                    break

    except KeyboardInterrupt:
        print("\n\n[用户中断] 正在停止...")
        stop_event.set()

    # 停止所有worker
    stop_event.set()
    for _ in range(args.workers):
        try:
            task_queue.put_nowait(None)
        except:
            pass
    for p in workers:
        p.join(timeout=3)
        if p.is_alive():
            p.terminate()

    elapsed = time.time() - start_time

    print("\n" + "=" * 60)
    if found_pwd:
        print(f"  ✅ 密码破解成功！")
        print(f"  密码: {found_pwd}")
        print(f"  尝试次数: {tried:,}")
        print(f"  耗时: {elapsed:.1f}秒")
        # 保存结果
        result_file = args.file + '.password.txt'
        with open(result_file, 'w', encoding='utf-8') as f:
            f.write(f"文件: {args.file}\n")
            f.write(f"密码: {found_pwd}\n")
            f.write(f"尝试次数: {tried}\n")
            f.write(f"耗时: {elapsed:.1f}秒\n")
        print(f"  结果已保存: {result_file}")
    else:
        print(f"  ❌ 未找到密码")
        print(f"  已尝试: {tried:,} 个密码")
        print(f"  耗时: {elapsed:.1f}秒")
        if args.mode == 'brute':
            print(f"  建议：尝试更大的字符集或更长的密码长度，或改用字典/掩码模式")
        elif args.mode == 'dict':
            print(f"  建议：使用更大的字典文件，或尝试掩码模式")
    print("=" * 60)

    return 0 if found_pwd else 1


if __name__ == '__main__':
    mp.freeze_support()
    sys.exit(main())
