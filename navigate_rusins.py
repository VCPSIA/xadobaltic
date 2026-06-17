import ctypes, time, subprocess, sys

user32 = ctypes.windll.user32
VK_CONTROL = 0x11
VK_RETURN = 0x0D
VK_L = 0x4C
VK_A = 0x41
VK_V = 0x56

def key_combo(vk1, vk2):
    user32.keybd_event(vk1, 0, 0, 0)
    time.sleep(0.08)
    user32.keybd_event(vk2, 0, 0, 0)
    time.sleep(0.08)
    user32.keybd_event(vk2, 0, 2, 0)
    time.sleep(0.08)
    user32.keybd_event(vk1, 0, 2, 0)
    time.sleep(0.1)

def set_clipboard(text):
    p = subprocess.Popen(['powershell', '-Command', f'Set-Clipboard -Value "{text}"'],
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    p.wait()

url = sys.argv[1] if len(sys.argv) > 1 else 'https://rusins.lv'

user32.SetForegroundWindow(328004)
time.sleep(0.8)
key_combo(VK_CONTROL, VK_L)
time.sleep(0.6)
key_combo(VK_CONTROL, VK_A)
time.sleep(0.2)
set_clipboard(url)
time.sleep(0.4)
key_combo(VK_CONTROL, VK_V)
time.sleep(0.4)
user32.keybd_event(VK_RETURN, 0, 0, 0)
time.sleep(0.1)
user32.keybd_event(VK_RETURN, 0, 2, 0)
print(f'Navigē: {url}')
time.sleep(5)

from PIL import ImageGrab
img = ImageGrab.grab()
img.save('rusins_nav.png')
print('Ekrāns saglabāts: rusins_nav.png')
