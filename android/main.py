#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ZIP密码恢复工具 - Android版 (Kivy)
仅用于恢复自己遗忘密码的压缩包
"""

import os
import sys
import time
import itertools
import threading
from queue import Queue, Empty

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.progressbar import ProgressBar
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock
from kivy.core.window import Window

try:
    import pyzipper
except ImportError:
    try:
        import zipfile as pyzipper
    except ImportError:
        pyzipper = None


# 字符集预设
CHARSET_PRESETS = {
    'digits': '0123456789',
    'lower': 'abcdefghijklmnopqrstuvwxyz',
    'upper': 'ABCDEFGHIJKLMNOPQRSTUVWXYZ',
    'letters': 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ',
    'alphanum': '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ',
    'all': '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!@#$%^&*()_+-=[]{}|;:,.<>?/~`',
}

MASK_CHARS = {
    'd': '0123456789',
    'l': 'abcdefghijklmnopqrstuvwxyz',
    'u': 'ABCDEFGHIJKLMNOPQRSTUVWXYZ',
    's': '!@#$%^&*()_+-=[]{}|;:,.<>?/~`',
    'a': '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!@#$%^&*()_+-=[]{}|;:,.<>?/~`',
}


def mask_generator(mask):
    """掩码密码生成器"""
    parts = []
    i = 0
    while i < len(mask):
        if mask[i] == '?' and i + 1 < len(mask) and mask[i + 1] in MASK_CHARS:
            parts.append(MASK_CHARS[mask[i + 1]])
            i += 2
        else:
            parts.append(mask[i])
            i += 1
    for combo in itertools.product(*parts):
        yield ''.join(combo)


def brute_generator(charset, min_len, max_len):
    """暴力生成器"""
    for length in range(min_len, max_len + 1):
        for combo in itertools.product(charset, repeat=length):
            yield ''.join(combo)


def try_password(zip_path, pwd):
    """尝试单个密码"""
    try:
        with pyzipper.AESZipFile(zip_path) as zf:
            zf.setpassword(pwd.encode('utf-8'))
            for info in zf.infolist():
                with zf.open(info) as f:
                    f.read(1)
                break
        return True
    except:
        return False


class CrackerThread(threading.Thread):
    """破解工作线程"""
    def __init__(self, zip_path, mode, **kwargs):
        super().__init__()
        self.zip_path = zip_path
        self.mode = mode
        self.kwargs = kwargs
        self.found_password = None
        self.tried = 0
        self.total = 0
        self.running = False
        self.start_time = 0
        self.daemon = True

    def estimate_total(self):
        if self.mode == 'mask':
            mask = self.kwargs.get('mask', '')
            total = 1
            i = 0
            while i < len(mask):
                if mask[i] == '?' and i + 1 < len(mask) and mask[i + 1] in MASK_CHARS:
                    total *= len(MASK_CHARS[mask[i + 1]])
                    i += 2
                else:
                    i += 1
            return total
        elif self.mode == 'brute':
            charset = self.kwargs.get('charset', '')
            min_len = self.kwargs.get('min_len', 1)
            max_len = self.kwargs.get('max_len', 6)
            total = 0
            for l in range(min_len, max_len + 1):
                total += len(charset) ** l
            return total
        return 0

    def run(self):
        self.running = True
        self.start_time = time.time()
        self.total = self.estimate_total()

        if self.mode == 'mask':
            pwd_iter = mask_generator(self.kwargs.get('mask', ''))
        elif self.mode == 'brute':
            charset = self.kwargs.get('charset', CHARSET_PRESETS['digits'])
            pwd_iter = brute_generator(charset,
                                       self.kwargs.get('min_len', 1),
                                       self.kwargs.get('max_len', 6))
        else:
            return

        for pwd in pwd_iter:
            if not self.running:
                break
            self.tried += 1
            if try_password(self.zip_path, pwd):
                self.found_password = pwd
                break

        self.running = False


class ZipCrackerLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 20
        self.spacing = 10
        self.cracker = None

        # 标题
        self.add_widget(Label(
            text='ZIP密码恢复工具',
            font_size='24sp',
            size_hint_y=None,
            height=50
        ))

        # 文件路径输入
        self.add_widget(Label(text='压缩包路径：', size_hint_y=None, height=30))
        self.zip_path_input = TextInput(
            multiline=False,
            size_hint_y=None,
            height=40,
            hint_text='/sdcard/Download/secret.zip'
        )
        self.add_widget(self.zip_path_input)

        # 攻击模式选择
        self.add_widget(Label(text='攻击模式：', size_hint_y=None, height=30))
        self.mode_spinner = Spinner(
            text='掩码攻击',
            values=('掩码攻击', '暴力破解'),
            size_hint_y=None,
            height=40
        )
        self.mode_spinner.bind(text=self.on_mode_change)
        self.add_widget(self.mode_spinner)

        # 掩码输入
        self.mask_label = Label(text='掩码（?d数字 ?l小写 ?u大写 ?s符号）：', size_hint_y=None, height=30)
        self.add_widget(self.mask_label)
        self.mask_input = TextInput(
            multiline=False,
            size_hint_y=None,
            height=40,
            hint_text='例如：pass?d?d?d?d'
        )
        self.add_widget(self.mask_input)

        # 暴力破解参数
        self.brute_box = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=40,
            opacity=0,
            disabled=True
        )
        self.charset_spinner = Spinner(
            text='digits',
            values=list(CHARSET_PRESETS.keys()),
            size_hint_x=0.5
        )
        self.min_input = TextInput(text='1', multiline=False, size_hint_x=0.25, hint_text='最小')
        self.max_input = TextInput(text='6', multiline=False, size_hint_x=0.25, hint_text='最大')
        self.brute_box.add_widget(self.charset_spinner)
        self.brute_box.add_widget(self.min_input)
        self.brute_box.add_widget(self.max_input)
        self.add_widget(self.brute_box)

        # 开始/停止按钮
        self.start_btn = Button(
            text='开始破解',
            size_hint_y=None,
            height=50,
            background_color=(0.2, 0.6, 1, 1)
        )
        self.start_btn.bind(on_press=self.toggle_crack)
        self.add_widget(self.start_btn)

        # 进度条
        self.progress = ProgressBar(max=100, size_hint_y=None, height=30)
        self.add_widget(self.progress)

        # 状态输出
        self.status_label = Label(
            text='就绪',
            size_hint_y=None,
            height=30
        )
        self.add_widget(self.status_label)

        # 结果输出（可滚动）
        self.result_box = BoxLayout(orientation='vertical')
        self.result_input = TextInput(
            readonly=True,
            font_size='14sp'
        )
        self.result_box.add_widget(self.result_input)
        self.add_widget(self.result_box)

        # 定时更新进度
        Clock.schedule_interval(self.update_progress, 0.5)

    def on_mode_change(self, spinner, text):
        if text == '暴力破解':
            self.brute_box.opacity = 1
            self.brute_box.disabled = False
            self.mask_label.opacity = 0
            self.mask_input.disabled = True
            self.mask_input.opacity = 0
        else:
            self.brute_box.opacity = 0
            self.brute_box.disabled = True
            self.mask_label.opacity = 1
            self.mask_input.disabled = False
            self.mask_input.opacity = 1

    def toggle_crack(self, instance):
        if self.cracker and self.cracker.running:
            # 停止
            self.cracker.running = False
            self.start_btn.text = '开始破解'
            self.start_btn.background_color = (0.2, 0.6, 1, 1)
            self.status_label.text = '已停止'
        else:
            # 开始
            zip_path = self.zip_path_input.text.strip()
            if not zip_path or not os.path.exists(zip_path):
                self.status_label.text = '错误：文件不存在'
                return

            if pyzipper is None:
                self.status_label.text = '错误：pyzipper未安装'
                return

            mode = 'mask' if self.mode_spinner.text == '掩码攻击' else 'brute'

            if mode == 'mask':
                mask = self.mask_input.text.strip()
                if not mask:
                    self.status_label.text = '错误：请输入掩码'
                    return
                self.cracker = CrackerThread(zip_path, 'mask', mask=mask)
            else:
                charset = CHARSET_PRESETS.get(self.charset_spinner.text, CHARSET_PRESETS['digits'])
                try:
                    min_len = int(self.min_input.text)
                    max_len = int(self.max_input.text)
                except ValueError:
                    self.status_label.text = '错误：长度必须是数字'
                    return
                self.cracker = CrackerThread(zip_path, 'brute',
                                             charset=charset,
                                             min_len=min_len,
                                             max_len=max_len)

            self.cracker.start()
            self.start_btn.text = '停止'
            self.start_btn.background_color = (1, 0.3, 0.3, 1)
            self.result_input.text = ''
            self.status_label.text = '正在破解...'

    def update_progress(self, dt):
        if self.cracker and self.cracker.running:
            elapsed = time.time() - self.cracker.start_time
            speed = self.cracker.tried / elapsed if elapsed > 0 else 0
            if self.cracker.total > 0:
                pct = min(100, self.cracker.tried / self.cracker.total * 100)
                self.progress.value = pct
                eta = (self.cracker.total - self.cracker.tried) / speed if speed > 0 else 0
                self.status_label.text = (
                    f'已尝试: {self.cracker.tried:,} / {self.cracker.total:,} '
                    f'({pct:.1f}%) 速度: {speed:,.0f}/秒 '
                    f'剩余: {eta/60:.1f}分钟'
                )
            else:
                self.status_label.text = f'已尝试: {self.cracker.tried:,} 速度: {speed:,.0f}/秒'

        elif self.cracker and not self.cracker.running and self.cracker.tried > 0:
            # 破解完成
            if self.cracker.found_password:
                self.progress.value = 100
                self.status_label.text = '✅ 破解成功！'
                self.result_input.text = (
                    f'密码: {self.cracker.found_password}\n'
                    f'尝试次数: {self.cracker.tried:,}\n'
                    f'耗时: {time.time() - self.cracker.start_time:.1f}秒'
                )
            else:
                self.status_label.text = '❌ 未找到密码'
                self.result_input.text = (
                    f'已尝试: {self.cracker.tried:,} 个密码\n'
                    f'建议：尝试更大的字典或调整掩码'
                )
            self.start_btn.text = '开始破解'
            self.start_btn.background_color = (0.2, 0.6, 1, 1)
            self.cracker.tried = 0  # 防止重复触发


class ZipCrackerApp(App):
    def build(self):
        Window.clearcolor = (0.95, 0.95, 0.95, 1)
        return ZipCrackerLayout()

    def on_pause(self):
        return True


if __name__ == '__main__':
    ZipCrackerApp().run()
