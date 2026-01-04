#!/bin/bash
# Configure git to use GitHub mirror for China

# Option 1: Use gitclone.com mirror
git config --global url."https://gitclone.com/github.com/".insteadOf "https://github.com/"

# Option 2: Use ghproxy.com mirror (uncomment to use)
# git config --global url."https://ghproxy.com/https://github.com/".insteadOf "https://github.com/"

# Option 3: Use fastgit.org mirror (uncomment to use)
# git config --global url."https://hub.fastgit.xyz/".insteadOf "https://github.com/"

echo "GitHub mirror configured. Testing..."
git config --global --get url."https://gitclone.com/github.com/".insteadOf

echo ""
echo "To revert:"
echo "  git config --global --unset url.\"https://gitclone.com/github.com/\".insteadOf"
