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
    print(f'  -> {name}')
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
time.sleep(0.8)

# 1. Ieslēdz Network cilni DevTools
# DevTools ir atvērts labajā pusē, Network cilne ir aptuveni x=865, y=145
print('1. Klikšķina Network cilni...')
click(865, 145)
time.sleep(0.5)

# 2. Iztīra network log
click(755, 145)
time.sleep(0.3)
screenshot('s1_network_clear.png')

# 3. Noklikšķina uz Kategorija dropdown
print('2. Atver Kategorija dropdown...')
click(200, 455)
time.sleep(1.0)
screenshot('s2_kategorija_open.png')

# 4. Noklikšķina uz "DZINĒJS UN TRANSMISIJA" (pirmā opcija ~ y=240)
print('3. Izvēlas DZINEEJS UN TRANSMISIJA...')
click(200, 240)
time.sleep(2.0)
screenshot('s3_after_kategorija.png')

# 5. Noklikšķina uz Marka dropdown
print('4. Atver Marka dropdown...')
click(200, 520)
time.sleep(1.0)
screenshot('s4_marka_open.png')

# 6. Noklikšķina uz pirmās markas (piemēram, Audi ~ y=250)
print('5. Izvēlas pirmo marku...')
click(200, 260)
time.sleep(2.0)
screenshot('s5_after_marka.png')

# 7. Skata Network pieprasījumus DevTools
print('6. Skata Network pieprasījumus...')
# Klikšķina uz pirmā pieprasījuma DevTools sarakstā
click(620, 300)
time.sleep(0.5)
screenshot('s6_network_request.png')

# Tuvina DevTools
img = ImageGrab.grab()
dt = img.crop((450, 100, 1350, 800))
dt2 = dt.resize((1800, 1400), Image.LANCZOS)
dt2.save('s7_devtools_zoom.png')
print('  -> s7_devtools_zoom.png')

print('Pabeigts!')
