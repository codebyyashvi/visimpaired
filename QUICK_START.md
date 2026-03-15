# Quick Start Guide: Image Enhancement & Recovery

## 🚀 Get Started in 5 Minutes

### Step 1: Open the New Notebook
Open `Notebooks/enhanced_quality_recovery.ipynb` in Jupyter

### Step 2: Run the First Example Cell
This will load your quality assessment model and enhance a test image with results visualization.

### Step 3: View Results
You'll see:
- **Original image** with quality score
- **Enhanced image** with improved quality score  
- **Distortion comparison** - what problems were reduced

---

## 📊 What You Get

Each enhancement produces:

```
✅ Enhanced Image - higher visual quality
✅ Quality Score - numerical improvement metric
✅ Distortion Analysis - what problems were fixed
✅ Side-by-side Comparison - visual difference
```

---

## 🎯 Three Ways to Use

### Option 1: Jupyter Notebook (Recommended for exploration)
```
Open: Notebooks/enhanced_quality_recovery.ipynb
- Adjust parameters
- Visualize results
- Try different methods
```

### Option 2: Python Script (Command line)
```bash
# Single image
python scripts/enhance_images.py -i input.jpg -o output.jpg -m combined

# Batch processing
python scripts/enhance_images.py -b image_folder/ -o output_folder/ -m combined
```

### Option 3: Python Code (Custom integration)
```python
from scripts.image_enhancement import ImageEnhancer

enhancer = ImageEnhancer()
enhanced, metadata = enhancer.enhance(image, method='combined')
```

---

## 💡 Enhancement Methods - Quick Comparison

| Method | Speed | Quality | Best For |
|--------|-------|---------|----------|
| **bilateral** | ⚡⚡⚡ Fast | ⭐⭐⭐ | Usually good |
| **nlm** | ⚡ Slow | ⭐⭐⭐⭐⭐ | Heavy noise |
| **morphological** | ⚡⚡ Med | ⭐⭐⭐ | Blurry images |
| **adaptive** | ⚡⚡ Med | ⭐⭐⭐ | Artifacts |
| **combined** | ⚡⚡ Med | ⭐⭐⭐⭐⭐ | **Best overall** |

**Recommendation**: Start with `combined` - it gives the best results for most images.

---

## 🔄 Workflow Example

### Scenario: Enhance 10 test images

```python
# In enhanced_quality_recovery.ipynb

# Step 1: Load model (runs automatically)
# Step 2: Process batch
batch_results = process_image_batch(
    image_folder='../Dataset/Vizwiz-Data/test/',
    enhancement_method='combined',    # Use 'combined'
    output_folder='./enhanced_test_images',
    max_images=10
)

# Step 3: View results
# Prints table with before/after quality scores
```

**Output**:
- 10 enhanced images in `./enhanced_test_images/`
- Quality improvement for each one
- Summary statistics

---

## 📈 Understanding Results

### Quality Score
- **70+**: Excellent (little need for enhancement)
- **50-70**: Good (enhancement recommended)
- **30-50**: Fair (enhancement helpful)
- **<30**: Poor (needs significant enhancement)

### Quality Improvement
- `+0.5` = Quality improved by 0.5 points
- `-0.2` = Quality slightly reduced (rare)
- Larger positive = Better enhancement

### Distortion Identification
The model identifies what's wrong:
- 🔲 **Compression Artifacts** - JPEG effects
- 🌫️ **Blur** - Motion/focus blur
- 🔊 **Noise** - Random noise
- 🎨 **Oversaturation** - Too colorful
- 🌑 **Underexposure** - Too dark
- ☀️ **Overexposure** - Too bright

---

## ✨ Examples

### Example 1: Denoise a noisy image
```python
results = assess_and_enhance_image(
    'noisy_photo.jpg',
    enhancement_method='nlm'  # Best for noise
)
visualize_results(results)
```

### Example 2: Fix blurry image
```python
results = assess_and_enhance_image(
    'blurry_photo.jpg',
    enhancement_method='morphological'  # Sharpens
)
visualize_results(results)
```

### Example 3: Compare all methods
```python
# See which method works best
comparison_results = compare_enhancement_methods('test_image.jpg')
# Shows all 5 methods side-by-side
```

### Example 4: Batch enhance dataset
```python
batch_results = process_image_batch(
    image_folder='../Dataset/Vizwiz-Data/test/',
    enhancement_method='combined',
    output_folder='./enhanced_images'
)
```

---

## 🎓 Tips for Best Results

1. **Start with 'combined'** - works for ~90% of cases
2. **Check the dominant distortion** - helps choose best method
   - Lots of **noise** → Try `'nlm'`
   - Very **blurry** → Try `'morphological'`
   - **Artifacts** → Try `'adaptive'`

3. **Compare on your data** - use `compare_enhancement_methods()` to see all options

4. **Monitor improvements** - positive quality score = successful enhancement

5. **Save results** - script automatically saves enhanced images

---

## 🔧 Customization

### Change enhancement strength (advanced)
```python
# For more aggressive denoising
enhancer.non_local_means_denoise(
    image,
    h=15,  # Higher = more denoising
    template_window_size=7,
    search_window_size=21
)
```

### Try different input/output paths
```python
batch_results = process_image_batch(
    image_folder='path/to/your/images/',
    output_folder='path/to/save/enhanced/'
)
```

---

## ❓ Common Questions

**Q: Which method should I use?**
A: Start with `'combined'` - it's the most robust for general use.

**Q: Why didn't quality improve much?**
A: 
- Image might already be high quality
- Try different method for your image type
- Some distortions are harder to fix

**Q: Can I use this for real-time processing?**
A: Yes, `'bilateral'` is fastest. Use in production for speed.

**Q: Does enhancement improve model predictions?**
A: Usually yes! Cleaner image → better quality assessment.

**Q: Can I customize parameters?**
A: Yes! Use `ImageEnhancer` class directly for full control.

---

## 📚 Files Reference

| File | Purpose |
|------|---------|
| `Notebooks/enhanced_quality_recovery.ipynb` | Main notebook with examples |
| `scripts/image_enhancement.py` | Core enhancement module |
| `scripts/enhance_images.py` | Command-line tool |
| `ENHANCEMENT_GUIDE.md` | Detailed technical guide |

---

## 🚀 Next Steps

1. **Now**: Run the notebook `enhanced_quality_recovery.ipynb`
2. **Then**: Try batch processing on your test dataset
3. **Finally**: Enhance your full dataset with best method

---

## 📝 Example: Complete Pipeline

```python
# 1. Load model
quality_model = build_model_mobilenet()
quality_model.load_weights('test_models/mobilenet.h5')

# 2. Compare methods on one image
comparison_results = compare_enhancement_methods('test.jpg')
# → See which method is best for your image type

# 3. Batch process with best method
batch_results = process_image_batch(
    '../Dataset/Vizwiz-Data/test/',
    enhancement_method='combined',  # Use best method from step 2
    output_folder='./enhanced_images'
)

# 4. Review results
# Check enhanced_images/ folder for results
# Check console output for quality improvements
```

**Done!** ✅ Your images are now enhanced and recovered.

---

## 🎬 Ready?
→ Open `Notebooks/enhanced_quality_recovery.ipynb` and start enhancing!

---

Need more details? See `ENHANCEMENT_GUIDE.md`
