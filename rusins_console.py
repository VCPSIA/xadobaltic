import ctypes, time, subprocess, sys
from PIL import ImageGrab, Image

user32 = ctypes.windll.user32
CHROME_HWND = 328004
VK_CONTROL = 0x11

def minimize_terminals():
    def callback(hwnd, _):
        if user32.IsWindowVisible(hwnd):
            buf = ctypes.create_unicode_buffer(512)
            user32.GetWindowTextW(hwnd, buf, 512)
            if any(x in buf.value for x in ['xadobaltic', 'PowerShell', 'Windows Terminal', 'CMD']):
                user32.ShowWindow(hwnd, 6)
        return True
    user32.EnumWindows(ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_int, ctypes.c_int)(callback), 0)

def shot(name):
    img = ImageGrab.grab()
    img.save(name)
    print(f'  -> {name}')
    return img

def zoom(img, x1, y1, x2, y2, name, w=1800):
    crop = img.crop((x1, y1, x2, y2))
    h = int(w * (y2-y1) / (x2-x1))
    crop.resize((w, h), Image.LANCZOS).save(name)
    print(f'  -> {name} (zoom)')

def click(x, y, delay=0.4):
    user32.SetCursorPos(x, y)
    time.sleep(0.1)
    user32.mouse_event(2, 0, 0, 0, 0)
    time.sleep(0.05)
    user32.mouse_event(4, 0, 0, 0, 0)
    time.sleep(delay)

def clipboard_paste(text):
    subprocess.Popen(['powershell', '-Command',
        f'$content = @\'\n{text}\n\'@; Set-Clipboard -Value $content'],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE).wait()
    time.sleep(0.3)
    user32.keybd_event(VK_CONTROL, 0, 0, 0)
    user32.keybd_event(0x56, 0, 0, 0)
    time.sleep(0.05)
    user32.keybd_event(0x56, 0, 2, 0)
    user32.keybd_event(VK_CONTROL, 0, 2, 0)
    time.sleep(0.3)

minimize_terminals()
user32.ShowWindow(CHROME_HWND, 3)
user32.SetForegroundWindow(CHROME_HWND)
time.sleep(1.2)

# Atver Chrome DevTools Console ar Ctrl+Shift+J
print('Atver DevTools Console...')
user32.keybd_event(VK_CONTROL, 0, 0, 0)
user32.keybd_event(0x10, 0, 0, 0)  # Shift
user32.keybd_event(0x4A, 0, 0, 0)  # J
time.sleep(0.1)
user32.keybd_event(0x4A, 0, 2, 0)
user32.keybd_event(0x10, 0, 2, 0)
user32.keybd_event(VK_CONTROL, 0, 2, 0)
time.sleep(2)

img = shot('c0_console.png')
zoom(img, 400, 100, 1366, 768, 'c0_zoom.png')

# Noklikšķina konsoles ievades rindu (apakšā pa labi)
# Konsoles ievade parasti ir apakšējā daļā
click(900, 700)
time.sleep(0.5)

# JS lai iegūtu visus script tagus un to URL
js1 = "Array.from(document.scripts).map(s=>s.src).filter(Boolean).join('\\n')"
print('Izpilda JS 1: iegūst script URLs...')
clipboard_paste(js1)
user32.keybd_event(0x0D, 0, 0, 0); time.sleep(0.05); user32.keybd_event(0x0D, 0, 2, 0)
time.sleep(1.5)

img = shot('c1_scripts.png')
zoom(img, 400, 400, 1366, 768, 'c1_zoom.png')

# Iztīra un izpilda nākamo JS
print('Izpilda JS 2: meklē AJAX funkcijas...')
click(900, 700)
time.sleep(0.3)
js2 = "Object.keys(window).filter(k=>['ajax','oil','catalog','elja','auto'].some(x=>k.toLowerCase().includes(x))).join(', ')"
clipboard_paste(js2)
user32.keybd_event(0x0D, 0, 0, 0); time.sleep(0.05); user32.keybd_event(0x0D, 0, 2, 0)
time.sleep(1.5)

img = shot('c2_globals.png')
zoom(img, 400, 300, 1366, 768, 'c2_zoom.png')

# jQuery AJAX intercept
print('Izpilda JS 3: jQuery AJAX setup...')
click(900, 700)
time.sleep(0.3)
js3 = "typeof jQuery !== 'undefined' ? 'jQuery ' + jQuery.fn.jquery + ' pieejams' : 'nav jQuery'"
clipboard_paste(js3)
user32.keybd_event(0x0D, 0, 0, 0); time.sleep(0.05); user32.keybd_event(0x0D, 0, 2, 0)
time.sleep(1.5)

img = shot('c3_jquery.png')
zoom(img, 400, 300, 1366, 768, 'c3_zoom.png')

# Meklē ajaxurl
print('Izpilda JS 4: ajaxurl...')
click(900, 700)
time.sleep(0.3)
js4 = "window.ajaxurl || window.ajax_url || window.wp_ajax || 'nav ajaxurl'"
clipboard_paste(js4)
user32.keybd_event(0x0D, 0, 0, 0); time.sleep(0.05); user32.keybd_event(0x0D, 0, 2, 0)
time.sleep(1.5)

img = shot('c4_ajaxurl.png')
zoom(img, 400, 300, 1366, 768, 'c4_zoom.png')

# WP localize vai citi globālie mainīgie
print('Izpilda JS 5: WP data...')
click(900, 700)
time.sleep(0.3)
js5 = "JSON.stringify(Object.fromEntries(Object.entries(window).filter(([k,v])=>typeof v==='object'&&v&&('ajax_url' in (v||{}) || 'nonce' in (v||{}) || 'action' in (v||{}))).slice(0,5)))"
clipboard_paste(js5)
user32.keybd_event(0x0D, 0, 0, 0); time.sleep(0.05); user32.keybd_event(0x0D, 0, 2, 0)
time.sleep(2)

img = shot('c5_wpdata.png')
zoom(img, 400, 200, 1366, 768, 'c5_zoom.png')

print('\nPabeigts! Pārbaudi c0_zoom.png..c5_zoom.png')
