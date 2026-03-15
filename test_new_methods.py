#!/usr/bin/env python3
"""Quick test of new SMART sharpening methods"""

import sys
sys.path.insert(0, 'scripts')

import cv2
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
from image_enhancement import ImageEnhancer

# Load test image
test_image_path = 'Dataset/Vizwiz-Data/test/VizWiz_test_00000001.jpg'
original = cv2.imread(test_image_path)
original_rgb = cv2.cvtColor(original, cv2.COLOR_BGR2RGB)

# Create enhancer
enhancer = ImageEnhancer()

# Test the new smart methods
methods = ['bilateral', 'aggressive', 'combined', 'morphological']

fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle('NEW SMART SHARPENING Methods (vs Original)', fontsize=16, fontweight='bold')

for idx, method in enumerate(methods):
    enhanced, metadata = enhancer.enhance(original, method=method)
    enhanced_rgb = cv2.cvtColor(enhanced, cv2.COLOR_BGR2RGB)
    
    ax = axes[idx // 2, idx % 2]
    ax.imshow(enhanced_rgb)
    ax.set_title(f'{method.upper()} - Smart Sharpening-First', fontweight='bold')
    ax.axis('off')
    
    print(f"✓ {method.upper()} enhancement applied successfully")

plt.tight_layout()
plt.savefig('test_results_smart_methods.png', dpi=100, bbox_inches='tight')
print("\n✓ Visualization saved to test_results_smart_methods.png")
print("\nNEW METHODS COMPARISON:")
print("=" * 60)
print("BILATERAL:    Single-pass bilateral (7, 50, 50) + Strong unsharp mask")
print("AGGRESSIVE:   Minimal bilateral + Unsharp masking + Moderate CLAHE")
print("COMBINED:     Light bilateral + Unsharp masking + Edge enhancement")
print("MORPHOLOGICAL: Gradient enhancement only (baseline)")
print("=" * 60)
print("\n🎯 EXPECTED IMPROVEMENT: Less blur, better details, no over-smoothing!")
