#include <windows.h>
#include <stdio.h>
#include <time.h>

// Function to get the current timestamp and format it for the filename
void get_timestamp(char* buffer, int buffer_size) {
    time_t now = time(NULL);
    struct tm* t = localtime(&now);
    strftime(buffer, buffer_size, "screenshot_%Y%m%d_%H%M%S.bmp", t);
}

// Function to capture the screenshot and save it as a BMP file
void take_screenshot(const char* filename) {
    // Get the desktop window and its device context
    HWND hDesktopWnd = GetDesktopWindow();
    HDC hDesktopDC = GetDC(hDesktopWnd);
    HDC hCaptureDC = CreateCompatibleDC(hDesktopDC);
    
    // Get the width and height of the screen
    int width = GetSystemMetrics(SM_CXSCREEN);
    int height = GetSystemMetrics(SM_CYSCREEN);
    
    // Create a compatible bitmap from the screen device context
    HBITMAP hCaptureBitmap = CreateCompatibleBitmap(hDesktopDC, width, height);
    SelectObject(hCaptureDC, hCaptureBitmap);
    
    // BitBlt function copies the bits from one device context to another
    BitBlt(hCaptureDC, 0, 0, width, height, hDesktopDC, 0, 0, SRCCOPY | CAPTUREBLT);
    
    // Create a file to save the screenshot
    BITMAPFILEHEADER bmfHeader;
    BITMAPINFOHEADER bi;

    bi.biSize = sizeof(BITMAPINFOHEADER);    
    bi.biWidth = width;    
    bi.biHeight = height;  
    bi.biPlanes = 1;    
    bi.biBitCount = 24;    
    bi.biCompression = BI_RGB;    
    bi.biSizeImage = 0;  
    bi.biXPelsPerMeter = 0;    
    bi.biYPelsPerMeter = 0;    
    bi.biClrUsed = 0;    
    bi.biClrImportant = 0;

    DWORD dwBmpSize = ((width * bi.biBitCount + 31) / 32) * 4 * height;

    HANDLE hDIB = GlobalAlloc(GHND,dwBmpSize); 
    char *lpbitmap = (char *)GlobalLock(hDIB);    

    GetDIBits(hDesktopDC, hCaptureBitmap, 0,
        (UINT)height,
        lpbitmap,
        (BITMAPINFO *)&bi, DIB_RGB_COLORS);

    // Create a new file to save the screenshot
    HANDLE hFile = CreateFile(filename,
        GENERIC_WRITE,
        0,
        NULL,
        CREATE_ALWAYS,
        FILE_ATTRIBUTE_NORMAL, NULL);   

    // Write the file header
    DWORD dwSizeofDIB = dwBmpSize + sizeof(BITMAPFILEHEADER) + sizeof(BITMAPINFOHEADER);
    bmfHeader.bfOffBits = sizeof(BITMAPFILEHEADER) + sizeof(BITMAPINFOHEADER); 
    bmfHeader.bfSize = dwSizeofDIB; 
    bmfHeader.bfType = 0x4D42; //BM   
    DWORD dwBytesWritten = 0;
    WriteFile(hFile, (LPSTR)&bmfHeader, sizeof(BITMAPFILEHEADER), &dwBytesWritten, NULL);
    WriteFile(hFile, (LPSTR)&bi, sizeof(BITMAPINFOHEADER), &dwBytesWritten, NULL);
    WriteFile(hFile, (LPSTR)lpbitmap, dwBmpSize, &dwBytesWritten, NULL);

    // Close the file
    CloseHandle(hFile);

    // Clean up
    GlobalUnlock(hDIB);
    GlobalFree(hDIB);
    DeleteObject(hCaptureBitmap);
    ReleaseDC(hDesktopWnd, hDesktopDC);
    DeleteDC(hCaptureDC);
    
    printf("Screenshot saved as %s\n", filename);
}

int main() {
    char filename[100];
    get_timestamp(filename, sizeof(filename));
    take_screenshot(filename);
    return 0;
}

