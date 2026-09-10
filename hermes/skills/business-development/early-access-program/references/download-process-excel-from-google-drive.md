# Downloading Excel Files from Google Drive for Processing

## Problem

Google Drive stores Excel files (`.xlsx`) differently than native Google Sheets. The Sheets API returns:

```
HttpError 400: This operation is not supported for this document. 
The document must not be an Office file.
```

## Solution: Download via Drive API, Process Locally

### Step 1: Download the Excel File

```python
from google_api import build_service

drive_service = build_service('drive', 'v3')

FILE_ID = "YOUR_FILE_ID_HERE"

request = drive_service.files().get_media(fileId=FILE_ID)
file_path = "/tmp/downloaded_file.xlsx"

with open(file_path, "wb") as f:
    f.write(request.execute())
```

### Step 2: Process with openpyxl

```python
import openpyxl

wb = openpyxl.load_workbook(file_path)

# List sheet names
print(wb.sheetnames)

# Read a specific sheet
ws = wb['SheetName']

# Get headers
headers = [cell.value for cell in ws[1]]

# Iterate rows
for i in range(2, ws.max_row + 1):
    row_data = {}
    for j, header in enumerate(headers):
        if header:
            row_data[header] = ws.cell(row=i, column=j+1).value
    print(row_data)
```

### Step 3: Modify and Save

```python
from openpyxl.styles import Font, PatternFill, Alignment

# Add new column
ws.cell(row=1, column=ws.max_column + 1, value="New Column")
ws.cell(row=1, column=ws.max_column).font = Font(bold=True)

# Style header
ws.cell(row=1, column=ws.max_column).fill = PatternFill(
    start_color="366092", 
    end_color="366092", 
    fill_type="solid"
)

# Save modified file
wb.save("/tmp/modified_file.xlsx")
```

### Step 4: Upload Back to Google Drive

```python
from googleapiclient.http import MediaFileUpload

media = MediaFileUpload(
    "/tmp/modified_file.xlsx",
    mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    resumable=True
)

updated_file = drive_service.files().update(
    fileId=FILE_ID,
    media_body=media
).execute()

print(f"Updated: https://docs.google.com/spreadsheets/d/{FILE_ID}/edit")
```

## Key Tips

1. **Install openpyxl**: `pip install openpyxl` (in the active venv)
2. **Use `.xlsx` format**: The upload mimetype must match the file extension
3. **Preserve formatting**: openpyxl preserves most Excel formatting
4. **Handle large files**: Use `read_only=True` for very large files: `openpyxl.load_workbook(path, read_only=True)`
5. **Check sheet names**: `wb.sheetnames` before accessing a sheet

## Common Errors

| Error | Cause | Fix |
|-------|-------|-----|
| `HttpError 400: Office file` | Trying Sheets API on Excel file | Use Drive API to download |
| `ModuleNotFoundError: openpyxl` | Package not installed | `pip install openpyxl` |
| `KeyError: 'SheetName'` | Sheet doesn't exist | Check `wb.sheetnames` first |
| `Permission denied` on save | File open elsewhere | Close Excel, retry |
