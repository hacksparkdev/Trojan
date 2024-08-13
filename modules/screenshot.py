from PIL import ImageGrab
import io
import os

def is_display_available():
    return "DISPLAY" in os.environ

def run():
    if is_display_available():
        try:
            screenshot = ImageGrab.grab()
            buffer = io.BytesIO()
            screenshot.save(buffer, format='PNG')
            screenshot_data = buffer.getvalue()

            output_filename = 'screenshot_output.png'
            with open(output_filename, 'wb') as file:
                file.write(screenshot_data)

            return output_filename
        except Exception as e:
            return f"Failed to capture screenshot: {e}"
    else:
        return "No display available for capturing screenshot"

