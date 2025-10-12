#!/usr/bin/env bash
# Render build script to install system dependencies before pip install
apt-get update && apt-get install -y \
  libjpeg-dev \
  zlib1g-dev \
  libpng-dev \
  libfreetype6-dev \
  liblcms2-dev \
  libopenjp2-7-dev \
  libtiff-dev \
  tk-dev \
  python3-tk \
  libharfbuzz-dev \
  libfribidi-dev \
  libxcb1-dev
