from PIL import ImageGrab
import io

def run():
    screenshot = ImageGrab.grab()
    buffer = io.BytesIO()
    screenshot.save(buffer, format='PNG')
    screenshot_data = buffer.getvalue()

    with open('screenshot_output.png', 'wb') as file:
        file.write(screenshot_data)

    return 'screenshot_output.png'

