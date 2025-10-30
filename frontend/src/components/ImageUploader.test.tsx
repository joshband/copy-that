import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import ImageUploader from './ImageUploader';

describe('ImageUploader', () => {
  it('renders the upload area', () => {
    render(<ImageUploader />);
    expect(screen.getByText(/Copy That/i)).toBeInTheDocument();
    expect(screen.getByText(/Upload up to 10 reference images/i)).toBeInTheDocument();
  });

  it('displays drag and drop instructions', () => {
    render(<ImageUploader />);
    expect(screen.getByText(/Drag & drop images here, or click to select/i)).toBeInTheDocument();
  });

  it('shows correct image count limit', () => {
    render(<ImageUploader />);
    expect(screen.getByText(/0\/10 images uploaded/i)).toBeInTheDocument();
  });

  it('displays supported file formats', () => {
    render(<ImageUploader />);
    expect(screen.getByText(/Supported formats: JPG, PNG, WebP, GIF/i)).toBeInTheDocument();
  });

  it('shows file size limit', () => {
    render(<ImageUploader />);
    expect(screen.getByText(/Max 10MB per image/i)).toBeInTheDocument();
  });
});
