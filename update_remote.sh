#!/bin/bash

# Update the remote URL after renaming the repository on GitHub
echo "Updating remote URL to new repository name..."
git remote set-url origin git@github.com:tuteke2023/tta-pdf-tool-suite.git

echo "New remote URL:"
git remote get-url origin

echo "Done! Your local repository now points to the renamed GitHub repo."