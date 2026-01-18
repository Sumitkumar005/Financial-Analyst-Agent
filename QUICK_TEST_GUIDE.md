# 🧪 Quick Test Guide: Interest Rate Risk Table

## 🎯 Test Your System with These Queries

Based on the **Interest Rate Risk** table from the screenshot, use these queries to verify your system works correctly.

---

## ✅ **START HERE: 3 Essential Tests**

### Test 1: Simple Extraction
**Query:**
```
What is the total value of cash equivalents and marketable debt securities as of December 31, 2024?
```

**Expected Answer:**
- **$84,667 million** (or similar format)
- Should cite the table

**✅ Pass if:** Number matches exactly

---

### Test 2: Table Reconstruction
**Query:**
```
Show me the interest rate risk table with all security types, their total values, and weighted average interest rates.
```

**Expected Answer:**
A properly formatted table showing:
- Money market funds: $28,282M at 4.42%
- Corporate debt securities: $51,139M at 4.60%
- U.S. government and agency securities: $3,457M at 3.51%
- Asset-backed securities: $1,541M at 3.92%
- Foreign government and agency securities: $180M at 4.48%
- Other debt securities: $68M at 2.13%
- **Total: $84,667M**

**✅ Pass if:** 
- Table is properly formatted
- All 6 security types are listed
- Numbers match exactly
- Table renders correctly in frontend

---

### Test 3: Comparison & Calculation
**Query:**
```
Which security type has the highest total value in the interest rate risk table, and what is its weighted average interest rate?
```

**Expected Answer:**
- **Corporate debt securities** with **$51,139 million** at **4.60%**
- Should explain why (highest value)

**✅ Pass if:** 
- Correctly identifies corporate debt
- Numbers are accurate
- Shows reasoning

---

## 🔍 **ADVANCED TESTS** (If Basic Tests Pass)

### Test 4: Time-Based Analysis
**Query:**
```
How much corporate debt securities mature in 2025, and what is the weighted average interest rate?
```

**Expected Answer:**
- **$47,908 million** at **4.65%**

### Test 5: Percentage Calculation
**Query:**
```
What percentage of total cash equivalents and marketable debt securities mature in 2025?
```

**Expected Answer:**
- $78,821M out of $84,667M = **~93.1%**

### Test 6: Multi-Column Extraction
**Query:**
```
Break down the interest rate risk table showing money market funds and corporate debt securities across all maturity years (2025-2029 and thereafter).
```

**Expected Answer:**
A table showing both security types with values for:
- 2025, 2026, 2027, 2028, 2029, Thereafter, Total

---

## 📋 **Verification Checklist**

After running each query, check:

### ✅ **Accuracy**
- [ ] Numbers match the screenshot exactly
- [ ] Units are correct (millions, percentages)
- [ ] No made-up numbers (hallucinations)

### ✅ **Table Formatting**
- [ ] Tables render properly in frontend
- [ ] Markdown table syntax is correct
- [ ] All columns and rows are present

### ✅ **Understanding**
- [ ] System understands "security types" = rows
- [ ] System understands "maturity years" = columns
- [ ] System can extract specific cells
- [ ] System can perform calculations

### ✅ **Response Quality**
- [ ] Clear and structured
- [ ] Source attribution present
- [ ] No errors or missing data

---

## 🚨 **Red Flags** (If You See These, System Needs Fixing)

❌ **Wrong Numbers**: Different values than in screenshot  
❌ **Missing Data**: Incomplete table  
❌ **Broken Tables**: Tables not rendering  
❌ **Hallucinations**: Numbers that don't exist  
❌ **No Source**: Missing file attribution  
❌ **Calculation Errors**: Wrong percentages or differences  

---

## 💡 **Pro Tips**

1. **Start with Test 1** - Simplest, verifies basic extraction
2. **Then Test 2** - Verifies table structure preservation
3. **Finally Test 3** - Verifies reasoning ability
4. **Compare Results** - Check against the screenshot
5. **Test Edge Cases** - Try unusual queries

---

## 🎯 **Success Criteria**

Your system is working correctly if:

✅ **Test 1 Passes**: Can extract exact values  
✅ **Test 2 Passes**: Can reconstruct full table  
✅ **Test 3 Passes**: Can compare and reason  
✅ **No Hallucinations**: All numbers are accurate  
✅ **Tables Render**: Proper formatting in frontend  

---

## 📊 **Expected Table Format in Response**

The system should return something like:

```markdown
| Security Type | Total Value | Weighted Avg Rate |
|--------------|-------------|-------------------|
| Money market funds | $28,282M | 4.42% |
| Corporate debt securities | $51,139M | 4.60% |
| U.S. government and agency securities | $3,457M | 3.51% |
| Asset-backed securities | $1,541M | 3.92% |
| Foreign government and agency securities | $180M | 4.48% |
| Other debt securities | $68M | 2.13% |
| **Total** | **$84,667M** | - |
```

---

## 🔧 **If Tests Fail**

1. **Check File Loading**: Verify the MD file contains the table
2. **Check Table Format**: Verify Markdown conversion preserved tables
3. **Check Prompt**: Verify Gemini prompt emphasizes tables
4. **Check Frontend**: Verify `remark-gfm` is installed
5. **Check Logs**: Look at server console for errors

---

## 🚀 **Ready to Test?**

1. Open your frontend
2. Go to "Analyze" tab
3. Start with **Test 1** query
4. Compare results with screenshot
5. Move to Test 2, then Test 3

**Good luck!** 🎉
