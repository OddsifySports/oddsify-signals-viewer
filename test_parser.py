#!/usr/bin/env python3
"""
Test script for Oddsify Signals Viewer
Verifies backend API and markdown parsing
"""

import sys
sys.path.insert(0, '/home/markusbot/oddsify-signals-viewer/backend')

from main import parse_markdown_signals
from pathlib import Path

def test_parser():
    """Test markdown parser with sample file"""
    
    sample_file = Path("/home/markusbot/oddsify-signals-viewer/uploads/test_sample.md")
    
    if not sample_file.exists():
        print("❌ Sample file not found")
        return False
    
    content = sample_file.read_text()
    
    try:
        result = parse_markdown_signals(content)
        
        print("="*60)
        print("PARSER TEST RESULTS")
        print("="*60)
        print(f"✅ Metadata extracted:")
        print(f"   Sport: {result['metadata'].get('sport')}")
        print(f"   N Signals: {result['metadata'].get('n_signals')}")
        print(f"   Model: {result['metadata'].get('model')}")
        print(f"   Fetch ID: {result['metadata'].get('fetch_id')}")
        print(f"   Generated: {result['metadata'].get('generated')}")
        print(f"\n✅ Signals parsed: {len(result['signals'])}")
        
        if result['signals']:
            first = result['signals'][0]
            print(f"\n✅ First signal:")
            print(f"   Bucket: {first.bucket}")
            print(f"   Market: {first.market}")
            print(f"   Player: {first.player}")
            print(f"   Team: {first.team}")
            print(f"   Edge: {first.edge}%")
            print(f"   EV: {first.ev}¢")
        
        # Verify we got all 59 signals
        if len(result['signals']) == 59:
            print(f"\n✅ ALL 59 SIGNALS PARSED CORRECTLY")
            return True
        else:
            print(f"\n⚠️  Expected 59 signals, got {len(result['signals'])}")
            return False
            
    except Exception as e:
        print(f"❌ Parser error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_parser()
    sys.exit(0 if success else 1)
