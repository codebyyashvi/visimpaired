#!/usr/bin/env python3
"""
Command-line tool for image enhancement and quality assessment
Usage: python enhance_images.py -i image.jpg -m combined -o output.jpg
"""

import argparse
import os
import sys
import numpy as np
import tensorflow as tf
import cv2
from pathlib import Path

sys.path.append('./scripts')

from image_enhancement import ImageEnhancer, save_enhanced_image


def build_model_mobilenet():
    """Build MobileNetV2 based quality assessment model"""
    IMG_SIZE = 448
    CHANNELS = 3

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

    # Head 1 → Distortion distribution (output_1)
    x1 = tf.keras.layers.Dense(32, activation='relu', name='hidden_layer2')(x)
    x1 = tf.keras.layers.Dropout(0.2)(x1)
    output_1 = tf.keras.layers.Dense(7, name='output_1')(x1)

    # Head 2 → Quality score (output_2)
    x2 = tf.keras.layers.Dense(32, activation='relu', name='hidden_layer3')(x)
    x2 = tf.keras.layers.Dropout(0.2)(x2)
    output_2 = tf.keras.layers.Dense(1, name='output_2')(x2)

    model = tf.keras.models.Model(inputs=input_layer,
                                  outputs=[output_1, output_2])
    return model


def assess_quality(image, model, img_size=448, channels=3):
    """Assess image quality and distortions"""
    distortion_types = [
        'Compression Artifacts', 'Blur', 'Noise', 'Oversaturation',
        'Underexposure', 'Overexposure', 'Other'
    ]
    
    # Resize and normalize
    image_resized = cv2.resize(image, (img_size, img_size))
    image_normalized = image_resized.astype(np.float32) / 255.0
    
    # Get predictions
    distortions, quality_score = model.predict(
        np.array([image_normalized]),
        verbose=0
    )
    
    quality = float(quality_score[0][0])
    distortion_probs = distortions[0]
    
    # Find dominant distortion
    dominant_idx = np.argmax(distortion_probs)
    dominant_distortion = distortion_types[dominant_idx]
    dominant_confidence = float(distortion_probs[dominant_idx])
    
    return {
        'quality_score': quality,
        'distortions': dict(zip(distortion_types, distortion_probs)),
        'dominant_distortion': dominant_distortion,
        'dominant_confidence': dominant_confidence
    }


def process_single_image(input_path, output_path, model_path, enhancement_method='combined',
                         save_original=False, verbose=True):
    """
    Process a single image with enhancement and quality assessment
    
    Args:
        input_path: Path to input image
        output_path: Path to save enhanced image
        model_path: Path to quality model weights
        enhancement_method: Method to use for enhancement
        save_original: Also save evaluation of original image
        verbose: Print progress
    
    Returns:
        Dictionary with results
    """
    
    if verbose:
        print(f"\n{'='*60}")
        print(f"Processing: {input_path}")
        print(f"{'='*60}")
    
    # Load image
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Image not found: {input_path}")
    
    image = cv2.imread(input_path)
    if image is None:
        raise ValueError(f"Cannot read image: {input_path}")
    
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    # Load model
    if verbose:
        print("Loading quality assessment model...")
    
    os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
    model = build_model_mobilenet()
    
    if os.path.exists(model_path):
        model.load_weights(model_path)
        if verbose:
            print("Model weights loaded successfully")
    else:
        if verbose:
            print(f"Warning: Model weights not found at {model_path}")
    
    # Assess original
    if verbose:
        print("Assessing original image quality...")
    
    original_assessment = assess_quality(image, model)
    
    print(f"\nOriginal Image:")
    print(f"  Quality Score: {original_assessment['quality_score']:.6f}")
    print(f"  Dominant Distortion: {original_assessment['dominant_distortion']}")
    print(f"  Confidence: {original_assessment['dominant_confidence']:.6f}")
    
    # Enhance
    if verbose:
        print(f"\nApplying '{enhancement_method}' enhancement...")
    
    enhancer = ImageEnhancer()
    enhanced_image, metadata = enhancer.enhance(image.copy(), method=enhancement_method)
    
    # Assess enhanced
    if verbose:
        print("Assessing enhanced image quality...")
    
    enhanced_assessment = assess_quality(enhanced_image, model)
    
    print(f"\nEnhanced Image ({enhancement_method}):")
    print(f"  Quality Score: {enhanced_assessment['quality_score']:.6f}")
    print(f"  Dominant Distortion: {enhanced_assessment['dominant_distortion']}")
    print(f"  Confidence: {enhanced_assessment['dominant_confidence']:.6f}")
    
    improvement = enhanced_assessment['quality_score'] - original_assessment['quality_score']
    print(f"\nQuality Improvement: {improvement:+.6f}")
    
    # Save enhanced image
    os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
    enhanced_bgr = cv2.cvtColor(enhanced_image, cv2.COLOR_RGB2BGR)
    cv2.imwrite(output_path, enhanced_bgr)
    
    if verbose:
        print(f"\nEnhanced image saved to: {output_path}")
    
    # Save original assessment if requested
    if save_original:
        original_output = output_path.replace('.', '_original.')
        if '.' in output_path:
            base, ext = output_path.rsplit('.', 1)
            original_output = f"{base}_original.{ext}"
        
        original_bgr = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        cv2.imwrite(original_output, original_bgr)
        if verbose:
            print(f"Original image saved to: {original_output}")
    
    return {
        'input_file': input_path,
        'output_file': output_path,
        'original_assessment': original_assessment,
        'enhanced_assessment': enhanced_assessment,
        'improvement': improvement,
        'enhancement_method': enhancement_method
    }


def process_batch(input_dir, output_dir, model_path, enhancement_method='combined',
                 pattern='*.jpg', max_images=None, verbose=True):
    """
    Process multiple images
    
    Args:
        input_dir: Directory containing images
        output_dir: Directory to save enhanced images
        model_path: Path to quality model weights
        enhancement_method: Enhancement method to use
        pattern: File pattern (e.g., '*.jpg')
        max_images: Maximum number of images to process
        verbose: Print progress
    
    Returns:
        List of results for each image
    """
    
    # Find images
    input_path = Path(input_dir)
    image_files = list(input_path.glob(pattern))
    
    if max_images:
        image_files = image_files[:max_images]
    
    if verbose:
        print(f"\nFound {len(image_files)} images to process")
        print(f"Enhancement method: {enhancement_method}")
        print(f"Output directory: {output_dir}\n")
    
    os.makedirs(output_dir, exist_ok=True)
    
    all_results = []
    
    for idx, image_file in enumerate(image_files, 1):
        try:
            output_file = os.path.join(output_dir, f"enhanced_{image_file.name}")
            
            result = process_single_image(
                str(image_file),
                output_file,
                model_path,
                enhancement_method=enhancement_method,
                verbose=verbose
            )
            
            all_results.append(result)
            
            print(f"\n[{idx}/{len(image_files)}] ✓ Completed")
            
        except Exception as e:
            print(f"\n[{idx}/{len(image_files)}] ✗ Error: {str(e)}")
            all_results.append({
                'input_file': str(image_file),
                'error': str(e)
            })
    
    # Print summary
    if verbose:
        print(f"\n{'='*60}")
        print("BATCH PROCESSING SUMMARY")
        print(f"{'='*60}")
        
        successful = [r for r in all_results if 'error' not in r]
        failed = [r for r in all_results if 'error' in r]
        
        print(f"Successful: {len(successful)}/{len(all_results)}")
        print(f"Failed: {len(failed)}/{len(all_results)}")
        
        if successful:
            improvements = [r['improvement'] for r in successful]
            print(f"\nAverage Quality Improvement: {np.mean(improvements):+.6f}")
            print(f"Median Quality Improvement: {np.median(improvements):+.6f}")
            print(f"Min Improvement: {np.min(improvements):+.6f}")
            print(f"Max Improvement: {np.max(improvements):+.6f}")
            print(f"Images Improved: {sum(1 for i in improvements if i > 0)}/{len(improvements)}")
        
        print(f"{'='*60}\n")
    
    return all_results


def main():
    parser = argparse.ArgumentParser(
        description='Image Enhancement and Quality Assessment Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:

  Single image enhancement:
    python enhance_images.py -i input.jpg -o output.jpg

  Batch processing:
    python enhance_images.py -b input_folder/ -o output_folder/ --method combined

  Try different method:
    python enhance_images.py -i input.jpg -o output.jpg -m bilateral

  Supported methods: bilateral, nlm, morphological, adaptive, combined
        """
    )
    
    # Input arguments
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument('-i', '--input', type=str,
                            help='Input image file')
    input_group.add_argument('-b', '--batch', type=str,
                            help='Input directory for batch processing')
    
    # Output arguments
    parser.add_argument('-o', '--output', type=str, required=True,
                       help='Output file or directory')
    
    # Enhancement options
    parser.add_argument('-m', '--method', type=str, default='combined',
                       choices=['bilateral', 'nlm', 'morphological', 'adaptive', 'combined'],
                       help='Enhancement method (default: combined)')
    
    # Model path
    parser.add_argument('--model', type=str,
                       default='./Notebooks/test_models/mobilenet.h5',
                       help='Path to quality assessment model weights')
    
    # Batch options
    parser.add_argument('--pattern', type=str, default='*.jpg',
                       help='File pattern for batch processing (default: *.jpg)')
    parser.add_argument('--max-images', type=int,
                       help='Maximum number of images to process')
    parser.add_argument('--save-original', action='store_true',
                       help='Also save original image')
    
    # Control options
    parser.add_argument('-q', '--quiet', action='store_true',
                       help='Reduce output verbosity')
    
    args = parser.parse_args()
    
    verbose = not args.quiet
    
    try:
        if args.input:
            # Single image
            process_single_image(
                args.input,
                args.output,
                args.model,
                enhancement_method=args.method,
                save_original=args.save_original,
                verbose=verbose
            )
        else:
            # Batch processing
            process_batch(
                args.batch,
                args.output,
                args.model,
                enhancement_method=args.method,
                pattern=args.pattern,
                max_images=args.max_images,
                verbose=verbose
            )
    
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
