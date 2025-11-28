# scripts/generate_icons.py
"""
Generate placeholder icons for AutoResumeFiller Chrome Extension

Creates 3 PNG icons with blue background and white "ARF" text:
- icon16.png (16x16) - Toolbar icon
- icon48.png (48x48) - Management page icon
- icon128.png (128x128) - Chrome Web Store icon
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_icon(size, text, output_path):
    """Create a simple icon with text on blue background"""
    # Create blue background (#007bff)
    img = Image.new('RGB', (size, size), color='#007bff')
    draw = ImageDraw.Draw(img)
    
    # Calculate font size (roughly 1/3 of icon size)
    font_size = size // 3
    
    try:
        # Try to use Arial font
        font = ImageFont.truetype("arial.ttf", font_size)
    except:
        try:
            # Fallback to another common font
            font = ImageFont.truetype("Arial.ttf", font_size)
        except:
            # Use default font as last resort
            font = ImageFont.load_default()
    
    # Get text bounding box
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    # Center text
    x = (size - text_width) // 2
    y = (size - text_height) // 2 - font_size // 6
    
    # Draw text
    draw.text((x, y), text, font=font, fill='white')
    
    # Save
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    img.save(output_path)
    print(f'Created: {output_path}')

if __name__ == '__main__':
    # Generate all icon sizes
    create_icon(16, 'ARF', 'extension/icons/icon16.png')
    create_icon(48, 'ARF', 'extension/icons/icon48.png')
    create_icon(128, 'ARF', 'extension/icons/icon128.png')
    
    print('All icons generated successfully!')
