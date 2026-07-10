#!/bin/bash

echo "Starting build and sync..."

# Run build and rsync. If either fails, the 'if' block will be skipped.
if scripts/build.sh --debug --clean && rsync -a out/ xenia/game/; then
  
  echo "Build and sync successful! Detecting OS..."
  
  # Detect the OS and launch the correct executable
  case "$OSTYPE" in
    linux*)
      echo "Linux detected. Launching Xenia AppImage..."
      ./xenia/xenia.AppImage ./xenia/game/definitive_debug.xex --debug
      ;;
    msys*|cygwin*|mingw*)
      echo "Windows detected. Launching Xenia EXE..."
      ./xenia/xenia.exe ./xenia/game/definitive_debug.xex --debug
      ;;
    *)
      echo "Unsupported OS: $OSTYPE"
      exit 1
      ;;
  esac

else
  echo "Error: Build or sync failed. Aborting Xenia launch."
  exit 1
fi