# Claude Code Cost Optimization Guide

**Current Situation**: $100+/day → **Target**: $20-40/day (60-80% savings)

---

## Quick Wins (Implement Today)

### 1. Use `/clear` After Each Feature
```bash
# After completing any distinct task:
/clear

# This prevents context bloat and resets token count to 0
```

**When to clear:**
- ✅ After completing a feature
- ✅ After fixing a bug
- ✅ Before starting unrelated work
- ✅ When approaching 100K tokens

**Impact**: 50-70% cost reduction

---

### 2. Session Management Strategy

**Bad Pattern (Current):**
```
Session 1: 200K tokens (all day work)
Cost: $100+/day
```

**Good Pattern (Target):**
```
Session 1: Feature A (40K tokens) → /clear
Session 2: Feature B (40K tokens) → /clear
Session 3: Feature C (40K tokens) → /clear
Session 4: Bug fixes (40K tokens) → /clear
Total: 160K tokens/day
Cost: $20-30/day
```

**Rule of Thumb:**
- Keep sessions under 50K tokens
- Use 3-4 focused sessions per day instead of 1 mega-session
- `/clear` between unrelated work

---

### 3. Use Task Tool with Haiku for Simple Operations

**Cost Comparison:**
- Sonnet: $3/MTok input, $15/MTok output
- **Haiku: $0.25/MTok input, $1.25/MTok output** (12x cheaper!)

**Use Haiku for:**
```typescript
// Simple file searches (90% cheaper)
/explore "Find all files with TypeScript errors"
// Uses Task tool with haiku automatically

// Simple test runs
"Run tests for color extractor using haiku model"

// Code reviews of small changes
"Review this 50-line change using haiku"
```

**Use Sonnet for:**
- Complex architectural decisions
- Large refactors
- Multi-file coordinated changes

**Impact**: 80-90% cost reduction on simple tasks

---

### 4. Optimize File Reading

**Bad (Expensive):**
```typescript
// ❌ Reading entire large files
"Show me the color extractor"
// Reads entire 5000+ line file

// ❌ Reading multiple files
"Read file1, file2, file3, file4, file5"
// 50K+ tokens in one request
```

**Good (Efficient):**
```typescript
// ✅ Targeted searches
"Find the ColorExtractor class definition"
// Uses Grep - returns only matching lines

// ✅ Specific line ranges
"Show me lines 100-150 of color_extractor.py"
// Minimal token usage

// ✅ Progressive exploration
"Find files with 'export' → Then read the main one"
// Search first, read second
```

**Impact**: 70-90% reduction in file reading costs

---

### 5. Concise Command Outputs

**Bad:**
```bash
# ❌ Verbose test output
pytest -vvv
# 100K+ tokens of detailed output

# ❌ Full git logs
git log --all
# Thousands of commits
```

**Good:**
```bash
# ✅ Quiet test output
pytest -q
# Shows only summary

# ✅ Limited git logs
git log --oneline -10
# Last 10 commits only

# ✅ Grep with file names only
grep "pattern" --files-with-matches
# Just file names, not content
```

**Impact**: 80% reduction in command output tokens

---

### 6. Batch Similar Operations

**Bad:**
```typescript
// ❌ Sequential operations (each adds context)
"Fix import in file1.py"
"Fix import in file2.py"
"Fix import in file3.py"
// 3 separate context-heavy operations
```

**Good:**
```typescript
// ✅ Single batched operation
"Fix imports in these files: file1.py, file2.py, file3.py"
// One operation, much cheaper
```

**Impact**: 60-70% reduction for repetitive tasks

---

## Cost Monitoring

### Track Token Usage
Each response shows:
```
Token usage: 114179/200000 (57% used)
```

**Red Flags:**
- 🚨 >100K tokens in one session
- 🚨 >60K tokens before lunch
- 🚨 Reading same files repeatedly
- 🚨 Verbose bash outputs

**Action When Hitting 80K:**
```bash
# Stop and clear
/clear

# Start fresh session for remaining work
```

---

## Monthly Cost Projections

### Current Pattern
```
$100/day × 22 working days = $2,200/month
```

### Optimized Pattern
```
Session 1 (Morning): 40K tokens
Session 2 (Afternoon): 40K tokens
Session 3 (End of day): 30K tokens
Total: 110K tokens/day

110K tokens × $3/MTok = $0.33/day input
110K tokens × $15/MTok × 0.3 = $0.50/day output (30% output ratio)
Total: ~$0.83/day

With overhead and variations: $20-30/day
$25/day × 22 working days = $550/month

Savings: $1,650/month (75% reduction)
```

---

## Implementation Checklist

### Today
- [ ] Install `/clear` habit after each feature
- [ ] Set personal rule: Clear at 50K tokens
- [ ] Use "quiet" flags for pytest (`-q`)
- [ ] Start using Grep before Read

### This Week
- [ ] Break work into 3-4 focused sessions daily
- [ ] Use Task tool with haiku for simple operations
- [ ] Batch similar file operations
- [ ] Monitor token usage actively

### This Month
- [ ] Review cost reports weekly
- [ ] Refine session boundaries
- [ ] Identify and eliminate token waste patterns
- [ ] Achieve target: $20-40/day

---

## Quick Reference Card

```
┌─────────────────────────────────────────────┐
│  COST OPTIMIZATION QUICK REFERENCE          │
├─────────────────────────────────────────────┤
│  Before Each Feature:                       │
│    Check token usage (<50K? continue)       │
│                                             │
│  After Each Feature:                        │
│    /clear                                   │
│                                             │
│  Simple Tasks:                              │
│    "do X using haiku"                       │
│                                             │
│  File Reading:                              │
│    Grep first → Read specific lines         │
│                                             │
│  Test Running:                              │
│    pytest -q (not -vvv)                     │
│                                             │
│  Token Alert:                               │
│    >80K tokens → /clear now                 │
└─────────────────────────────────────────────┘
```

---

## Support

If costs remain high after implementing these strategies:
1. Check for background processes
2. Review session patterns in billing
3. Consider dedicated "research" vs "implementation" sessions
4. Use `/help` for additional optimization tips

**Target Achieved**: $2,200/month → $550/month = **$1,650 monthly savings**
