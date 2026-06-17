import ctypes, time
from PIL import ImageGrab, Image

user32 = ctypes.windll.user32
CHROME_HWND = 328004

def click(x, y):
    user32.SetCursorPos(x, y)
    time.sleep(0.2)
    user32.mouse_event(2, 0, 0, 0, 0)
    time.sleep(0.05)
    user32.mouse_event(4, 0, 0, 0, 0)
    time.sleep(0.5)

def screenshot(name):
    img = ImageGrab.grab()
    img.save(name)
    print(f'Saglabats: {name}')
    return img

def minimize_terminals():
    def callback(hwnd, _):
        if user32.IsWindowVisible(hwnd):
            buf = ctypes.create_unicode_buffer(512)
            user32.GetWindowTextW(hwnd, buf, 512)
            if any(x in buf.value for x in ['xadobaltic', 'PowerShell', 'Windows Terminal']):
                user32.ShowWindow(hwnd, 6)
        return True
    user32.EnumWindows(ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_int, ctypes.c_int)(callback), 0)

minimize_terminals()
user32.SetForegroundWindow(CHROME_HWND)
time.sleep(1)

# 1. Noklikšķina uz Network (Tikls) cilnes DevTools - aptuveni x=870, y=145
click(870, 145)
time.sleep(0.5)

# 2. Iztīra iepriekšējos pieprasījumus (Ctrl+L vai iztīrīšanas poga)
# DevTools clear button ir aptuveni x=755, y=145
click(755, 145)
time.sleep(0.3)

screenshot('before_click.png')

# 3. Noklikšķina uz Kategorija dropdown (lapā kreisajā pusē)
# Pēc formas izskata, Kategorija ir aptuveni x=200, y=460
click(200, 460)
time.sleep(1)
screenshot('after_kategorija_click.png')

# 4. Ja parādās opcijas, izvēlas pirmo
# Scroll un meklē opcijas
time.sleep(0.5)
# Nospiediet Down arrow un Enter lai izvēlētos pirmo
user32.keybd_event(0x28, 0, 0, 0)  # VK_DOWN
time.sleep(0.2)
user32.keybd_event(0x28, 0, 2, 0)
time.sleep(0.3)
user32.keybd_event(0x0D, 0, 0, 0)  # VK_RETURN
time.sleep(0.1)
user32.keybd_event(0x0D, 0, 2, 0)
time.sleep(1.5)
screenshot('after_kategorija_select.png')

# 5. Skatos DevTools tīkla pieprasījumus
# Noklikšķina uz pirmā pieprasījuma DevTools
click(630, 250)
time.sleep(0.5)
screenshot('network_request.png')

print('Pabeigts!')
