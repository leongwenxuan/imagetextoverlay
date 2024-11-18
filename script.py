import os
import json
from PIL import Image, ImageDraw, ImageFont
import textwrap
import unicodedata 
from pilmoji import Pilmoji

def process_image(image_path, captions):
    img = Image.open(image_path)
    
    target_ratio = 1080 / 1350
    img_ratio = img.size[0] / img.size[1]
    
    top_margin = 100
    line_spacing = 180  # Vertical space between caption groups
    emoji_offset = 70   # Space between emoji
    
    
    if img_ratio > target_ratio:
        new_width = int(img.size[1] * target_ratio)
        left = (img.size[0] - new_width) // 2
        img = img.crop((left, 0, left + new_width, img.size[1]))
    else:
        new_height = int(img.size[0] / target_ratio)
        top = (img.size[1] - new_height) // 2
        img = img.crop((0, top, img.size[0], top + new_height))

    img = img.resize((1080, 1350), Image.Resampling.LANCZOS)
    img_width, img_height = img.size    
    
    # Font setup
    
    firstIndexHeaderFontSize = 40
    firstIndexSubHeaderFontSize = 30
    headerfontsize = 25
    subheaderfontsize = 20
    
    try:
        headerfont = ImageFont.truetype(font="./font/TikTokText-Bold.ttf", size=headerfontsize)
        subheaderfont = ImageFont.truetype(font="./font/TikTokText-Bold.ttf", size=subheaderfontsize)
        firstIndexHeaderFont = ImageFont.truetype(font="./font/TikTokText-Bold.ttf", size=firstIndexHeaderFontSize)
        firstIndexSubHeaderFont = ImageFont.truetype(font="./font/TikTokText-Bold.ttf", size=firstIndexSubHeaderFontSize)
        emoji_font = ImageFont.truetype('/System/Library/Fonts/Apple Color Emoji.ttc', 64)

        test_emojis = ["😀", "🎉", "❤️"]
        for emoji in test_emojis:
            if emoji_font.getbbox(emoji) is None:
                print(f"Warning: Cannot render emoji: {emoji}")
                return
            
    except Exception as e:
        print(f"Font failed to load: {e}")
        return
    
    
    draw = Pilmoji(img)
    
    # Draw captions
    for idx, item in enumerate(captions):
        headeremoji = item["headeremoji"]    
        header = item["header"]
        subheader = item["subheader"]
        
        # Get actual text dimensions
        current_header_font = firstIndexHeaderFont if idx == 0 else headerfont
        current_subheader_font = firstIndexSubHeaderFont if idx == 0 else subheaderfont
        
        header_bbox = current_header_font.getbbox(header)
        header_width = header_bbox[2] - header_bbox[0]

        
        edge_padding = 150  # Distance from edges (adjust this to bring left/right closer)
        rightedge_paddding = 180
        
        # Update base_y calculation to account for larger first caption
        base_y = top_margin + (idx * line_spacing)
        if idx > 0:
            # Add extra spacing after first caption to account for larger font
            base_y += 50  # Adjust this value based on your needs
            
        if idx == 0:
            # Center the first caption
            x_pos = (img_width - header_width) // 2
            header_position = (x_pos, base_y)
            subheader_position = (x_pos, base_y + firstIndexHeaderFontSize + 30)  # Use firstIndexHeaderFontSize
            emoji_position = (x_pos - emoji_offset, base_y)
                
        if idx == 0:
            # Center the first caption
            x_pos = (img_width - header_width) // 2
            header_position = (x_pos, base_y)
            subheader_position = (x_pos, base_y + headerfontsize + 30)
            emoji_position = (x_pos - emoji_offset, base_y)
        else:
            # Alternate between left and right alignment
            if idx % 2 == 1:
                x_pos = edge_padding
            else:
                x_pos = img_width - header_width - rightedge_paddding
                
            header_position = (x_pos, base_y)
            subheader_position = (x_pos, base_y + headerfontsize + 10)
            emoji_position = (x_pos - emoji_offset, base_y)
        
        wrapped_subheader = "\n".join(textwrap.fill(subheader, width=30).splitlines())  # Adjust width as needed

        draw.text(header_position, header, font=current_header_font, fill="white", stroke_fill="black", stroke_width=2)
        y_offset = subheader_position[1]
        for line in wrapped_subheader.splitlines():
            draw.text(
                (subheader_position[0], y_offset), 
                line, 
                font=current_subheader_font, 
                fill="white", 
                stroke_fill="black", 
                stroke_width=2
            )
            y_offset += current_subheader_font.size + 4 
        draw.text(emoji_position, headeremoji, font=emoji_font)

        
    # Save the processed image
    output_dir = os.path.join(os.path.dirname(image_path), "processed_images")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"processed_{os.path.basename(image_path)}")
    img.save(output_path)
    return output_path
    

def main():
    posts_dir = "posts"
    caption_file = "captions.json"
    image_extensions = ('.jpg', '.jpeg', '.png')

    for post_folder in os.listdir(posts_dir):
        post_dir = os.path.join(posts_dir, post_folder)
        if not os.path.isdir(post_dir):  
            continue
    
        caption_file_path = os.path.join(post_dir, caption_file)
        if not os.path.exists(caption_file_path):
            print(f"Skipping {post_folder}: No captions file found")
            continue
        
        with open(caption_file_path, "r") as file:
            data = json.load(file)
            image_files = sorted([f for f in os.listdir(post_dir) 
                if f.lower().endswith(image_extensions)])
            
            print(f"\nProcessing folder: {post_folder}")
            num_images = len(image_files)
            num_captions = len(data['images'])
            
            if num_images != num_captions:
                print(f"ERROR in {post_folder}: Number of images ({num_images}) does not match number of captions ({num_captions})")
                continue

            # Just print info instead of processing
            for idx, image_file in enumerate(image_files):
                if idx >= len(data["images"]):
                    print(f"Warning: No caption data for {image_file}")
                    break
                    
                image_path = os.path.join(post_dir, image_file)
                captions = data["images"][idx]
                processed_path = process_image(image_path, captions)
                print(f"Processed {image_file} -> {processed_path}")

if __name__ == "__main__":
    main()