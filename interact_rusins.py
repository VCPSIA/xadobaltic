"""
Mijiedarbojas ar rusins.lv eļļu atlasi un tver API pieprasījumus.
Izmanto CDP (Chrome DevTools Protocol) caur remote debugging.
"""
import ctypes, time, subprocess
from PIL import ImageGrab, Image

user32 = ctypes.windll.user32
CHROME_HWND = 328004

def minimize_terminals():
    hwnd_list = []
    def callback(hwnd, _):
        if user32.IsWindowVisible(hwnd):
            buf = ctypes.create_unicode_buffer(512)
            user32.GetWindowTextW(hwnd, buf, 512)
            t = buf.value
            if any(x in t for x in ['xadobaltic', 'PowerShell', 'Windows Terminal']):
                hwnd_list.append(hwnd)
        return True
    user32.EnumWindows(ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_int, ctypes.c_int)(callback), 0)
    for h in hwnd_list:
        user32.ShowWindow(h, 6)

def show_chrome():
    user32.ShowWindow(CHROME_HWND, 3)
    user32.SetForegroundWindow(CHROME_HWND)
    time.sleep(1)

def screenshot(name):
    img = ImageGrab.grab()
    img.save(name)
    return img

def click(x, y):
    user32.SetCursorPos(x, y)
    time.sleep(0.1)
    user32.mouse_event(2, 0, 0, 0, 0)  # MOUSEEVENTF_LEFTDOWN
    time.sleep(0.05)
    user32.mouse_event(4, 0, 0, 0, 0)  # MOUSEEVENTF_LEFTUP
    time.sleep(0.3)

minimize_terminals()
show_chrome()
screenshot('step1_page.png')
print('1. Lapa ielādēta, ekrāns saglabāts')

# Pāriet uz Network cilni DevTools (nospiest F12 ja nav atvērts, tad Ctrl+Shift+I)
# DevTools parasti ir labajā pusē ekrāna
# Noklikšķina uz "Tikls" (Network) cilnes DevTools
# Atrod Network cilni - aptuveni pozīcijā

# Vispirms izdzēs esošos pieprasījumus ar Ctrl+Shift+Delete vai pogu Dzēst
# Tad izvēlas Kategorija -> Marka

time.sleep(2)
screenshot('step2_ready.png')
print('2. Gatavs interakcijai')
