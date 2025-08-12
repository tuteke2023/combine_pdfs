#!/usr/bin/env python3
"""Quick test to verify the redaction logic"""

import re

def detect_abn(text):
    """Test version of ABN detection"""
    abn_patterns = [
        r'\b\d{2}\s+\d{3}\s+\d{3}\s+\d{3}\b',  # XX XXX XXX XXX (with spaces)
        r'\b\d{2}[\s-]?\d{3}[\s-]?\d{3}[\s-]?\d{3}\b',  # XX XXX XXX XXX or XX-XXX-XXX-XXX
        r'\b\d{11}\b',  # XXXXXXXXXXX
    ]
    
    found_items = []
    seen_positions = set()
    
    for pattern in abn_patterns:
        matches = re.finditer(pattern, text)
        for match in matches:
            digits = re.sub(r'\D', '', match.group())
            if len(digits) == 11:
                if match.start() not in seen_positions:
                    found_items.append({
                        'type': 'ABN',
                        'text': match.group(),
                        'start': match.start(),
                        'end': match.end(),
                        'digits': digits
                    })
                    seen_positions.add(match.start())
    
    return found_items

def detect_tfn(text, abn_positions=None):
    """Test version of TFN detection"""
    tfn_patterns = [
        r'(?<!\d)\d{3}[\s-]?\d{3}[\s-]?\d{3}(?!\d)',  # XXX XXX XXX or XXX-XXX-XXX (not part of longer number)
        r'(?<!\d)\d{9}(?!\d)',  # XXXXXXXXX (not part of longer number)
    ]
    
    found_items = []
    seen_positions = set()
    
    for pattern in tfn_patterns:
        matches = re.finditer(pattern, text)
        for match in matches:
            digits = re.sub(r'\D', '', match.group())
            if len(digits) == 9 and match.start() not in seen_positions:
                # Check if this TFN is part of an ABN
                is_part_of_abn = False
                if abn_positions:
                    for abn_start, abn_end in abn_positions:
                        if (match.start() >= abn_start and match.start() < abn_end) or \
                           (match.end() > abn_start and match.end() <= abn_end):
                            is_part_of_abn = True
                            break
                
                if not is_part_of_abn:
                    # Additional check for 2 digits before
                    before_text = text[max(0, match.start()-10):match.start()]
                    if re.search(r'\d{2}[\s-]?$', before_text):
                        continue
                    
                    found_items.append({
                        'type': 'TFN',
                        'text': match.group(),
                        'start': match.start(),
                        'end': match.end(),
                        'digits': digits
                    })
                    seen_positions.add(match.start())
    
    return found_items

# Test cases
test_cases = [
    ("ABN: 65 762 770 637", "ABN with spaces"),
    ("TFN: 123 456 789", "TFN with spaces"),
    ("Company ABN 65762770637 and TFN 987654321", "Mixed compact format"),
    ("ABN: 12-345-678-901", "ABN with dashes"),
    ("Just numbers: 762 770 637", "9 digits alone (should be TFN)"),
]

print("Testing detection logic:\n")
for text, description in test_cases:
    print(f"Test: {description}")
    print(f"Text: '{text}'")
    
    # Detect ABNs first
    abns = detect_abn(text)
    abn_positions = [(item['start'], item['end']) for item in abns]
    
    # Detect TFNs with ABN positions
    tfns = detect_tfn(text, abn_positions)
    
    print(f"  ABNs found: {len(abns)}")
    for abn in abns:
        print(f"    - '{abn['text']}' at positions {abn['start']}-{abn['end']}")
    
    print(f"  TFNs found: {len(tfns)}")
    for tfn in tfns:
        print(f"    - '{tfn['text']}' at positions {tfn['start']}-{tfn['end']}")
    print()

print("\nKey verification:")
print("✓ ABN '65 762 770 637' should be detected as ABN only")
print("✓ '762 770 637' alone should be detected as TFN")
print("✓ TFN detection should skip 9-digit sequences within ABNs")