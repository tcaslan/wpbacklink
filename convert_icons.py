import os
import sys
import cairosvg
from PIL import Image, ImageDraw, ImageFont

def convert_svg_to_png(svg_path, png_path, size=(64, 64)):
    """Convert an SVG file to PNG format"""
    try:
        cairosvg.svg2png(url=svg_path, write_to=png_path, output_width=size[0], output_height=size[1])
        print(f"Converted {svg_path} to {png_path}")
        return True
    except Exception as e:
        print(f"Error converting {svg_path}: {str(e)}")
        return False

def create_fallback_icon(icon_name, png_path, size=(64, 64)):
    """Create a fallback icon with text"""
    # Create a blank image with a blue background
    img = Image.new('RGBA', size, (59, 130, 246))  # Blue color
    draw = ImageDraw.Draw(img)
    
    # Try to add text (first letter of icon name)
    try:
        # Map icon names to symbols
        icon_map = {
            'logo': "🔗",
            'browse': "📂",
            'load': "📥",
            'start': "▶️",
            'pause': "⏸️",
            'stop': "⏹️",
            'save': "💾",
            'reset': "🔄",
            'export': "📤",
            'globe': "🌐",
            'flag_en': "🇬🇧",
            'flag_tr': "🇹🇷"
        }
        
        text = icon_map.get(icon_name, icon_name[0].upper())
        
        # Calculate text position (center)
        font_size = size[0] // 2
        try:
            font = ImageFont.truetype("Arial", font_size)
        except:
            font = ImageFont.load_default()
            
        # For emoji, just use the first letter if emoji rendering fails
        if len(text) > 1 and ord(text[0]) > 127:
            text = icon_name[0].upper()
            
        # Get text size and position
        text_width, text_height = draw.textsize(text, font=font) if hasattr(draw, 'textsize') else (font_size, font_size)
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
    
    # Try to convert SVG files to PNG
    for icon_name in icon_names:
        svg_path = os.path.join('icons', f"{icon_name}.svg")
        png_path = os.path.join('icons', f"{icon_name}.png")
        
        # Check if SVG exists
        if os.path.exists(svg_path):
            try:
                # Try to convert SVG to PNG
                success = convert_svg_to_png(svg_path, png_path)
                if not success:
                    # If conversion fails, create a fallback icon
                    create_fallback_icon(icon_name, png_path)
            except:
                # If cairosvg is not available, create a fallback icon
                create_fallback_icon(icon_name, png_path)
        else:
            # If SVG doesn't exist, check for temp SVG
            temp_svg_path = f"temp_{icon_name}.svg"
            if os.path.exists(temp_svg_path):
                try:
                    # Try to convert temp SVG to PNG
                    success = convert_svg_to_png(temp_svg_path, png_path)
                    if not success:
                        # If conversion fails, create a fallback icon
                        create_fallback_icon(icon_name, png_path)
                except:
                    # If cairosvg is not available, create a fallback icon
                    create_fallback_icon(icon_name, png_path)
            else:
                # If no SVG exists, create a fallback icon
                create_fallback_icon(icon_name, png_path)

if __name__ == "__main__":
    main() 