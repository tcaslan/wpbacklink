import os
from PIL import Image, ImageDraw, ImageFont

def create_fallback_icon(icon_name, png_path, size=(64, 64)):
    """Create a fallback icon with text"""
    # Create a blank image with a blue background
    img = Image.new('RGBA', size, (59, 130, 246))  # Blue color
    draw = ImageDraw.Draw(img)
    
    # Map icon names to symbols (for text representation)
    icon_map = {
        'logo': "L",
        'browse': "B",
        'load': "L",
        'start': "▶",
        'pause': "⏸",
        'stop': "⏹",
        'save': "S",
        'reset': "R",
        'export': "E",
        'globe': "G",
        'flag_en': "EN",
        'flag_tr': "TR"
    }
    
    text = icon_map.get(icon_name, icon_name[0].upper())
    
    # Calculate text position (center)
    font_size = size[0] // 2
    try:
        # Try to load a font, fall back to default if not available
        try:
            font = ImageFont.truetype("Arial", font_size)
        except:
            font = ImageFont.load_default()
        
        # Get text size and position
        # PIL's textsize is deprecated in newer versions, so handle both cases
        if hasattr(draw, 'textsize'):
            text_width, text_height = draw.textsize(text, font=font)
        else:
            # For newer PIL versions
            try:
                text_width, text_height = font.getsize(text)
            except:
                text_width, text_height = font_size, font_size
                
        position = ((size[0] - text_width) // 2, (size[1] - text_height) // 2)
        
        # Draw text
        draw.text(position, text, fill=(255, 255, 255), font=font)
    except Exception as e:
        print(f"Error adding text to {icon_name}: {str(e)}")
    
    # Save the image
    img.save(png_path)
    print(f"Created fallback icon for {icon_name} at {png_path}")
    return True

def main():
    # Create icons directory if it doesn't exist
    if not os.path.exists('icons'):
        os.makedirs('icons')
        print("Created icons directory")
    
    # List of icon names to create
    icon_names = [
        'logo', 'browse', 'load', 'start', 'pause', 'stop',
        'save', 'reset', 'export', 'globe', 'flag_en', 'flag_tr'
    ]
    
    # Create fallback PNG icons
    for icon_name in icon_names:
        png_path = os.path.join('icons', f"{icon_name}.png")
        create_fallback_icon(icon_name, png_path)
    
    print("All fallback icons created successfully!")

if __name__ == "__main__":
    main() 