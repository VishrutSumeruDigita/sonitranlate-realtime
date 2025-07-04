#!/usr/bin/env python3
"""
Test script to verify the None comparison fix.
"""

def test_sorting_with_none():
    """Test sorting with None values."""
    print("🧪 Testing sorting with None values...")
    
    # Simulate format data with None values
    formats = [
        {'abr': None, 'tbr': None, 'url': 'url1'},
        {'abr': 128, 'tbr': None, 'url': 'url2'},
        {'abr': None, 'tbr': 256, 'url': 'url3'},
        {'abr': 64, 'tbr': 128, 'url': 'url4'},
        {'abr': None, 'tbr': None, 'url': 'url5'},
    ]
    
    print("Original formats:")
    for i, fmt in enumerate(formats):
        print(f"  {i}: abr={fmt['abr']}, tbr={fmt['tbr']}, url={fmt['url']}")
    
    # Test the fixed sorting logic
    try:
        formats.sort(key=lambda x: (x.get('abr') or 0) + (x.get('tbr') or 0), reverse=True)
        print("\nSorted formats (fixed logic):")
        for i, fmt in enumerate(formats):
            print(f"  {i}: abr={fmt['abr']}, tbr={fmt['tbr']}, url={fmt['url']}")
        print("✅ Sorting with None values works!")
        
    except Exception as e:
        print(f"❌ Sorting failed: {e}")
        return False
    
    return True

def test_old_sorting_logic():
    """Test the old sorting logic that would fail."""
    print("\n🧪 Testing old sorting logic (should fail)...")
    
    formats = [
        {'abr': None, 'tbr': None, 'url': 'url1'},
        {'abr': 128, 'tbr': None, 'url': 'url2'},
    ]
    
    try:
        # This is the old logic that would fail
        formats.sort(key=lambda x: x.get('abr', 0) or x.get('tbr', 0), reverse=True)
        print("❌ Old logic didn't fail as expected")
        return False
    except TypeError as e:
        print(f"✅ Old logic correctly failed with: {e}")
        return True

def main():
    """Run all tests."""
    print("🧪 Testing None Comparison Fix")
    print("=" * 40)
    
    success1 = test_sorting_with_none()
    success2 = test_old_sorting_logic()
    
    if success1 and success2:
        print("\n✅ All tests passed! The fix should work.")
    else:
        print("\n❌ Some tests failed.")

if __name__ == "__main__":
    main() 