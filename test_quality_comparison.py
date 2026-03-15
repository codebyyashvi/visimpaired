#!/usr/bin/env python3
"""Comprehensive quality comparison of NEW SMART SHARPENING methods"""

import sys
sys.path.insert(0, 'scripts')

import cv2
import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt
from image_enhancement import ImageEnhancer
from PIL import Image

# Load test image
test_image_path = 'Dataset/Vizwiz-Data/test/VizWiz_test_00000001.jpg'
original = cv2.imread(test_image_path)

print("="*70)
print("TESTING NEW SMART SHARPENING ENHANCEMENT METHODS")
print("="*70)

# Load quality assessment model
print("\nLoading MobileNetV2 quality assessment model...")
IMG_SIZE = 448
CHANNELS = 3

def build_model_mobilenet():
    base_model = tf.keras.applications.MobileNetV2(
        input_shape=(IMG_SIZE, IMG_SIZE, CHANNELS),
        include_top=False,
        weights='imagenet'
    )
    base_model.trainable = False

    input_layer = tf.keras.layers.Input(shape=(IMG_SIZE, IMG_SIZE, CHANNELS))
    x = base_model(input_layer, training=False)
    x = tf.keras.layers.GlobalAveragePooling2D()(x)
    x = tf.keras.layers.Dropout(0.2)(x)
    x = tf.keras.layers.Dense(512, activation='relu', name='hidden_layer1')(x)
    x = tf.keras.layers.Dropout(0.2)(x)

    x1 = tf.keras.layers.Dense(32, activation='relu', name='hidden_layer2')(x)
    x1 = tf.keras.layers.Dropout(0.2)(x1)
    output_2 = tf.keras.layers.Dense(1, name='output_2')(x1)

    x2 = tf.keras.layers.Dense(32, activation='relu', name='hidden_layer3')(x)
    x2 = tf.keras.layers.Dropout(0.2)(x2)
    output_1 = tf.keras.layers.Dense(7, name='output_1')(x2)

    return tf.keras.models.Model(inputs=input_layer, outputs=[output_1, output_2])

test_model = build_model_mobilenet()
test_model.load_weights('Notebooks/test_models/mobilenet.h5')

def assess_quality(image_path):
    """Assess image quality using the model"""
    im = Image.open(image_path)
    im = im.resize((IMG_SIZE, IMG_SIZE), Image.LANCZOS)
    image_array = np.array(im).astype(np.float32) / 255.0
    
    pred = test_model.predict(np.array([image_array]), verbose=0)
    distortion_dist = pred[0][0]  # Distribution over 7 distortion types
    quality_score = float(pred[1][0][0])  # Quality score
    
    return quality_score, distortion_dist

def save_and_assess(image_path, method_name):
    """Save image temporarily and assess quality"""
    quality, dist = assess_quality(image_path)
    return quality

# Assess original
print("Assessing original image...")
original_path = 'original_temp.jpg'
cv2.imwrite(original_path, original)
original_quality, original_dist = assess_quality(original_path)

print(f"\n[OK] Original image quality: {original_quality:.4f}")
print(f"  Distortion signature: {[f'{d:.4f}' for d in original_dist]}")

# Create enhancer
enhancer = ImageEnhancer()

# Test methods
methods = ['bilateral', 'aggressive', 'combined', 'morphological']
results = {}

print("\n" + "="*70)
print("TESTING ENHANCEMENT METHODS:")
print("="*70)

for method in methods:
    print(f"\n[*] Testing {method.upper()}...", end=" ")
    
    enhanced, metadata = enhancer.enhance(original, method=method)
    
    # Save to temp file and assess
    temp_path = f'{method}_temp.jpg'
    cv2.imwrite(temp_path, enhanced)
    quality, dist = assess_quality(temp_path)
    
    improvement = quality - original_quality
    percent_change = (improvement / original_quality * 100) if original_quality != 0 else 0
    
    results[method] = {
        'quality': quality,
        'improvement': improvement,
        'percent_change': percent_change,
        'dist': dist
    }
    
    status = "[BETTER]" if improvement > 0 else "[WORSE]" if improvement < 0 else "[SAME]"
    print(f"{status}")
    print(f"   Quality: {quality:.4f} (Δ {improvement:+.4f}, {percent_change:+.2f}%)")

# Print comprehensive results
print("\n" + "="*70)
print("COMPREHENSIVE RESULTS SUMMARY:")
print("="*70)

print(f"\n{'Method':<15} {'Quality':<12} {'Improvement':<15} {'Change %':<12} {'Status':<15}")
print("-"*70)

best_method = None
best_improvement = -float('inf')

for method in methods:
    res = results[method]
    improvement = res['improvement']
    if improvement > best_improvement:
        best_improvement = improvement
        best_method = method
    
    status = "[BETTER]" if improvement > 0 else "[WORSE]" if improvement < 0 else "[SAME]"
    print(f"{method:<15} {res['quality']:<12.4f} {improvement:+.4f}{'':10} {res['percent_change']:+.2f}% {status:<15}")

print("-"*70)
print(f"\n{'ORIGINAL':<15} {original_quality:<12.4f}")

# Recommendations
print("\n" + "="*70)
print("RECOMMENDATIONS:")
print("="*70)

if best_improvement > 0.01:
    print(f"\n[BEST] METHOD: {best_method.upper()}")
    print(f"   Quality improvement: +{best_improvement:.4f} ({results[best_method]['percent_change']:+.2f}%)")
    print(f"   This method successfully reduces blur without over-smoothing!")
elif max(res['improvement'] for res in results.values()) >= 0:
    print(f"\n[OK] Some methods show improvements, consider:")
    for method in methods:
        if results[method]['improvement'] > 0:
            print(f"   - {method.upper()}: +{results[method]['improvement']:.4f}")
else:
    print(f"\n[WARN] All methods show degradation - indicates special handling needed")
    print(f"    Dataset may need: Super-resolution, different preprocessing, or hybrid approach")

print("\n" + "="*70)

# Cleanup
import os
for method in methods:
    try:
        os.remove(f'{method}_temp.jpg')
    except:
        pass
try:
    os.remove(original_path)
except:
    pass
