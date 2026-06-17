import ctypes, time, subprocess
from PIL import ImageGrab, Image

user32 = ctypes.windll.user32
CHROME_HWND = 328004
VK_CONTROL = 0x11
VK_U = 0x55

def key_combo(vk1, vk2):
    user32.keybd_event(vk1, 0, 0, 0)
    time.sleep(0.05)
    user32.keybd_event(vk2, 0, 0, 0)
    time.sleep(0.05)
    user32.keybd_event(vk2, 0, 2, 0)
    time.sleep(0.05)
    user32.keybd_event(vk1, 0, 2, 0)
    time.sleep(0.3)

def minimize_terminals():
    def callback(hwnd, _):
        if user32.IsWindowVisible(hwnd):
            buf = ctypes.create_unicode_buffer(512)
            user32.GetWindowTextW(hwnd, buf, 512)
            if any(x in buf.value for x in ['xadobaltic', 'PowerShell', 'Windows Terminal']):
                user32.ShowWindow(hwnd, 6)
        return True
    user32.EnumWindows(ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_int, ctypes.c_int)(callback), 0)

def set_clipboard(text):
    subprocess.Popen(['powershell', '-Command', f'Set-Clipboard -Value \'{text}\''],
                     stdout=subprocess.PIPE, stderr=subprocess.PIPE).wait()

def click(x, y):
    user32.SetCursorPos(x, y)
    time.sleep(0.15)
    user32.mouse_event(2, 0, 0, 0, 0)
    time.sleep(0.05)
    user32.mouse_event(4, 0, 0, 0, 0)
    time.sleep(0.4)

minimize_terminals()
user32.ShowWindow(CHROME_HWND, 3)
user32.SetForegroundWindow(CHROME_HWND)
time.sleep(1)

# Atver Console (Ctrl+Shift+J)
print('Atver DevTools Console...')
user32.keybd_event(VK_CONTROL, 0, 0, 0)
user32.keybd_event(0x10, 0, 0, 0)  # Shift
user32.keybd_event(0x4A, 0, 0, 0)  # J
time.sleep(0.1)
user32.keybd_event(0x4A, 0, 2, 0)
user32.keybd_event(0x10, 0, 2, 0)
user32.keybd_event(VK_CONTROL, 0, 2, 0)
time.sleep(1.5)

img = ImageGrab.grab()
img.save('console_open.png')
print('Konsole atvērta')

# Ievada JS lai iegūtu AJAX/fetch URLs
js_code = "JSON.stringify(performance.getEntriesByType('resource').filter(r=>r.initiatorType=='xmlhttprequest'||r.initiatorType=='fetch').map(r=>r.name))"

# Noklikšķina konsoles ievades laukā (parasti apakšā)
click(900, 1020)
time.sleep(0.5)

set_clipboard(js_code)
time.sleep(0.3)
key_combo(VK_CONTROL, 0x56)  # Ctrl+V
time.sleep(0.3)
user32.keybd_event(0x0D, 0, 0, 0)
time.sleep(0.1)
user32.keybd_event(0x0D, 0, 2, 0)
time.sleep(1)

img = ImageGrab.grab()
img.save('console_result.png')
# Tuvina konsoles rezultātu
cons = img.crop((450, 700, 1400, 1080))
cons2 = cons.resize((1900, 760), Image.LANCZOS)
cons2.save('console_result_zoom.png')
print('Rezultāts saglabāts')
