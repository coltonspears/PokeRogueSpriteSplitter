import json
import os
import argparse
import requests
from PIL import Image
from io import BytesIO

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

def split_sprite(json_data, sprite_image):
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
                filename = frame_data.get('filename', "frame_0.png")
            else:
                # Simple dictionary format
                x = frame_data['x']
                y = frame_data['y']
                w = frame_data['w']
                h = frame_data['h']
                filename = "frame_0.png"
        elif isinstance(frame_data, list):
            # List format
            x, y, w, h = frame_data
            filename = "frame_0.png"
        else:
            raise ValueError(f"Unsupported frame data format: {type(frame_data)}")

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

def process_url(json_url, png_url):
    try:
        # Download JSON data
        json_data = download_file(json_url)
        
        # Download PNG data
        png_data = download_file(png_url)

        # Process the sprite
        split_sprite(json_data, png_data)
    except requests.exceptions.RequestException as e:
        print(f"Error downloading files: {str(e)}")

if __name__ == "__main__":
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Download and split a sprite sheet, saving only the first image.")
    parser.add_argument("json_url", help="URL of the JSON file")
    parser.add_argument("png_url", help="URL of the PNG file")

    # Parse arguments
    args = parser.parse_args()

    # Process the URLs
    process_url(args.json_url, args.png_url)