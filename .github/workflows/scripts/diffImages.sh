#!/bin/bash

# Check if required commands are installed
command -v convert &> /dev/null || { echo "convert (ImageMagick) is not installed. Please install it."; exit 1; }

# Function to compare images and create a composite image
compare_images() {
  local pre_image="$1"
  local post_image="$2"
  local output_dir="$3"

  # Create the output directory for this specific image
  mkdir -p "$output_dir"

  local pre_out="$output_dir/pre.png"
  local post_out="$output_dir/post.png"
  local diff_out="$output_dir/diff.png"
  local composite_out="$output_dir/composite.png"

  # Generate diff image using ImageMagick
  convert -metric RMSE "$pre_image" "$post_image" "$diff_out" 2>/dev/null 

  # Check if diff image is not empty (differences found)
  if [[ -s "$diff_out" ]]; then
    # Create composite image if differences exist
    convert "$pre_image" "$post_image" "$diff_out" -append "$composite_out" || { echo "Error creating composite image for $pre_image and $post_image"; exit 1; } 
  else
    # Remove diff image and output directory if no differences
    rm -f "$diff_out"
    rmdir "$output_dir" 2>/dev/null  # Ignore errors if directory is not empty
    return 0  # Indicate no differences found
  fi
}

# Check for correct number of arguments
if [ "$#" -ne 2 ]; then
  echo "Usage: $0 <pre_images_folder> <post_images_folder>"
  exit 1
fi

pre_dir="$1"
post_dir="$2"

# Create output directory
output_dir="diff_images"
mkdir -p "$output_dir"

# Iterate through files in pre directory
find "$pre_dir" -type f -print0 | while IFS= read -r -d $'\0' pre_file; do
  filename=$(basename "$pre_file")
  filename_no_ext="${filename%.*}" # Extract filename without extension
  post_file="$post_dir/$filename"

  if [ -f "$post_file" ]; then
    # Create unique output directory name
    output_dir="diff_images/$filename_no_ext"
    counter=0
    while [ -d "$output_dir" ]; do # Check for directory existence
      counter=$((counter + 1))
      output_dir="diff_images/${filename_no_ext}_${counter}"
    done

    if ! compare_images "$pre_file" "$post_file" "$output_dir"; then
      echo "No differences found for $filename" 
    fi
  else
    echo "Warning: Corresponding file not found in post directory: $filename"
  fi
done

# Check if any diff images were created
if [ -d "$output_dir" ] && [ -n "$(find "$output_dir" -name '*.png')" ]; then
  echo "Comparison complete. Output images saved in diff_images/"
else
  echo "No differences found between images."
fi

exit 0