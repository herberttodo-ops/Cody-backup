---
name: spreadsheet-reorganization
description: Clean up and restructure messy Excel/CSV files into well-organized, logical formats with unique IDs and multiple views.
triggers:
  - "spreadsheet is a mess"
  - "reorganize this excel"
  - "clean up this csv"
  - "review row and columns"
  - "restructure spreadsheet"
---

# Spreadsheet Reorganization

Clean up and restructure messy Excel/CSV files into well-organized, logical formats.

## When to Use

- Data is duplicated across multiple sheets
- Mixed content types in single lists
- No unique identifiers for cross-referencing
- Inconsistent or embedded metadata
- Need multiple views of same data
- User requests "review and reorganize"

## Procedure

### Phase 1: Analysis

1. **Extract and inventory all sheets**
   - If pandas available: `pd.ExcelFile(path).sheet_names`
   - Fallback: Parse XLSX as ZIP, read `xl/workbook.xml`

2. **Identify these common problems:**
   - Duplication (same records in multiple sheets)
   - Missing unique IDs
   - Text encoding (e.g., "channel1→channel2→channel3")
   - Inconsistent categorization
   - Empty critical fields (assignees, status)

3. **Count and categorize:**
   - Records by type
   - Distribution by status/priority
   - Identify orphaned records

### Phase 2: Design New Structure

**Create these standard outputs:**

1. **Master Inventory** - Canonical source with IDs
   - Columns: ID, Week, Date, Type, Title, Description, Keywords, Priority, Status, Assigned, Channel1, Channel2, Notes

2. **By Type View** - Same data, grouped by category
   - Use for batch work on similar items

3. **Chronological View** - Sorted by date/week
   - Use for scheduling and timeline planning

4. **Execution Dashboard** - Metrics and progress
   - Counts by status, type, priority
   - Completion percentages

5. **Specialized Sheets** - Platform-specific (Social, Email, etc.)
   - Cross-reference to Master via ID

### Phase 3: Implementation

1. **Assign unique IDs** (CNT-1000, CNT-1001, etc.)
2. **Parse channel text** into structured columns
3. **Flag empty required fields** (e.g., "UNASSIGNED")
4. **Sort consistently**: Week → Priority → Date
5. **Create cross-reference mappings** between sheets

### Phase 4: Export Options

**CSV approach** (works everywhere):
- Export each sheet as separate CSV
- Use `csv.DictWriter` for clean output

**XLSX rebuild** (if libraries available):
- Create workbook with multiple sheets
- Set frozen headers (pane ySplit="1")
- Apply basic styling to headers

## Common Anti-Patterns to Fix

| Problem | Solution |
|---------|----------|
| "Value→Arrow→Value" in cells | Split to Primary/Secondary columns |
| Duplicate records | Consolidate to one canonical sheet, reference by ID |
| 47 "types" of posts | Consolidate to 8-12 meaningful categories |
| Scattered dates | Sort chronologically, add week grouping |
| All "Not Started" | Ready the structure for status workflow |
| No owner assigned | Default to "UNASSIGNED" flag |

## Verification Checklist

- [ ] Every record has unique ID
- [ ] No duplication across sheets
- [ ] Dates sort correctly
- [ ] Status field ready for workflow
- [ ] Channel data structured
- [ ] Categories consolidated (8-12 max)
- [ ] Assigned field has value or flag

## Example Output Structure

```
/optirfp_reorganized/
├── 01_content_inventory.csv    (canonical)
├── 02_content_by_type.csv      (grouped view)
├── 03_weekly_calendar.csv      (chronological)
├── 04_social_media.csv         (specialized)
├── 05_lead_magnets.csv         (resources)
├── 06_execution_dashboard.csv  (metrics)
└── combined_workbook.xlsx      (all sheets)
```

## Pitfalls

- Don't lose data during consolidation - verify row counts
- Watch for date formatting issues when parsing
- Ensure unique IDs are actually unique
- Keep original file until new one is verified