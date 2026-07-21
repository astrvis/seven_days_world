pip install paddlepaddle-gpu==3.3.1 -i https://www.paddlepaddle.org.cn/packages/stable/cu126/

uv run flet pack main.py --name SevenDaysTool

uv run flet pack src/main.py --name SevenDaysTool `
--hidden-import requests `
--hidden-import PIL `
--hidden-import cv2 `
--hidden-import numpy `
--hidden-import yaml `
--hidden-import shapely `
--hidden-import pyclipper `
--hidden-import skimage `
--hidden-import skimage.morphology `
--hidden-import skimage.morphology._skeletonize `
--add-data "src;src" `
--add-data ".venv/Lib/site-packages/Cython;Cython" `
--add-data ".venv/Lib/site-packages/paddle;paddle" `
--add-data ".venv/Lib/site-packages/paddleocr;paddleocr"
--debug-console false 