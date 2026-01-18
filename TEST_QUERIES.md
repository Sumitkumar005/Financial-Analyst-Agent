# Test Queries for Interest Rate Risk Table

## 🎯 Purpose
Test queries to verify your Table-Aware RAG system correctly understands and extracts data from complex financial tables like the "Interest Rate Risk" table shown in the screenshot.

---

## 📊 Table Context
The table shows:
- **Cash equivalents and marketable debt securities**
- **By type**: Money market funds, Corporate debt, U.S. government, Asset-backed, Foreign government, Other
- **By maturity**: 2025, 2026, 2027, 2028, 2029, Thereafter, Total
- **Data points**: Monetary values ($) and weighted-average interest rates (%)

---

## ✅ Test Queries (Start Simple → Complex)

### Level 1: Simple Extraction
**Test if system can find basic table data**

1. **"What is the total value of cash equivalents and marketable debt securities as of December 31, 2024?"**
   - Expected: ~$84,667 million
   - Tests: Basic table lookup

2. **"What is the weighted average interest rate for money market funds?"**
   - Expected: 4.42%
   - Tests: Specific cell extraction

### Level 2: Comparison
**Test if system can compare rows/columns**

3. **"Which security type has the highest total value: corporate debt securities or money market funds?"**
   - Expected: Corporate debt securities ($51,139M vs $28,282M)
   - Tests: Multi-row comparison

4. **"What is the difference between corporate debt securities and money market funds in 2025?"**
   - Expected: Corporate debt: $47,908M, Money market: $28,282M, Difference: ~$19,626M
   - Tests: Calculation ability

### Level 3: Time Series Analysis
**Test understanding of maturity dates**

5. **"How much corporate debt securities mature in 2025 compared to 2029?"**
   - Expected: 2025: $47,908M, 2029: $55M
   - Tests: Time-based extraction

6. **"What percentage of total securities mature in 2025?"**
   - Expected: $78,821M out of $84,667M = ~93%
   - Tests: Percentage calculation

### Level 4: Complex Analysis
**Test deep understanding and reasoning**

7. **"Break down the interest rate risk table showing all security types, their 2025 values, and weighted average interest rates."**
   - Expected: Complete table with all 6 security types
   - Tests: Full table reconstruction

8. **"What is the weighted average interest rate for all cash equivalents and marketable debt securities combined?"**
   - Expected: Need to calculate from individual rates
   - Tests: Weighted average calculation

9. **"Which year has the highest concentration of maturities, and what is the total value?"**
   - Expected: 2025 with $78,821M
   - Tests: Maximum value identification

### Level 5: Cross-Table Analysis
**Test if system can relate to other sections**

10. **"Based on the interest rate risk table, what is the company's exposure to interest rate changes in the next 2 years?"**
    - Expected: Analysis of 2025-2026 maturities
    - Tests: Risk analysis capability

11. **"Compare the interest rates of U.S. government securities versus corporate debt securities."**
    - Expected: U.S. gov: 3.51%, Corporate: 4.60%
    - Tests: Cross-category comparison

---

## 🔍 Verification Checklist

After running queries, verify:

### ✅ Accuracy Checks:
- [ ] Numbers match the table exactly
- [ ] Units are correct (millions, percentages)
- [ ] Table structure is preserved in response
- [ ] All requested data points are included

### ✅ Table Understanding:
- [ ] System understands row headers (security types)
- [ ] System understands column headers (years)
- [ ] System can extract specific cells
- [ ] System can perform calculations

### ✅ Response Quality:
- [ ] Tables are formatted correctly
- [ ] Data is presented clearly
- [ ] No hallucinations (made-up numbers)
- [ ] Source attribution is present

---

## 🎯 Recommended Test Sequence

**Start with these 3 queries to quickly verify:**

1. **"What is the total value of cash equivalents and marketable debt securities?"**
   - Quick accuracy test

2. **"Show me the interest rate risk table with all security types and their 2025 values."**
   - Table reconstruction test

3. **"Which security type has the highest total value and what is its weighted average interest rate?"**
   - Complex reasoning test

---

## 📝 Expected Response Format

A good response should include:

```
✅ **Table Structure**: Properly formatted markdown table
✅ **Accurate Numbers**: Exact values from the document
✅ **Clear Labels**: Security types, years, units
✅ **Source**: Attribution to the document
✅ **Context**: Brief explanation if needed
```

---

## 🚨 Red Flags (If You See These, System Needs Fixing)

❌ **Wrong Numbers**: Different values than in table  
❌ **Missing Data**: Incomplete table in response  
❌ **Broken Tables**: Tables not rendering properly  
❌ **Hallucinations**: Numbers that don't exist  
❌ **No Source**: Missing file attribution  

---

## 💡 Pro Tips

1. **Start Simple**: Begin with basic extraction queries
2. **Build Complexity**: Gradually test more complex queries
3. **Compare Results**: Check against the original document
4. **Test Edge Cases**: Try unusual queries
5. **Verify Calculations**: Test if system can do math correctly

---

## 🎯 Success Criteria

Your system is working correctly if:
- ✅ Can extract exact table values
- ✅ Can compare different rows/columns
- ✅ Can perform calculations
- ✅ Preserves table structure in response
- ✅ No hallucinations
- ✅ Clear source attribution

Good luck testing! 🚀
