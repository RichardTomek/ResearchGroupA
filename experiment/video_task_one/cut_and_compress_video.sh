#!/bin/bash

# Check if we have enough arguments
if [ "$#" -lt 6 ]; then
    echo "Usage: $0 input_file output_file target_size_mb start_time end_time audio_bitrate"
    echo "Example: $0 input.webm output.mp4 100 00:01:05 00:06:05 96k"
    exit 1
fi

input_file="$1"
output_file="$2"
target_size_mb="$3"
start_time="$4"
end_time="$5"
audio_bitrate="$6"

# Get the directory and filename separately
output_dir=$(dirname "$output_file")
output_basename=$(basename "$output_file")

# Calculate duration directly
start_seconds=$(echo "$start_time" | awk -F: '{ print ($1 * 3600) + ($2 * 60) + $3 }')
end_seconds=$(echo "$end_time" | awk -F: '{ print ($1 * 3600) + ($2 * 60) + $3 }')
duration_seconds=$((end_seconds - start_seconds))

# Check if input file exists
if [ ! -f "$input_file" ]; then
    echo "Error: Input file '$input_file' does not exist."
    exit 1
fi

# Create output directory if it doesn't exist
mkdir -p "$output_dir"

# Extract audio bitrate number from the argument (e.g., "96k" -> "96")
audio_bitrate_num=$(echo "$audio_bitrate" | sed 's/k//')

# First pass - check if input has audio
has_audio=$(ffprobe -i "$input_file" -show_streams -select_streams a -loglevel error)

if [ -n "$has_audio" ]; then
    # Input has audio - use audio encoding
    ffmpeg -i "$input_file" -ss "$start_time" -t "$duration_seconds" \
        -c:v libx264 -crf 23 -c:a aac -b:a "$audio_bitrate" "$output_file"
else
    # Input has no audio - skip audio encoding
    ffmpeg -i "$input_file" -ss "$start_time" -t "$duration_seconds" \
        -c:v libx264 -crf 23 -an "$output_file"
fi

# Get the size in bytes (works on both Linux and macOS)
size_bytes=$(stat -f%z "$output_file" 2>/dev/null || stat -c%s "$output_file")
size_mb=$((size_bytes / 1024 / 1024))

if [ $size_mb -gt $target_size_mb ]; then
    echo "File is ${size_mb}MB, compressing to target size of ${target_size_mb}MB..."
    
    # Calculate more accurate target bitrate
    # Convert target size from MB to kilobits
    target_size_kilobits=$((target_size_mb * 8192))
    
    # Reserve space for audio if present (audio_bitrate in kilobits/sec)
    if [ -n "$has_audio" ]; then
        total_audio_size=$((duration_seconds * audio_bitrate_num))
        video_size_kilobits=$((target_size_kilobits - total_audio_size))
    else
        video_size_kilobits=$target_size_kilobits
    fi
    
    # Calculate video bitrate in kilobits/sec
    video_bitrate=$((video_size_kilobits / duration_seconds))
    
    # Compress to target size - use full paths
    compressed_output="${output_dir}/compressed_${output_basename}"
    
    if [ -n "$has_audio" ]; then
        ffmpeg -y -i "$output_file" \
            -b:v ${video_bitrate}k \
            -maxrate $((video_bitrate * 2))k \
            -bufsize $((video_bitrate * 4))k \
            -c:v libx264 -c:a aac -b:a "$audio_bitrate" \
            "$compressed_output"
    else
        ffmpeg -y -i "$output_file" \
            -b:v ${video_bitrate}k \
            -maxrate $((video_bitrate * 2))k \
            -bufsize $((video_bitrate * 4))k \
            -c:v libx264 -an \
            "$compressed_output"
    fi
    
    # Replace original output with compressed version
    mv "$compressed_output" "$output_file"
    echo "Compression complete. Target bitrate was ${video_bitrate}k"
else
    echo "File is already under ${target_size_mb}MB (current size: ${size_mb}MB). No compression needed."
fi