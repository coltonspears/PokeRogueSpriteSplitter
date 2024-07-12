import json
import os
import argparse
from PIL import Image

def get_frames(data):
    """Extract frames data from different JSON structures."""
    if 'textures' in data:
        return data['textures'][0]['frames']
    elif 'frames' in data:
        return data['frames']
    else:
        raise ValueError("Unsupported JSON structure. Cannot find frames data.")

def split_sprite(json_file, sprite_image):
    # Load JSON data
    with open(json_file, 'r') as f:
        data = json.load(f)

    # Open the sprite image
    sprite = Image.open(sprite_image)

    # Create output directory if it doesn't exist
    output_dir = os.path.join('output2', os.path.splitext(os.path.basename(sprite_image))[0])
    os.makedirs(output_dir, exist_ok=True)

    try:
        # Extract frame information from JSON
        frames = get_frames(data)

        # Process each frame
        if isinstance(frames, dict):
            frame_items = frames.items()
        elif isinstance(frames, list):
            frame_items = enumerate(frames)
        else:
            raise ValueError(f"Unsupported frames data type: {type(frames)}")

        for frame_id, frame_data in frame_items:
            if isinstance(frame_data, dict):
                if 'frame' in frame_data:
                    # TexturePacker format
                    x = frame_data['frame']['x']
                    y = frame_data['frame']['y']
                    w = frame_data['frame']['w']
                    h = frame_data['frame']['h']
                    filename = frame_data.get('filename', f"frame_{frame_id}.png")
                else:
                    # Simple dictionary format
                    x = frame_data['x']
                    y = frame_data['y']
                    w = frame_data['w']
                    h = frame_data['h']
                    filename = f"frame_{frame_id}.png"
            elif isinstance(frame_data, list):
                # List format
                x, y, w, h = frame_data
                filename = f"frame_{frame_id}.png"
            else:
                print(f"Skipping frame {frame_id}: Unsupported format")
                continue

            # Extract the individual image from the sprite
            img = sprite.crop((x, y, x + w, y + h))

            # Save the image
            output_path = os.path.join(output_dir, filename)
            img.save(output_path)
            print(f"Saved {output_path}")

    except ValueError as e:
        print(f"Error processing {json_file}: {str(e)}")
    except KeyError as e:
        print(f"Error processing {json_file}: Missing key {str(e)}")

def process_directory(directory):
    # Get all JSON files in the directory
    json_files = [f for f in os.listdir(directory) if f.endswith('.json')]

    for json_file in json_files:
        # Construct the full path to the JSON file
        json_path = os.path.join(directory, json_file)

        # Construct the corresponding PNG file name
        png_file = os.path.splitext(json_file)[0] + '.png'
        png_path = os.path.join(directory, png_file)

        # Check if the corresponding PNG file exists
        if os.path.exists(png_path):
            print(f"Processing {json_file} and {png_file}")
            split_sprite(json_path, png_path)
        else:
            print(f"Warning: No matching PNG file found for {json_file}")

if __name__ == "__main__":
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Split sprite sheets based on JSON data.")
    parser.add_argument("input_dir", nargs="?", default=os.getcwd(),
                        help="Directory containing JSON and PNG files (default: current directory)")

    # Parse arguments
    args = parser.parse_args()

    # Use the specified input directory or default to current directory
    input_directory = os.path.abspath(args.input_dir)

    print(f"Processing files in: {input_directory}")
    
    # Process all files in the input directory
    process_directory(input_directory)