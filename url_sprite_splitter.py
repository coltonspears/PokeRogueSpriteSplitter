import json
import os
import argparse
import requests
from PIL import Image
from io import BytesIO

BASE_JSON_URL = "https://raw.githubusercontent.com/pagefaultgames/pokerogue/main/public/images/pokemon/{}.json"
BASE_PNG_URL = "https://raw.githubusercontent.com/pagefaultgames/pokerogue/f4a1c83a7ddff97895747d4129891f22a64b832b/public/images/pokemon/{}.png"

def download_file(url):
    response = requests.get(url)
    response.raise_for_status()  # Raise an exception for bad status codes
    return response.content

def get_frames(data):
    """Extract frames data from different JSON structures."""
    if 'textures' in data:
        return data['textures'][0]['frames']
    elif 'frames' in data:
        return data['frames']
    else:
        raise ValueError("Unsupported JSON structure. Cannot find frames data.")

def split_sprite(json_data, sprite_image, sprite_name):
    # Parse JSON data
    data = json.loads(json_data)

    # Create output directory if it doesn't exist
    output_dir = 'output_single'
    os.makedirs(output_dir, exist_ok=True)

    try:
        # Extract frame information from JSON
        frames = get_frames(data)

        # Process only the first frame
        if isinstance(frames, dict):
            frame_data = next(iter(frames.values()))
        elif isinstance(frames, list):
            frame_data = frames[0]
        else:
            raise ValueError(f"Unsupported frames data type: {type(frames)}")

        if isinstance(frame_data, dict):
            if 'frame' in frame_data:
                # TexturePacker format
                x = frame_data['frame']['x']
                y = frame_data['frame']['y']
                w = frame_data['frame']['w']
                h = frame_data['frame']['h']
            else:
                # Simple dictionary format
                x = frame_data['x']
                y = frame_data['y']
                w = frame_data['w']
                h = frame_data['h']
        elif isinstance(frame_data, list):
            # List format
            x, y, w, h = frame_data
        else:
            raise ValueError(f"Unsupported frame data format: {type(frame_data)}")

        # Generate the new filename
        filename = f"{sprite_name}.png"

        # Extract the individual image from the sprite
        img = Image.open(BytesIO(sprite_image))
        single_image = img.crop((x, y, x + w, y + h))

        # Save the image
        output_path = os.path.join(output_dir, filename)
        single_image.save(output_path)
        print(f"Saved {output_path}")

    except ValueError as e:
        print(f"Error processing sprite: {str(e)}")
    except KeyError as e:
        print(f"Error processing sprite: Missing key {str(e)}")

def process_sprite(sprite_name):
    json_url = BASE_JSON_URL.format(sprite_name)
    png_url = BASE_PNG_URL.format(sprite_name)

    try:
        # Download JSON data
        json_data = download_file(json_url)
        
        # Download PNG data
        png_data = download_file(png_url)

        # Process the sprite
        split_sprite(json_data, png_data, sprite_name)
    except requests.exceptions.RequestException as e:
        print(f"Error downloading files: {str(e)}")

if __name__ == "__main__":
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Download and split a sprite sheet, saving only the first image.")
    parser.add_argument("sprite_name", type=str, help="Name of the Pokemon sprite to process (e.g., '6-gigantamax')")

    # Parse arguments
    args = parser.parse_args()

    # Process the sprite
    process_sprite(args.sprite_name)