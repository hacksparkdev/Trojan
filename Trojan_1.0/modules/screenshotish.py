import os
import win32api
import win32con
import win32gui
import win32ui

def get_dimensions():
    width = win32api.GetSystemMetrics(win32con.SM_CXVIRTUALSCREEN)
    height = win32api.GetSystemMetrics(win32con.SM_CYVIRTUALSCREEN)
    left = win32api.GetSystemMetrics(win32con.SM_XVIRTUALSCREEN)
    top = win32api.GetSystemMetrics(win32con.SM_YVIRTUALSCREEN)
    return (width, height, left, top)

def screenshot(directory='screen', name='screenshot'):
    # Create the directory if it doesn't exist
    if not os.path.exists(directory):
        os.makedirs(directory)

    hdesktop = win32gui.GetDesktopWindow()
    width, height, left, top = get_dimensions()

    desktop_dc = win32gui.GetWindowDC(hdesktop)
    img_dc = win32ui.CreateDCFromHandle(desktop_dc)
    mem_dc = img_dc.CreateCompatibleDC()

    screenshot_bitmap = win32ui.CreateBitmap()
    screenshot_bitmap.CreateCompatibleBitmap(img_dc, width, height)
    mem_dc.SelectObject(screenshot_bitmap)

    mem_dc.BitBlt((0, 0), (width, height), img_dc, (left, top), win32con.SRCCOPY)

    file_path = os.path.join(directory, f'{name}.bmp')
    screenshot_bitmap.SaveBitmapFile(mem_dc, file_path)

    mem_dc.DeleteDC()
    win32gui.DeleteObject(screenshot_bitmap.GetHandle())

    print(f"Screenshot saved to {file_path}")

def run():
    screenshot()
    with open('screen/screenshot.bmp', 'rb') as f:  # Updated to reflect the new directory
        img = f.read()
    return img

if __name__ == '__main__':
    screenshot()

