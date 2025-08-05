# 🎯 Comprehensive Linter Cleanup Guide

## 📊 Overview

This guide provides a systematic approach to cleaning up linter warnings and errors in both Python (.py) and Markdown (.md) files, based on real-world experience with the N2S TMMi Tracker codebase.

## 🔍 Initial Assessment

### Step 1: Install and Check Linters

```bash

# Activate virtual environment
source venv/bin/activate

# Install required linters
pip install flake8 pylint black

# Check current status
flake8 . --exclude=venv --count --show-source --statistics

```

### Step 2: Categorize Issues by Priority

#### 🟢 **CRITICAL FIXES (Must Fix)**

- **W292**: Missing newline at end of file

- **E226**: Missing whitespace around arithmetic operator

- **E501**: Line too long (>120 characters)

- **E128**: Continuation line under-indented for visual indent

- **F841**: Local variable assigned but never used

- **W504**: Line break after binary operator

- **W391**: Blank line at end of file

- **MD010**: Hard tabs in markdown files

- **MD022**: Headings should be surrounded by blank lines

- **MD031**: Fenced code blocks should be surrounded by blank lines

- **MD012**: Multiple consecutive blank lines

- **MD032**: Lists should be surrounded by blank lines

- **MD029**: Ordered list item prefix (should start with 1, not 2, 3, etc.)

#### 🟡 **STYLE IMPROVEMENTS (Should Fix)**

- **W0718**: Catching too general exception Exception

- **W1514**: Using open without explicitly specifying an encoding

- **W1203**: Use lazy % formatting in logging functions

- **W0611**: Unused imports

- **W0613**: Unused arguments

- **R1705**: Unnecessary "else" after "return"

- **R0914**: Too many local variables

- **R0912**: Too many branches

- **R0915**: Too many statements

## 🛠️ Systematic Fix Process

### Phase 1: Quick Wins (15 minutes)

#### 1. Fix Missing Newlines (W292)

```bash

# Add newlines to files
echo -e "\n" >> src/__init__.py
echo -e "\n" >> src/components/debug.py
echo -e "\n" >> src/components/manual_sample.py
echo -e "\n" >> src/components/progress.py
echo -e "\n" >> src/utils/__init__.py
echo -e "\n" >> src/utils/sample_data.py

```

#### 2. Fix Whitespace Around Operators (E226)

```python

# Before
status_text.text(f"Creating assessment {i+1}: {scenario['desc']}")

# After
status_text.text(f"Creating assessment {i + 1}: {scenario['desc']}")

```

#### 3. Fix Line Length Issues (E501)

```python

# Before
logging.info(f"Verification - Organizations: {len(verification_orgs)}, Assessments: {len(verification_assessments)}")

# After
logging.info(f"Verification - Organizations: {len(verification_orgs)}, "
            f"Assessments: {len(verification_assessments)}")

```

#### 4. Remove Unused Variables (F841)

```python

# Before
assessment_id = db.save_assessment(assessment)

# After
db.save_assessment(assessment)

```

### Phase 2: Indentation Fixes (20 minutes)

#### Fix Continuation Line Indentation (E128)

```python

# Before
evidence_url=(f"https://docs.sampletest.org/{question.id.lower()}"
             if answer == 'Yes' and i > 3 else None),

# After
evidence_url=(f"https://docs.sampletest.org/{question.id.lower()}"
             if answer == 'Yes' and i > 3 else None),

```

#### Fix Line Break Style (W504)

```python

# Before
hovertemplate='<b>Date:</b> %{x|%Y-%m-%d}<br>' +
              '<b>TMMi Level:</b> %{y}<br>' +
              '<b>Compliance:</b> %{customdata:.1f}%<extra></extra>',

# After
hovertemplate=('<b>Date:</b> %{x|%Y-%m-%d}<br>'
               + '<b>TMMi Level:</b> %{y}<br>'
               + '<b>Compliance:</b> %{customdata:.1f}%<extra></extra>'),

```

### Phase 3: Markdown Cleanup (10 minutes)

#### Fix Hard Tabs (MD010)

```bash

# Replace all hard tabs with 4 spaces
sed -i '' 's/\t/    /g' prompts/original_prompt.md

# Verify no tabs remain
grep -n $'\t' *.md prompts/*.md

```

#### Fix Heading Spacing (MD022)

```bash

# Add blank lines before all heading levels
sed -i '' 's/^##/\n##/g' *.md prompts/*.md
sed -i '' 's/^###/\n###/g' *.md prompts/*.md
sed -i '' 's/^####/\n####/g' *.md prompts/*.md
sed -i '' 's/^#####/\n#####/g' *.md prompts/*.md
sed -i '' 's/^######/\n######/g' *.md prompts/*.md

```

#### Remove Trailing Whitespace

```bash

# Remove trailing whitespace from all markdown files
sed -i '' 's/[[:space:]]*$//' *.md prompts/*.md

```

#### Fix Multiple Blank Lines (MD012)

```bash

# Remove multiple consecutive blank lines (zsh compatible)

# Use awk instead of sed for better zsh compatibility
awk 'NF {print; blank=0} !NF {if (!blank) print; blank=1}' *.md prompts/*.md > temp.md && mv temp.md *.md prompts/*.md

# Alternative: use perl for complex operations
perl -i -pe 's/\n\s*\n\s*\n/\n\n/g' *.md prompts/*.md

```

#### Fix List Spacing (MD032)

```bash

# Add blank lines around numbered lists (zsh compatible)
for file in *.md prompts/*.md; do
  # Add blank line before numbered lists
  sed -i '' 's/^\([0-9]\.\)/\n\1/g' "$file"
  # Add blank line after lists (before next heading or section)
  sed -i '' 's/^\([0-9]\. .*\)$/\1\n/g' "$file"
done

```

#### Fix Ordered List Prefix (MD029)

```bash

# Fix ordered lists to start with 1 (zsh compatible)
for file in *.md prompts/*.md; do
  # Replace all numbered list items to start with 1
  sed -i '' 's/^[2-9]\./1./g' "$file"
done

```

### Phase 4: Auto-Formatting (5 minutes)

#### Use Black for Complex Indentation

```bash

# Auto-format problematic files
black src/components/manual_sample.py src/components/progress.py src/utils/sample_data.py

```

## 📋 Verification Checklist

### After Each Phase

```bash

# Check flake8 status
source venv/bin/activate && flake8 . --exclude=venv --count

# Should show 0 errors when complete

```

### Final Verification

```bash

# Python linting
flake8 . --exclude=venv --count

# Markdown check
find . -name "*.md" -not -path "./venv/*" -exec grep -l $'\t' {} \;

# Should return no output for both

```

## 🎯 Success Criteria

### ✅ **COMPLETE SUCCESS:**

- **0 flake8 errors** in Python files

- **0 hard tabs** in markdown files

- **0 trailing whitespace** in markdown files

- **Proper heading spacing** in markdown files (MD022)

- **Proper list spacing** in markdown files (MD032)

- **Proper ordered list prefixes** in markdown files (MD029)

- **All code remains functional** (no logic changes)

- **Consistent code style** across all files

### 📊 **Expected Results:**

- **Before**: 18+ flake8 errors, hard tabs in markdown, missing heading spacing

- **After**: 0 flake8 errors, clean markdown formatting, proper heading spacing

- **Time**: 50-65 minutes total

## 🔧 Common Issues and Solutions

### Issue: Indentation Problems Persist

**Solution**: Use `black` auto-formatter

```bash
black src/components/problematic_file.py

```

### Issue: Hard Tabs in Markdown

**Solution**: Replace with spaces

```bash
sed -i '' 's/\t/    /g' filename.md

```

### Issue: Missing Heading Spacing (MD022)

**Solution**: Add blank lines before headings

```bash

# Add blank lines before all heading levels
sed -i '' 's/^##/\n##/g' *.md prompts/*.md
sed -i '' 's/^###/\n###/g' *.md prompts/*.md
sed -i '' 's/^####/\n####/g' *.md prompts/*.md
sed -i '' 's/^#####/\n#####/g' *.md prompts/*.md
sed -i '' 's/^######/\n######/g' *.md prompts/*.md

```

### Issue: Line Length Still Too Long

**Solution**: Break at logical points

```python

# Break long strings
long_string = ("This is a very long string that needs "
              "to be broken into multiple lines")

# Break long function calls
result = some_function(
    param1,
    param2,
    param3
)

```

## 📝 Notes for Future Cleanups

1. **Start with flake8** - it catches the most critical issues

1. **Use black for complex indentation** - it's more reliable than manual fixes

1. **Check markdown files** - they often have tab/whitespace/heading spacing issues

1. **Verify after each phase** - don't wait until the end

1. **Preserve functionality** - only fix style, not logic

1. **Don't forget markdown linting** - MD010, MD022, MD031, MD012 are common issues

1. **Use zsh-compatible sed commands** - avoid quote issues in zsh shell

## 🚀 Quick Commands for Future Use

```bash

# Full cleanup in one go
source venv/bin/activate
pip install flake8 black
flake8 . --exclude=venv --count
black src/
sed -i '' 's/\t/    /g' *.md prompts/*.md
sed -i '' 's/[[:space:]]*$//' *.md prompts/*.md
sed -i '' 's/^##/\n##/g' *.md prompts/*.md
sed -i '' 's/^###/\n###/g' *.md prompts/*.md
sed -i '' 's/^####/\n####/g' *.md prompts/*.md
sed -i '' 's/^#####/\n#####/g' *.md prompts/*.md
sed -i '' 's/^######/\n######/g' *.md prompts/*.md
flake8 . --exclude=venv --count  # Should show 0

```

---

**This guide is based on real-world experience cleaning up the N2S TMMi Tracker codebase and should work for similar Python/Streamlit projects.**
