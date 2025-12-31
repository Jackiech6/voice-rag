# File Upload Troubleshooting Guide

## Issue: "Upload failed: Not Found"

If you're seeing "Upload failed: Not Found" when uploading a PDF file, follow these steps:

### 1. Restart the Server

The most common cause is that the server is running old code. **Restart the server** after the code updates:

```bash
# Stop the current server (Ctrl+C)
# Then restart it:
cd /Users/chenjackie/Desktop/WRDS
source venv/bin/activate
python api.py
```

### 2. Verify the Endpoint is Available

Check that the server is running and the endpoint exists:

```bash
curl http://localhost:8000/
```

You should see `"upload": "/documents/upload"` in the endpoints list.

### 3. Check Browser Console

Open your browser's developer console (F12) and check for:
- CORS errors
- Network errors
- JavaScript errors

### 4. Verify File Format

Make sure you're uploading a **valid PDF file**:
- The file should have a `.pdf` extension
- The file should be a real PDF (not just renamed)
- Try with a simple PDF first to test

### 5. Check File Size

The maximum file size is **50MB**. If your file is larger, it will be rejected.

### 6. Test with a Simple File

Try uploading a simple text file first to verify the upload mechanism works:

1. Create a file `test.txt` with some text
2. Upload it via the web interface
3. If that works, the issue is likely with the PDF file itself

### 7. Check Server Logs

Look at the server terminal output for error messages. Common errors:
- `Failed to open file` - PDF is corrupted or invalid
- `File not found` - Temporary file issue
- `Processing error` - PDF cannot be parsed

### 8. Common Issues and Solutions

#### Issue: "Failed to open file"
**Cause**: The PDF file is corrupted or not a valid PDF
**Solution**: 
- Try opening the PDF in a PDF viewer first
- Re-save the PDF if possible
- Try a different PDF file

#### Issue: "Not Found" (404)
**Cause**: Server not running or endpoint not registered
**Solution**:
- Restart the server
- Check that `api.py` has the `/documents/upload` endpoint
- Verify the server is running on `http://localhost:8000`

#### Issue: CORS Error
**Cause**: Browser blocking the request
**Solution**:
- Check that CORS is enabled in `api.py`
- Make sure you're accessing via `http://localhost:8000` (not `file://`)

#### Issue: Empty File Error
**Cause**: File is empty or couldn't be read
**Solution**:
- Check file size
- Try a different file
- Check file permissions

### 9. Manual Test

Test the endpoint directly with curl:

```bash
curl -X POST "http://localhost:8000/documents/upload" \
  -F "file=@your_file.pdf"
```

If this works, the issue is in the frontend. If it doesn't, check the server error message.

### 10. Verify Code Updates

Make sure all files are updated:
- `api.py` - Should have `/documents/upload` endpoint
- `ingestion_service.py` - Should exist and be importable
- `static/index.html` - Should have upload UI

### Still Having Issues?

1. Check the server terminal for detailed error messages
2. Check the browser console for JavaScript errors
3. Try uploading a text file instead of PDF to isolate the issue
4. Verify the PDF file opens correctly in a PDF viewer

## Expected Behavior

When upload works correctly:
1. File is selected/dropped
2. Progress bar appears and fills
3. Success message: "✅ Successfully uploaded: [filename] ([N] chunks)"
4. Document appears in the documents list below
5. You can immediately query the document

## Error Messages Explained

- **"Not Found"** - Endpoint not found (server needs restart)
- **"Failed to open file"** - PDF is invalid/corrupted
- **"File too large"** - File exceeds 50MB limit
- **"Unsupported file type"** - File is not PDF, TXT, or MD
- **"Error processing document"** - PDF cannot be parsed

