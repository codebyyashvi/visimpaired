# Image Denoising & Enhancement Guide

This guide explains the image denoising and enhancement system integrated into your VISimpaired project.

## Overview

The enhancement system provides **5 different denoising and enhancement methods** combined with your quality assessment model to:
1. **Assess** the original image's quality and identify distortions
2. **Enhance** the image using various techniques
3. **Compare** before/after quality improvements

## Enhancement Methods Explained

### 1. **Bilateral Filter** (`'bilateral'`)
- **What it does**: Reduces noise while preserving sharp edges
- **Best for**: 
  - General-purpose denoising
  - Images with moderate noise
  - Edge preservation is critical
- **Speed**: ⚡⚡⚡ Fast
- **Quality**: ⭐⭐⭐ Good

**How it works**: Applies weighted averaging based on both spatial distance and intensity difference. Pixels with similar intensity are smoothed together while edges remain sharp.

```python
results = assess_and_enhance_image(image_path, method='bilateral')
```

---

### 2. **Non-Local Means (NLM)** (`'nlm'`)
- **What it does**: Advanced statistical denoising by comparing image patches
- **Best for**:
  - Heavy noise (Gaussian, Poisson)
  - Fine texture preservation
  - High-quality results required
- **Speed**: ⚡ Slow (but thorough)
- **Quality**: ⭐⭐⭐⭐⭐ Excellent

**How it works**: Searches for similar patches throughout the image and averages them. Preserves textures and fine details better than simpler methods.

```python
results = assess_and_enhance_image(image_path, method='nlm')
```

---

### 3. **Morphological Enhancement** (`'morphological'`)
- **What it does**: Sharpens edges and enhances image structure
- **Best for**:
  - Blurry images
  - Low contrast
  - Enhancing edges and details
- **Speed**: ⚡⚡ Medium
- **Quality**: ⭐⭐⭐ Good for edges

**How it works**: Uses morphological operations (closing, opening, gradient) to remove noise and enhance edge information.

```python
results = assess_and_enhance_image(image_path, method='morphological')
```

---

### 4. **Adaptive Denoising** (`'adaptive'`)
- **What it does**: Removes salt-and-pepper noise and structured artifacts
- **Best for**:
  - Compression artifacts
  - Salt-and-pepper noise
  - Structured noise patterns
- **Speed**: ⚡⚡ Medium
- **Quality**: ⭐⭐⭐ Good for artifacts

**How it works**: Combines morphological closing and opening to remove small noise while preserving larger structures.

```python
results = assess_and_enhance_image(image_path, method='adaptive')
```

---

### 5. **Combined Enhancement** (`'combined'`) - **RECOMMENDED**
- **What it does**: Multi-step pipeline combining multiple techniques
- **Best for**: 
  - General-purpose use
  - Unknown noise types
  - Best overall visual quality
- **Speed**: ⚡⚡ Medium
- **Quality**: ⭐⭐⭐⭐⭐ Best overall

**Steps in pipeline**:
1. **Bilateral filtering** → Reduces noise
2. **CLAHE** (Contrast Limited Adaptive Histogram Equalization) → Improves contrast
3. **Unsharp masking** → Sharpens details

```python
results = assess_and_enhance_image(image_path, method='combined')
```

---

## Usage Examples

### Basic Single Image Enhancement

```python
# Load model and image
quality_model = build_model_mobilenet()
quality_model.load_weights('test_models/mobilenet.h5')

# Enhance and assess
results = assess_and_enhance_image(
    'path/to/image.jpg',
    enhancement_method='combined'
)

# Visualize results
visualize_results(results)
```

**Results dictionary contains**:
- `original_image`: Original image array
- `enhanced_image`: Enhanced image array
- `original_quality_score`: Quality metric of original
- `enhanced_quality_score`: Quality metric after enhancement
- `quality_improvement`: Difference in scores
- `original_distortions`: Detected issues in original
- `enhanced_distortions`: Detected issues after enhancement

---

### Batch Processing Multiple Images

```python
batch_results = process_image_batch(
    image_folder='../Dataset/Vizwiz-Data/test/',
    enhancement_method='combined',
    output_folder='./enhanced_images',
    max_images=10
)

# batch_results is a list of improvements for each image
```

**Output**:
- Enhanced images saved to `output_folder`
- Returns list with quality scores before/after for each image

---

### Compare All Methods on One Image

```python
comparison_results = compare_enhancement_methods(
    'path/to/image.jpg'
)

# Displays visual comparison and quality metrics for all methods
```

---

## Interpreting Results

When you run `assess_and_enhance_image()`, you get:

### Quality Score
- **Range**: 0 to ~100 (higher is better)
- **Interpretation**: 
  - 70+ : Excellent quality
  - 50-70: Good quality  
  - 30-50: Fair quality
  - <30: Poor quality

### Distortion Types
The model identifies 7 distortion categories:
1. **Compression Artifacts** - JPEG/lossy compression effects
2. **Blur** - Motion or focus blur
3. **Noise** - Gaussian, salt-and-pepper noise
4. **Oversaturation** - Too much color intensity
5. **Underexposure** - Too dark
6. **Overexposure** - Too bright
7. **Other** - Miscellaneous distortions

### Quality Improvement
- **Positive value** (+X.XXXX) = Enhancement improved quality
- **Negative value** (-X.XXXX) = Enhancement reduced quality (rare)
- **Larger magnitude** = Stronger effect

---

## Choosing the Right Method

| Scenario | Recommended Method | Reason |
|----------|-------------------|--------|
| Don't know problem type | `'combined'` | Best all-around |
| Heavy noise (Gaussian) | `'nlm'` | Superior noise reduction |
| Blurry images | `'morphological'` | Sharpens edges |
| Compression artifacts | `'adaptive'` | Targets artifact patterns |
| Speed critical | `'bilateral'` | Fastest option |
| Comparing methods | Use `compare_enhancement_methods()` | Tests all at once |

---

## Advanced Usage

### Custom Enhancement Parameters

For more control, use `ImageEnhancer` class directly:

```python
from image_enhancement import ImageEnhancer

enhancer = ImageEnhancer()

# Bilateral with custom parameters
enhanced = enhancer.bilateral_denoise(
    image,
    diameter=15,      # Larger = more smoothing
    sigma_color=100,  # Higher = more color smoothing
    sigma_space=100   # Higher = larger spatial range
)

# Non-local means with custom parameters
enhanced = enhancer.non_local_means_denoise(
    image,
    h=15,                    # Denoising strength (higher = more denoising)
    template_window_size=7,  # Template patch size
    search_window_size=21    # Search area size
)
```

### Save Enhanced Images

```python
from image_enhancement import save_enhanced_image

save_enhanced_image(
    enhanced_image,
    output_path='./results/enhanced_image.jpg',
    original_range='normalized'  # If image was 0-1 range
)
```

---

## Tips for Best Results

1. **For noisy images**: Use `'nlm'` or `'combined'` for best results
2. **For blurry images**: Use `'morphological'` to enhance edges
3. **For compression artifacts**: Use `'adaptive'` targeting JPEG artifacts
4. **When in doubt**: Start with `'combined'` - it's the most robust

5. **Batch processing workflow**:
   - Test on a few images with different methods
   - Find best method for your image types
   - Apply that method to entire dataset

6. **Quality assessment**:
   - Always compare before/after quality scores
   - Monitor which distortions are reduced
   - Check if overall quality improved

---

## File Structure

```
visimpaired/
├── Notebooks/
│   ├── base_model.ipynb                    # Original quality assessment
│   ├── enhanced_quality_recovery.ipynb     # NEW: Enhancement + assessment
│   └── ...
├── scripts/
│   ├── image_enhancement.py                # NEW: Enhancement module
│   ├── mliqa_resnet50_tf.py
│   ├── mliqa_mobilenet_tf.py
│   └── ...
└── Dataset/
    ├── enhanced_images/                    # NEW: Output folder
    └── ...
```

---

## Troubleshooting

### Issue: "Out of memory" on large batch
**Solution**: Reduce batch size or process images one at a time
```python
# Process fewer images at once
batch_results = process_image_batch(..., max_images=5)
```

### Issue: No improvement in quality scores
**Solution**: 
- Try `'nlm'` method for heavy noise
- Check if image is already high-quality
- Try `compare_enhancement_methods()` to see all options

### Issue: Enhanced image looks worse
**Solution**:
- Some images (already high quality) may not benefit
- Try different enhancement method
- Check original quality score - enhancement helps most on lower-quality images

---

## Next Steps

1. **Run the notebook**: Open `enhanced_quality_recovery.ipynb` in Jupyter
2. **Try different methods**: Use `compare_enhancement_methods()` 
3. **Batch process**: Process your entire dataset with best method
4. **Analyze results**: Check quality improvements and save enhanced images

---

## References

- **Bilateral Filtering**: Tomasi & Manduchi, "Bilateral Filtering for Gray and Color Images" (1998)
- **Non-Local Means**: Buades et al., "A non-local algorithm for image denoising" (2005)
- **CLAHE**: Zuiderveld, "Contrast Limited Adaptive Histogram Equalization" (1994)
- **Morphological Operations**: OpenCV documentation

---

**Need help?** Check the example cells in `enhanced_quality_recovery.ipynb`
