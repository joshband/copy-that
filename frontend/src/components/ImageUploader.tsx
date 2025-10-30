import { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { XMarkIcon, PhotoIcon } from '@heroicons/react/24/outline';

interface UploadedImage {
  id: string;
  file: File;
  preview: string;
}

const MAX_IMAGES = 10;
const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB
const ACCEPTED_FORMATS = {
  'image/jpeg': ['.jpg', '.jpeg'],
  'image/png': ['.png'],
  'image/webp': ['.webp'],
  'image/gif': ['.gif']
};

export default function ImageUploader() {
  const [images, setImages] = useState<UploadedImage[]>([]);
  const [errors, setErrors] = useState<string[]>([]);

  const onDrop = useCallback((acceptedFiles: File[], rejectedFiles: any[]) => {
    setErrors([]);
    const newErrors: string[] = [];

    // Check total count
    if (images.length + acceptedFiles.length > MAX_IMAGES) {
      newErrors.push(`Maximum ${MAX_IMAGES} images allowed`);
      setErrors(newErrors);
      return;
    }

    // Validate and add accepted files
    const newImages: UploadedImage[] = acceptedFiles.map(file => ({
      id: Math.random().toString(36).substring(7),
      file,
      preview: URL.createObjectURL(file)
    }));

    // Handle rejected files
    if (rejectedFiles.length > 0) {
      rejectedFiles.forEach(rejected => {
        rejected.errors.forEach((error: any) => {
          if (error.code === 'file-too-large') {
            newErrors.push(`${rejected.file.name}: File too large (max 10MB)`);
          } else if (error.code === 'file-invalid-type') {
            newErrors.push(`${rejected.file.name}: Invalid file type`);
          } else {
            newErrors.push(`${rejected.file.name}: ${error.message}`);
          }
        });
      });
    }

    setImages(prev => [...prev, ...newImages]);
    if (newErrors.length > 0) {
      setErrors(newErrors);
    }
  }, [images.length]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: ACCEPTED_FORMATS,
    maxSize: MAX_FILE_SIZE,
    multiple: true,
    disabled: images.length >= MAX_IMAGES
  });

  const removeImage = (id: string) => {
    setImages(prev => {
      const updated = prev.filter(img => img.id !== id);
      // Revoke object URL to free memory
      const removed = prev.find(img => img.id === id);
      if (removed) {
        URL.revokeObjectURL(removed.preview);
      }
      return updated;
    });
  };

  const clearAll = () => {
    images.forEach(img => URL.revokeObjectURL(img.preview));
    setImages([]);
    setErrors([]);
  };

  return (
    <div className="w-full max-w-6xl mx-auto p-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Copy That
        </h1>
        <p className="text-gray-600">
          Upload up to {MAX_IMAGES} reference images to generate a design system
        </p>
      </div>

      {/* Dropzone */}
      <div
        {...getRootProps()}
        className={`
          border-2 border-dashed rounded-lg p-12 text-center cursor-pointer
          transition-colors duration-200
          ${isDragActive
            ? 'border-blue-500 bg-blue-50'
            : 'border-gray-300 hover:border-gray-400'
          }
          ${images.length >= MAX_IMAGES ? 'opacity-50 cursor-not-allowed' : ''}
        `}
      >
        <input {...getInputProps()} />
        <PhotoIcon className="mx-auto h-12 w-12 text-gray-400 mb-4" />
        {isDragActive ? (
          <p className="text-lg text-blue-600">Drop the images here...</p>
        ) : (
          <div>
            <p className="text-lg text-gray-700 mb-2">
              Drag & drop images here, or click to select
            </p>
            <p className="text-sm text-gray-500">
              {images.length}/{MAX_IMAGES} images uploaded • Max 10MB per image
            </p>
            <p className="text-xs text-gray-400 mt-2">
              Supported formats: JPG, PNG, WebP, GIF
            </p>
          </div>
        )}
      </div>

      {/* Errors */}
      {errors.length > 0 && (
        <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg">
          <h3 className="text-sm font-medium text-red-800 mb-2">Errors:</h3>
          <ul className="list-disc list-inside space-y-1">
            {errors.map((error, index) => (
              <li key={index} className="text-sm text-red-600">{error}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Image Grid */}
      {images.length > 0 && (
        <div className="mt-8">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-semibold text-gray-900">
              Uploaded Images ({images.length}/{MAX_IMAGES})
            </h2>
            <button
              onClick={clearAll}
              className="px-4 py-2 text-sm font-medium text-red-600 hover:text-red-700
                       hover:bg-red-50 rounded-lg transition-colors"
            >
              Clear All
            </button>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
            {images.map(image => (
              <div
                key={image.id}
                className="relative group aspect-square rounded-lg overflow-hidden
                         border-2 border-gray-200 hover:border-gray-300 transition-colors"
              >
                <img
                  src={image.preview}
                  alt={image.file.name}
                  className="w-full h-full object-cover"
                />
                <button
                  onClick={() => removeImage(image.id)}
                  className="absolute top-2 right-2 p-1.5 bg-red-500 hover:bg-red-600
                           text-white rounded-full opacity-0 group-hover:opacity-100
                           transition-opacity shadow-lg"
                  aria-label="Remove image"
                >
                  <XMarkIcon className="h-4 w-4" />
                </button>
                <div className="absolute bottom-0 left-0 right-0 bg-black bg-opacity-60
                              text-white text-xs p-2 truncate opacity-0 group-hover:opacity-100
                              transition-opacity">
                  {image.file.name}
                </div>
              </div>
            ))}
          </div>

          {/* Action Buttons */}
          <div className="mt-8 flex gap-4">
            <button
              className="flex-1 bg-blue-600 hover:bg-blue-700 text-white font-medium
                       py-3 px-6 rounded-lg transition-colors disabled:opacity-50
                       disabled:cursor-not-allowed"
              disabled={images.length === 0}
            >
              Generate Design System
            </button>
            <button
              className="px-6 py-3 border-2 border-gray-300 hover:border-gray-400
                       text-gray-700 font-medium rounded-lg transition-colors"
            >
              Save as Draft
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
