#!/usr/bin/env python
"""Create a colorful test image for color extraction testing"""

from PIL import Image, ImageDraw
import os

def create_test_image():
    """Create a colorful test image"""
    width, height = 800, 600

    # Create image with white background
    img = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(img)

    # Define colors for different sections
    colors = [
        ((255, 107, 107), 'Coral Red'),      # Top left
        ((78, 205, 196), 'Teal'),            # Top center
        ((69, 183, 209), 'Sky Blue'),        # Top right
        ((149, 225, 211), 'Mint Green'),     # Middle left
        ((240, 165, 0), 'Amber'),            # Middle center
        ((100, 150, 200), 'Steel Blue'),     # Middle right
        ((220, 100, 150), 'Rose'),           # Bottom left
        ((255, 200, 100), 'Peach'),          # Bottom center
        ((100, 200, 100), 'Sage Green'),     # Bottom right
    ]

    # Draw 3x3 grid of colored rectangles
    rect_width = width // 3
    rect_height = height // 3

    for idx, (color, name) in enumerate(colors):
        row = idx // 3
        col = idx % 3

        x1 = col * rect_width
        y1 = row * rect_height
        x2 = x1 + rect_width
        y2 = y1 + rect_height

        # Draw filled rectangle
        draw.rectangle([x1, y1, x2, y2], fill=color, outline='black', width=2)

        # Add text label
        text_x = x1 + rect_width // 2 - 40
        text_y = y1 + rect_height // 2 - 10
        draw.text((text_x, text_y), name, fill='black' if sum(color) > 400 else 'white')

    # Save the image
    output_path = 'test_image.png'
    img.save(output_path)
    print(f"✅ Created test image: {output_path}")
    print(f"   Size: {width}x{height} pixels")
    print(f"   Colors: 9 distinct colors in 3x3 grid")
    print(f"\n   Run color extraction with:")
    print(f"   python test_color_extraction.py {output_path}")

    return output_path

if __name__ == '__main__':
    create_test_image()
