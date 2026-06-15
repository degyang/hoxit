---
title: "PR-SKILL-004 Implementation Report"
pr: "PR-SKILL-004"
skill: "lhb-analyzer"
status: "IMPLEMENTED"
date: "2026-06-14"
---

# PR-SKILL-004: UZEN LHB Analyzer Protocol

## Summary

Implemented comprehensive UZEN LHB Analyzer protocol documentation, providing detailed guidance for analyzing Dragon and Tiger List (龙虎榜) data with proper institution vs hot-money seat classification and buy/sell seat interpretation.

## Deliverables

### 1. `uzen-skills/skills/lhb-analyzer/SKILL.md` (192 lines)

Complete protocol covering:
- **Input Requirements**: code, trade_date, lhb_data, peer_data, board_data
- **Hoxit LHB Data Boundary**: Clear separation between available hoxit data and deferred APIs
- **Target Seat Schema**: Standardized schema for seat analysis with all required fields
- **Institution vs Hot-Money Classification**: Classification logic with confidence scoring
- **Buy/Sell Seat Interpretation**: Detailed interpretation rules for buy and sell seat patterns
- **Board and Peer Leadership Comparison**: Comparison logic for identifying leadership patterns
- **Fallback Strategy**: Graceful degradation when partial data is available
- **Deferred APIs**: Clear documentation of future enhancements (seat database, peer ranking, historical patterns)

### 2. `uzen-skills/commands/lhb-analyzer.md` (69 lines)

Command documentation including:
- Command syntax and parameters
- Input/output specifications
- Usage examples
- Integration with UZEN workflow

## Verification

- [x] No whitespace errors (`git diff --check`)
- [x] All files properly formatted
- [x] Consistent with existing UZEN skill documentation patterns
- [x] Clear separation between available data and deferred features
- [x] Comprehensive seat classification logic documented
- [x] Buy/sell interpretation rules complete

## Technical Details

### Seat Classification Logic

The protocol defines a clear classification system:
- **Institution Seats**: Funds, insurance, QFII, social security, etc.
- **Hot-Money Seats**: Known游资 (youzi) seats with historical patterns
- **Confidence Scoring**: 0-100 scale based on seat name pattern matching

### Buy/Sell Interpretation

Detailed rules for interpreting:
- Buy-side concentration (单席位买入占比)
- Sell-side distribution (多席位分散卖出)
- Net buy/sell patterns (买卖净额)
- Seat turnover patterns (席位换手率)

### Data Boundary

Clear separation between:
- **Available via hoxit**: Basic LHB data, seat names, buy/sell amounts
- **Deferred**: Historical seat patterns, peer ranking, social sentiment

## Integration

This protocol integrates with:
- UZEN Deep Analysis workflow
- Hoxit signals module (`signals.py`)
- Future seat database enhancements

## Status

**IMPLEMENTED** - Ready for Codex review.

All deliverables complete. Protocol documentation follows established UZEN skill patterns and provides comprehensive guidance for LHB analysis within the hoxit ecosystem.
