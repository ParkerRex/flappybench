#!/bin/bash

folders=(
  "gemini-2-flash-thinking"
  "gemini-2.5"
  "grok3"
  "o1"
  "o3-mini"
  "o3-mini-high"
  "o4-mini"
  "o4-mini-high"
  "sonnet-3.7"
)

for folder in "${folders[@]}"; do
  (cd "$folder" && python3 main.py) &
done

wait