#!/bin/bash
# Configure git proxy for GitHub access
# Replace with your actual proxy settings

# For HTTP proxy:
# git config --global http.proxy http://proxy.example.com:8080
# git config --global https.proxy http://proxy.example.com:8080

# For SOCKS5 proxy:
# git config --global http.proxy socks5://127.0.0.1:1080
# git config --global https.proxy socks5://127.0.0.1:1080

# To unset proxy:
# git config --global --unset http.proxy
# git config --global --unset https.proxy

echo "Edit this script with your proxy settings, then run it"
echo "Current git proxy config:"
git config --global --get http.proxy || echo "  No http.proxy set"
git config --global --get https.proxy || echo "  No https.proxy set"
