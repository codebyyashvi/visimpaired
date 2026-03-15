"""
Image Denoising and Enhancement Module
Provides multiple techniques to denoise and enhance images
"""

import cv2
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
import tensorflow as tf
from typing import Tuple, Dict
import warnings

warnings.filterwarnings('ignore')


class ImageEnhancer:
    """Comprehensive image denoising and enhancement"""
    
    def __init__(self):
        self.supported_methods = {
            'bilateral': self.bilateral_denoise,
            'nlm': self.non_local_means_denoise,
            'morphological': self.morphological_enhance,
            'adaptive': self.adaptive_denoise,
            'combined': self.combined_enhancement,
            'aggressive': self.aggressive_enhancement,
            'super_resolution': self.super_resolution_enhance
        }
    
    @staticmethod
    def bilateral_denoise(image: np.ndarray, diameter: int = 7, 
                         sigma_color: float = 50, sigma_space: float = 50) -> np.ndarray:
        """
        Bilateral filtering - light denoising while preserving edges AND COLORS
        OPTIMIZED: Brightness-only processing to prevent color shifts
        Best for: Blurry images with gentle noise
        
        Args:
            image: Input image (BGR or RGB)
            diameter: Pixel neighborhood diameter (reduced to 7 for minimal smoothing)
            sigma_color: Filter sigma in the color space (reduced to 50)
            sigma_space: Filter sigma in the coordinate space (reduced to 50)
        
        Returns:
            Denoised image (colors preserved)
        """
        # Ensure uint8 format
        if image.dtype != np.uint8:
            image_work = (image * 255).astype(np.uint8)
        else:
            image_work = image.copy()
        
        # Work in LAB color space - denoise ONLY brightness channel!
        if len(image_work.shape) == 2:  # Grayscale
            # Apply bilateral filter to grayscale
            denoised = cv2.bilateralFilter(image_work, diameter, sigma_color, sigma_space)
            
            # Main technique: Smart unsharp masking for sharpening
            blurred = cv2.GaussianBlur(denoised, (0, 0), 1.5)
            high_pass = cv2.subtract(denoised, blurred)
            sharpened = cv2.addWeighted(denoised, 1.0, high_pass, 2.0, 0)
            
        else:  # Color image - denoise ONLY brightness channel!
            # Convert to LAB color space
            lab = cv2.cvtColor(image_work, cv2.COLOR_BGR2LAB)
            L, A, B = cv2.split(lab)
            
            # Bilateral filter ONLY on L channel
            L_denoised = cv2.bilateralFilter(L, diameter, sigma_color, sigma_space)
            
            # Unsharp masking ONLY on L channel
            L_blurred = cv2.GaussianBlur(L_denoised, (0, 0), 1.5)
            L_high_pass = cv2.subtract(L_denoised, L_blurred)
            L_sharpened = cv2.addWeighted(L_denoised, 1.0, L_high_pass, 2.0, 0)
            
            # Clip brightness channel
            L_sharpened = np.clip(L_sharpened, 0, 255).astype(np.uint8)
            
            # Recombine with ORIGINAL A and B channels (colors unchanged!)
            lab_enhanced = cv2.merge([L_sharpened, A, B])
            sharpened = cv2.cvtColor(lab_enhanced, cv2.COLOR_LAB2BGR)
        
        # Convert back if needed
        if image.dtype != np.uint8:
            sharpened = sharpened.astype(np.float32) / 255.0
        else:
            sharpened = np.clip(sharpened, 0, 255).astype(np.uint8)
        
        return sharpened
    
    @staticmethod
    def non_local_means_denoise(image: np.ndarray, h: float = 10, 
                               template_window_size: int = 7,
                               search_window_size: int = 21) -> np.ndarray:
        """
        Non-Local Means Denoising - advanced noise reduction technique
        Best for: Heavy noise, fine details preservation
        
        Args:
            image: Input image
            h: Filter strength (higher = more noise reduction)
            template_window_size: Size of template patch
            search_window_size: Size of search area
        
        Returns:
            Denoised image
        """
        if len(image.shape) == 2:  # Grayscale
            denoised = cv2.fastNlMeansDenoising(
                image, 
                h=h, 
                templateWindowSize=template_window_size,
                searchWindowSize=search_window_size
            )
        else:  # Color - need to convert
            # Check if image is 0-255 range
            if image.dtype == np.uint8:
                # Assume BGR format
                denoised = cv2.fastNlMeansDenoisingColored(
                    image,
                    h=h,
                    templateWindowSize=template_window_size,
                    searchWindowSize=search_window_size
                )
            else:
                # Normalized format (0-1), convert to 0-255
                image_uint8 = (image * 255).astype(np.uint8)
                denoised = cv2.fastNlMeansDenoisingColored(
                    image_uint8,
                    h=h,
                    templateWindowSize=template_window_size,
                    searchWindowSize=search_window_size
                )
                denoised = denoised.astype(np.float32) / 255.0
        
        return denoised
    
    @staticmethod
    def morphological_enhance(image: np.ndarray, kernel_size: int = 3) -> np.ndarray:
        """
        Morphological operations for edge enhancement and sharpening
        Best for: Blurry images, edge definition
        
        Args:
            image: Input image
            kernel_size: Size of morphological kernel
        
        Returns:
            Enhanced image
        """
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (kernel_size, kernel_size))
        
        # Perform morphological gradient (edge enhancement)
        gradient = cv2.morphologyEx(image, cv2.MORPH_GRADIENT, kernel)
        
        # Enhance edges by adding gradient to original
        if image.dtype == np.uint8:
            enhanced = cv2.addWeighted(image, 1.0, gradient, 0.5, 0)
        else:
            enhanced = image + 0.5 * gradient
            enhanced = np.clip(enhanced, 0, 1.0 if image.dtype != np.uint8 else 255)
        
        return enhanced
    
    @staticmethod
    def aggressive_enhancement(image: np.ndarray) -> np.ndarray:
        """
        🔥 ULTRA AGGRESSIVE ENHANCEMENT - Maximum clarity and sharpness!
        Focus: EXTREME unsharp masking + heavy contrast + multi-pass sharpening on BRIGHTNESS ONLY
        NOTE: Only brightness is enhanced - COLORS REMAIN UNCHANGED!
        BEST FOR: Very blurry or heavily distorted images - MAXIMUM CLARITY!
        
        Args:
            image: Input image
        
        Returns:
            Massively enhanced image with maximum clarity (colors preserved)
        """
        # Ensure uint8 format
        if image.dtype != np.uint8:
            work_image = (image * 255).astype(np.uint8)
        else:
            work_image = image.copy()
        
        # Work in LAB color space - process only L (brightness) channel
        if len(work_image.shape) == 2:  # Grayscale
            # STEP 1: Minimal denoising to preserve details
            denoised = cv2.bilateralFilter(work_image, 5, 50, 50)
            
            # STEP 2: AGGRESSIVE contrast enhancement
            clahe = cv2.createCLAHE(clipLimit=5.0, tileGridSize=(2, 2))
            contrasted = clahe.apply(denoised)
            
            # STEP 3: EXTREME unsharp masking (Pass 1)
            blurred1 = cv2.GaussianBlur(contrasted, (0, 0), 1.0)
            high_pass1 = cv2.subtract(contrasted, blurred1)
            sharpened1 = cv2.addWeighted(contrasted, 1.0, high_pass1, 3.5, 0)  # 3.5x strength!
            sharpened1 = np.clip(sharpened1, 0, 255).astype(np.uint8)
            
            # STEP 4: EXTRA unsharp masking (Pass 2)
            blurred2 = cv2.GaussianBlur(sharpened1, (0, 0), 1.5)
            high_pass2 = cv2.subtract(sharpened1, blurred2)
            sharpened2 = cv2.addWeighted(sharpened1, 1.0, high_pass2, 2.0, 0)
            sharpened2 = np.clip(sharpened2, 0, 255).astype(np.uint8)
            
            # STEP 5: Edge enhancement kernel
            edge_kernel = np.array([[-2, -1,  0],
                                   [-1,  1,  1],
                                   [ 0,  1,  2]], dtype=np.float32)
            edges = cv2.filter2D(sharpened2, -1, edge_kernel)
            final = cv2.addWeighted(sharpened2, 0.9, np.abs(edges), 0.1, 0)
            
        else:  # Color image - process ONLY brightness channel!
            # Convert to LAB color space
            lab = cv2.cvtColor(work_image, cv2.COLOR_BGR2LAB)
            L, A, B = cv2.split(lab)
            
            # STEP 1: Minimal denoising to preserve details - ONLY on L
            L_denoised = cv2.bilateralFilter(L, 5, 50, 50)
            
            # STEP 2: AGGRESSIVE contrast enhancement - ONLY on L
            clahe = cv2.createCLAHE(clipLimit=5.0, tileGridSize=(2, 2))
            L_contrasted = clahe.apply(L_denoised)
            
            # STEP 3: EXTREME unsharp masking (Pass 1) - ONLY on L
            L_blurred1 = cv2.GaussianBlur(L_contrasted, (0, 0), 1.0)
            L_high_pass1 = cv2.subtract(L_contrasted, L_blurred1)
            L_sharpened1 = cv2.addWeighted(L_contrasted, 1.0, L_high_pass1, 3.5, 0)  # 3.5x strength!
            L_sharpened1 = np.clip(L_sharpened1, 0, 255).astype(np.uint8)
            
            # STEP 4: EXTRA unsharp masking (Pass 2) - ONLY on L
            L_blurred2 = cv2.GaussianBlur(L_sharpened1, (0, 0), 1.5)
            L_high_pass2 = cv2.subtract(L_sharpened1, L_blurred2)
            L_sharpened2 = cv2.addWeighted(L_sharpened1, 1.0, L_high_pass2, 2.0, 0)
            L_sharpened2 = np.clip(L_sharpened2, 0, 255).astype(np.uint8)
            
            # STEP 5: Edge enhancement kernel - ONLY on L
            edge_kernel = np.array([[-2, -1,  0],
                                   [-1,  1,  1],
                                   [ 0,  1,  2]], dtype=np.float32)
            L_edges = cv2.filter2D(L_sharpened2, -1, edge_kernel)
            L_final = cv2.addWeighted(L_sharpened2, 0.9, np.abs(L_edges).astype(np.uint8), 0.1, 0)
            
            # Clip brightness channel
            L_final = np.clip(L_final, 0, 255).astype(np.uint8)
            
            # Recombine with ORIGINAL A and B channels (colors unchanged!)
            lab_enhanced = cv2.merge([L_final, A, B])
            final = cv2.cvtColor(lab_enhanced, cv2.COLOR_LAB2BGR)
        
        # Clip and ensure valid range
        final = np.clip(final, 0, 255).astype(np.uint8)
        
        # Convert back to original format if needed
        if image.dtype != np.uint8:
            final = final.astype(np.float32) / 255.0
        
        return final
    
    @staticmethod
    def adaptive_denoise(image: np.ndarray, filter_strength: int = 10) -> np.ndarray:
        """
        Adaptive denoising using morphological closing
        Best for: Salt-and-pepper noise, structured artifacts
        
        Args:
            image: Input image
            filter_strength: Strength of denoising filter
        
        Returns:
            Denoised image
        """
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (filter_strength, filter_strength))
        
        # Morphological closing to remove small noise
        denoised = cv2.morphologyEx(image, cv2.MORPH_CLOSE, kernel)
        # Morphological opening to restore structure
        denoised = cv2.morphologyEx(denoised, cv2.MORPH_OPEN, kernel)
        
        return denoised
    
    @staticmethod
    def combined_enhancement(image: np.ndarray, 
                           denoise_strength: float = 0.7,
                           enhance_strength: float = 0.5) -> np.ndarray:
        """
        SMART Combined enhancement - Gentle denoise + Unsharp masking + CLAHE on BRIGHTNESS ONLY
        Optimized for blurry/distorted images (SHARPENING-FIRST strategy)
        NOTE: Only brightness is enhanced - COLORS REMAIN UNCHANGED!
        
        Args:
            image: Input image
            denoise_strength: Denoising weight (0-1)
            enhance_strength: Enhancement weight (0-1)
        
        Returns:
            Enhanced image (sharper, colors preserved)
        """
        # Ensure uint8 format for processing
        if image.dtype != np.uint8:
            image_work = (image * 255).astype(np.uint8)
        else:
            image_work = image.copy()
        
        # Work in LAB color space - process only L (brightness) channel
        if len(image_work.shape) == 2:  # Grayscale
            # Step 1: Light denoising
            denoised = cv2.bilateralFilter(image_work, 7, 50, 50)
            
            # Step 2: Smart unsharp masking
            blurred = cv2.GaussianBlur(denoised, (0, 0), 1.5)
            high_pass = cv2.subtract(denoised, blurred)
            sharpened = cv2.addWeighted(denoised, 1.0, high_pass, 1.8, 0)
            
            # Step 3: Contrast Enhancement
            clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
            enhanced = clahe.apply(sharpened)
            
            # Step 4: Morphological edge enhancement
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
            gradient = cv2.morphologyEx(enhanced, cv2.MORPH_GRADIENT, kernel)
            final = cv2.addWeighted(enhanced, 1.0, gradient, 0.4, 0)
            
        else:  # Color image - process ONLY brightness channel!
            # Convert to LAB color space
            lab = cv2.cvtColor(image_work, cv2.COLOR_BGR2LAB)
            L, A, B = cv2.split(lab)
            
            # Step 1: Light denoising - ONLY on L channel
            L_denoised = cv2.bilateralFilter(L, 7, 50, 50)
            
            # Step 2: Smart unsharp masking - ONLY on L channel
            L_blurred = cv2.GaussianBlur(L_denoised, (0, 0), 1.5)
            L_high_pass = cv2.subtract(L_denoised, L_blurred)
            L_sharpened = cv2.addWeighted(L_denoised, 1.0, L_high_pass, 1.8, 0)
            
            # Step 3: Contrast Enhancement - ONLY on L channel
            clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
            L_enhanced = clahe.apply(L_sharpened)
            
            # Step 4: Morphological edge enhancement - ONLY on L channel
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
            L_gradient = cv2.morphologyEx(L_enhanced, cv2.MORPH_GRADIENT, kernel)
            L_final = cv2.addWeighted(L_enhanced, 1.0, L_gradient, 0.4, 0)
            
            # Clip brightness channel
            L_final = np.clip(L_final, 0, 255).astype(np.uint8)
            
            # Recombine with ORIGINAL A and B channels (colors unchanged!)
            lab_enhanced = cv2.merge([L_final, A, B])
            final = cv2.cvtColor(lab_enhanced, cv2.COLOR_LAB2BGR)
        
        # Clip and ensure valid range
        final = np.clip(final, 0, 255).astype(np.uint8)
        
        # Convert back to original format if needed
        if image.dtype != np.uint8:
            final = final.astype(np.float32) / 255.0
        
        return final
    
    @staticmethod
    def super_resolution_enhance(image: np.ndarray, upscale_factor: int = 2) -> np.ndarray:
        """
        Super-resolution upscaling and detail recovery
        Best for: Downsampled/low-res images
        
        Args:
            image: Input image
            upscale_factor: Upscaling factor (2 or 4)
        
        Returns:
            Upscaled image
        """
        # Ensure uint8 format
        if image.dtype != np.uint8:
            image_uint8 = (image * 255).astype(np.uint8)
        else:
            image_uint8 = image
        
        # Use OpenCV's super resolution
        sr = cv2.dnn_superres.DnnSuperResImpl_create()
        
        # Load appropriate model based on upscale factor
        if upscale_factor == 2:
            model_path = 'ESPCN_x2.pb'
            model_name = 'espcn'
        elif upscale_factor == 4:
            model_path = 'ESPCN_x4.pb'
            model_name = 'espcn'
        
        try:
            sr.readModel(model_path)
            sr.setModel(model_name, upscale_factor)
            upscaled = sr.upsample(image_uint8)
            return upscaled
        except:
            # Fallback to simple interpolation if model not available
            h, w = image_uint8.shape[:2]
            upscaled = cv2.resize(image_uint8, (w * upscale_factor, h * upscale_factor),
                                interpolation=cv2.INTER_CUBIC)
            return upscaled
    
    def enhance(self, image: np.ndarray, method: str = 'combined', 
                return_all: bool = False) -> Tuple[np.ndarray, Dict]:
        """
        Main enhancement function
        
        Args:
            image: Input image
            method: Enhancement method ('bilateral', 'nlm', 'morphological', 
                   'adaptive', 'combined', 'super_resolution')
            return_all: If True, return all versions for comparison
        
        Returns:
            Enhanced image and metadata
        """
        if method not in self.supported_methods:
            raise ValueError(f"Unknown method: {method}. Supported: {list(self.supported_methods.keys())}")
        
        if return_all:
            results = {}
            for method_name, method_func in self.supported_methods.items():
                try:
                    results[method_name] = method_func(image.copy())
                except Exception as e:
                    results[method_name + '_error'] = str(e)
            return results
        
        enhanced = self.supported_methods[method](image.copy())
        
        metadata = {
            'method': method,
            'original_shape': image.shape,
            'enhanced_shape': enhanced.shape,
            'original_dtype': str(image.dtype),
            'enhanced_dtype': str(enhanced.dtype)
        }
        
        return enhanced, metadata


def load_and_enhance_image(image_path: str, method: str = 'combined',
                          target_size: Tuple[int, int] = (448, 448),
                          normalize: bool = True) -> Tuple[np.ndarray, np.ndarray, Dict]:
    """
    Load image, enhance it, and optionally resize/normalize
    
    Args:
        image_path: Path to image file
        method: Enhancement method
        target_size: Target output size
        normalize: Whether to normalize to 0-1 range
    
    Returns:
        Original image, enhanced image, metadata
    """
    # Load image
    image = cv2.imread(image_path)
    if image is None:
        raise FileNotFoundError(f"Image not found: {image_path}")
    
    # Convert BGR to RGB if needed
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    # Create enhancer
    enhancer = ImageEnhancer()
    
    # Enhance
    enhanced, metadata = enhancer.enhance(image, method=method)
    
    # Resize if specified
    if target_size:
        image_resized = cv2.resize(image, target_size)
        enhanced_resized = cv2.resize(enhanced, target_size)
    else:
        image_resized = image
        enhanced_resized = enhanced
    
    # Normalize if specified
    if normalize:
        image_resized = image_resized.astype(np.float32) / 255.0
        enhanced_resized = enhanced_resized.astype(np.float32) / 255.0
    else:
        image_resized = image_resized.astype(np.uint8)
        enhanced_resized = enhanced_resized.astype(np.uint8)
    
    metadata['normalized'] = normalize
    metadata['target_size'] = target_size
    
    return image_resized, enhanced_resized, metadata


def save_enhanced_image(enhanced_image: np.ndarray, output_path: str,
                       original_range: str = 'normalized'):
    """
    Save enhanced image to disk
    
    Args:
        enhanced_image: Enhanced image array
        output_path: Output file path
        original_range: 'normalized' (0-1) or 'uint8' (0-255)
    """
    if original_range == 'normalized':
        # Convert from 0-1 to 0-255
        image_to_save = (enhanced_image * 255).astype(np.uint8)
    else:
        image_to_save = enhanced_image.astype(np.uint8)
    
    # Convert RGB back to BGR for OpenCV
    image_to_save = cv2.cvtColor(image_to_save, cv2.COLOR_RGB2BGR)
    
    # Create output directory if needed
    import os
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    cv2.imwrite(output_path, image_to_save)
    print(f"Enhanced image saved to: {output_path}")


# Example usage
if __name__ == "__main__":
    # Test the enhancement on a sample image
    test_image_path = "../Dataset/Vizwiz-Data/test/test_image.jpg"
    
    try:
        original, enhanced, metadata = load_and_enhance_image(
            test_image_path,
            method='combined',
            target_size=(448, 448),
            normalize=True
        )
        
        print("Enhancement metadata:", metadata)
        print(f"Original shape: {original.shape}, Enhanced shape: {enhanced.shape}")
        
        # Save enhanced image
        save_enhanced_image(enhanced, "./test_enhanced_output.jpg", original_range='normalized')
        
    except Exception as e:
        print(f"Error: {e}")
