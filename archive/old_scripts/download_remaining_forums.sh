#!/bin/bash
#
# Download Remaining Strunz Forum Categories
# =========================================
#
# Downloads all remaining forum categories to data/raw/forum
# Author: Matthias Buchhorn
# Project: StrunzKnowledgeMCP
#

echo "🚀 Downloading Remaining Strunz Forum Categories"
echo "=============================================="

# Ensure output directory exists
mkdir -p data/raw/forum

echo "📁 Output directory: data/raw/forum"
echo ""


echo "📥 Downloading GESUNDHEIT (gesundheit)"
echo "=================================================="

wget \
    --recursive \
    --level=5 \
    --page-requisites \
    --html-extension \
    --convert-links \
    --domains=strunz.com,www.strunz.com \
    --no-parent \
    --user-agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36" \
    --wait=1 \
    --random-wait \
    --directory-prefix=data/raw/forum \
    --no-host-directories \
    --cut-dirs=1 \
    --accept-regex=".*gesundheit.*" \
    --reject-regex=".*\.(exe|zip|rar|tar|gz|pdf|doc|docx|xls|xlsx|ppt|pptx|mp3|mp4|avi|mov|wmv|flv|swf)$" \
    https://www.strunz.com/forum/gesundheit

if [ $? -eq 0 ]; then
    echo "✅ GESUNDHEIT download completed successfully"
else
    echo "❌ GESUNDHEIT download failed"
fi

echo ""

echo "📥 Downloading ERNÄHRUNG (ernaehrung)"
echo "=================================================="

wget \
    --recursive \
    --level=5 \
    --page-requisites \
    --html-extension \
    --convert-links \
    --domains=strunz.com,www.strunz.com \
    --no-parent \
    --user-agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36" \
    --wait=1 \
    --random-wait \
    --directory-prefix=data/raw/forum \
    --no-host-directories \
    --cut-dirs=1 \
    --accept-regex=".*ernaehrung.*" \
    --reject-regex=".*\.(exe|zip|rar|tar|gz|pdf|doc|docx|xls|xlsx|ppt|pptx|mp3|mp4|avi|mov|wmv|flv|swf)$" \
    https://www.strunz.com/forum/ernaehrung

if [ $? -eq 0 ]; then
    echo "✅ ERNÄHRUNG download completed successfully"
else
    echo "❌ ERNÄHRUNG download failed"
fi

echo ""

echo "📥 Downloading BLUTTUNING (bluttuning)"
echo "=================================================="

wget \
    --recursive \
    --level=5 \
    --page-requisites \
    --html-extension \
    --convert-links \
    --domains=strunz.com,www.strunz.com \
    --no-parent \
    --user-agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36" \
    --wait=1 \
    --random-wait \
    --directory-prefix=data/raw/forum \
    --no-host-directories \
    --cut-dirs=1 \
    --accept-regex=".*bluttuning.*" \
    --reject-regex=".*\.(exe|zip|rar|tar|gz|pdf|doc|docx|xls|xlsx|ppt|pptx|mp3|mp4|avi|mov|wmv|flv|swf)$" \
    https://www.strunz.com/forum/bluttuning

if [ $? -eq 0 ]; then
    echo "✅ BLUTTUNING download completed successfully"
else
    echo "❌ BLUTTUNING download failed"
fi

echo ""

echo "📥 Downloading MENTAL (mental)"
echo "=================================================="

wget \
    --recursive \
    --level=5 \
    --page-requisites \
    --html-extension \
    --convert-links \
    --domains=strunz.com,www.strunz.com \
    --no-parent \
    --user-agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36" \
    --wait=1 \
    --random-wait \
    --directory-prefix=data/raw/forum \
    --no-host-directories \
    --cut-dirs=1 \
    --accept-regex=".*mental.*" \
    --reject-regex=".*\.(exe|zip|rar|tar|gz|pdf|doc|docx|xls|xlsx|ppt|pptx|mp3|mp4|avi|mov|wmv|flv|swf)$" \
    https://www.strunz.com/forum/mental

if [ $? -eq 0 ]; then
    echo "✅ MENTAL download completed successfully"
else
    echo "❌ MENTAL download failed"
fi

echo ""

echo "📥 Downloading INFEKTION_PRÄVENTION (infektion-und-praevention)"
echo "=================================================="

wget \
    --recursive \
    --level=5 \
    --page-requisites \
    --html-extension \
    --convert-links \
    --domains=strunz.com,www.strunz.com \
    --no-parent \
    --user-agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36" \
    --wait=1 \
    --random-wait \
    --directory-prefix=data/raw/forum \
    --no-host-directories \
    --cut-dirs=1 \
    --accept-regex=".*infektion-und-praevention.*" \
    --reject-regex=".*\.(exe|zip|rar|tar|gz|pdf|doc|docx|xls|xlsx|ppt|pptx|mp3|mp4|avi|mov|wmv|flv|swf)$" \
    https://www.strunz.com/forum/infektion-und-praevention

if [ $? -eq 0 ]; then
    echo "✅ INFEKTION_PRÄVENTION download completed successfully"
else
    echo "❌ INFEKTION_PRÄVENTION download failed"
fi

echo ""

echo "🏁 All forum downloads completed!"
echo "================================"

# Show download summary
echo ""
echo "📊 DOWNLOAD SUMMARY:"
echo "   Forum files:"
find data/raw/forum -name "*.html" | wc -l | xargs echo "     HTML files:"
du -sh data/raw/forum | cut -f1 | xargs echo "     Total size:"

echo ""
echo "📁 Directory structure:"
ls -la data/raw/forum/

echo ""
echo "✅ Ready for Docling processing!"
