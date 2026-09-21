/**
 * Shared file handling utilities
 */

type ResizeOptions = {
  maxDimension?: number;
  quality?: number;
  mimeType?: string;
};

/**
 * Convert a File to base64 data URL
 */
export function fileToBase64(file: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(reader.result as string);
    reader.onerror = (error) => reject(error);
    reader.readAsDataURL(file);
  });
}

/**
 * Validate that a file is an image
 */
export function isValidImageFile(file: File): boolean {
  return file.type.startsWith('image/');
}

/**
 * Get image dimensions from a File
 */
export function getImageDimensions(
  file: File
): Promise<{ width: number; height: number }> {
  return new Promise((resolve, reject) => {
    const img = new Image();
    const url = URL.createObjectURL(file);

    img.onload = () => {
      URL.revokeObjectURL(url);
      resolve({ width: img.width, height: img.height });
    };

    img.onerror = () => {
      URL.revokeObjectURL(url);
      reject(new Error('Failed to load image'));
    };

    img.src = url;
  });
}

/**
 * Extract base64 data from a data URL
 */
export function extractBase64FromDataUrl(dataUrl: string): {
  mediaType: string;
  base64: string;
} | null {
  const match = dataUrl.match(/^data:([^;]+);base64,(.+)$/);

  if (!match) return null;

  return {
    mediaType: match[1],
    base64: match[2],
  };
}

/**
 * Validate file size (in bytes)
 */
export function isFileSizeValid(file: File, maxSizeBytes: number): boolean {
  return file.size <= maxSizeBytes;
}

/**
 * Format file size for display
 */
export function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 Bytes';

  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));

  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

/**
 * Resize and compress an image client-side before upload.
 * Returns dataUrl, base64 (no prefix), and mediaType.
 */
export async function resizeImageFile(
  file: File,
  { maxDimension = 1400, quality = 0.82, mimeType }: ResizeOptions = {}
): Promise<{ dataUrl: string; base64: string; mediaType: string }> {
  const targetMime = mimeType ?? 'image/jpeg';

  const dataUrl = await fileToBase64(file);
  const img = await new Promise<HTMLImageElement>((resolve, reject) => {
    const image = new Image();
    image.onload = () => resolve(image);
    image.onerror = reject;
    image.src = dataUrl;
  });

  const { width, height } = img;
  const scale = Math.min(1, maxDimension / Math.max(width, height));
  const targetWidth = Math.round(width * scale);
  const targetHeight = Math.round(height * scale);

  const canvas = document.createElement('canvas');
  canvas.width = targetWidth;
  canvas.height = targetHeight;
  const ctx = canvas.getContext('2d');
  if (!ctx) {
    throw new Error('Canvas not supported');
  }
  ctx.drawImage(img, 0, 0, targetWidth, targetHeight);

  const compressedDataUrl = canvas.toDataURL(targetMime, quality);
  const extracted = extractBase64FromDataUrl(compressedDataUrl);
  if (!extracted) {
    throw new Error('Failed to extract base64 from compressed image');
  }

  return {
    dataUrl: compressedDataUrl,
    base64: extracted.base64,
    mediaType: extracted.mediaType,
  };
}
