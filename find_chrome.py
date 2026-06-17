import ctypes

user32 = ctypes.windll.user32

results = []
def callback(hwnd, _):
    if user32.IsWindowVisible(hwnd):
        buf = ctypes.create_unicode_buffer(512)
        user32.GetWindowTextW(hwnd, buf, 512)
        title = buf.value
        if title:
            cls = ctypes.create_unicode_buffer(256)
            user32.GetClassNameW(hwnd, cls, 256)
            results.append((hwnd, cls.value, title))
    return True

user32.EnumWindows(ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_int, ctypes.c_int)(callback), 0)

print('=== Chrome logi ===')
for hwnd, cls, title in results:
    if 'Chrome' in cls or 'chrome' in title.lower() or 'rusins' in title.lower() or 'Google' in title:
        print(f'HWND={hwnd} cls={cls}: {title[:80]}')

print('\n=== Visi redzamie logi ===')
for hwnd, cls, title in results[:30]:
    print(f'HWND={hwnd} cls={cls[:20]}: {title[:60]}')
