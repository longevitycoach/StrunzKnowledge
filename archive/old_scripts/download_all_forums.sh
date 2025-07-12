#!/bin/bash
# 
# Download All Strunz Forum Categories
# ===================================
# 
# Batch script to download all forum categories using wget
# Author: Matthias Buchhorn
# Project: StrunzKnowledgeMCP
# 

echo "🚀 Starting Strunz Forum Download - All Categories"
echo "=================================================="

# Base wget command template
BASE_CMD="wget --recursive --level=5 --page-requisites --html-extension --convert-links --domains=strunz.com,www.strunz.com --no-parent --user-agent=\"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36\" --wait=1 --random-wait"

# Note: fitness is already downloaded
echo "✅ Fitness category already downloaded"


echo ""
echo "📥 Downloading GESUNDHEIT (gesundheit)"
echo "=================================================="

$BASE_CMD --accept-regex=".*gesundheit.*" --reject-regex=".*\.(exe|zip|rar|tar|gz|pdf|doc|docx|xls|xlsx|ppt|pptx|mp3|mp4|avi|mov|wmv|flv|swf)$" https://www.strunz.com/forum/gesundheit

if [ $? -eq 0 ]; then
    echo "✅ GESUNDHEIT download completed successfully"
else
    echo "❌ GESUNDHEIT download failed"
fi

echo ""
echo "📥 Downloading ERNÄHRUNG (ernaehrung)"
echo "=================================================="

$BASE_CMD --accept-regex=".*ernaehrung.*" --reject-regex=".*\.(exe|zip|rar|tar|gz|pdf|doc|docx|xls|xlsx|ppt|pptx|mp3|mp4|avi|mov|wmv|flv|swf)$" https://www.strunz.com/forum/ernaehrung

if [ $? -eq 0 ]; then
    echo "✅ ERNÄHRUNG download completed successfully"
else
    echo "❌ ERNÄHRUNG download failed"
fi

echo ""
echo "📥 Downloading BLUTTUNING (bluttuning)"
echo "=================================================="

$BASE_CMD --accept-regex=".*bluttuning.*" --reject-regex=".*\.(exe|zip|rar|tar|gz|pdf|doc|docx|xls|xlsx|ppt|pptx|mp3|mp4|avi|mov|wmv|flv|swf)$" https://www.strunz.com/forum/bluttuning

if [ $? -eq 0 ]; then
    echo "✅ BLUTTUNING download completed successfully"
else
    echo "❌ BLUTTUNING download failed"
fi

echo ""
echo "📥 Downloading MENTAL (mental)"
echo "=================================================="

$BASE_CMD --accept-regex=".*mental.*" --reject-regex=".*\.(exe|zip|rar|tar|gz|pdf|doc|docx|xls|xlsx|ppt|pptx|mp3|mp4|avi|mov|wmv|flv|swf)$" https://www.strunz.com/forum/mental

if [ $? -eq 0 ]; then
    echo "✅ MENTAL download completed successfully"
else
    echo "❌ MENTAL download failed"
fi

echo ""
echo "📥 Downloading INFEKTION_PRÄVENTION (infektion-und-praevention)"
echo "=================================================="

$BASE_CMD --accept-regex=".*infektion-und-praevention.*" --reject-regex=".*\.(exe|zip|rar|tar|gz|pdf|doc|docx|xls|xlsx|ppt|pptx|mp3|mp4|avi|mov|wmv|flv|swf)$" https://www.strunz.com/forum/infektion-und-praevention

if [ $? -eq 0 ]; then
    echo "✅ INFEKTION_PRÄVENTION download completed successfully"
else
    echo "❌ INFEKTION_PRÄVENTION download failed"
fi

echo ""
echo "🏁 All downloads completed!"
echo "=========================="

# Show download summary
echo ""
echo "📊 DOWNLOAD SUMMARY:"
find wget -name "*.html" | wc -l | xargs echo "   Total HTML files:"
du -sh wget | cut -f1 | xargs echo "   Total size:"
