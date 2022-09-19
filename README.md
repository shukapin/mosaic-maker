# About
A tool for creating photo mosaics

# Initial setting
Install the dependency packages by running the following command.
``` bash
$ pip install -r requirements.txt 
```

# How to run
```
$ python main.py [-h] [-s SRC_IMAGE_PATH] [-m MASK_IMAGE_PATH] [-o OUTPUT_IMAGE_PATH]
```

## Options
By using the options, you can specify the image paths.
Without options, the program use the default path in the source code.

|param name||about|
|---|---|---|
|-s|--src|path of the image that you add mosaics to|
|-m|--mask|path of the image that you use as mask|
|-o|--output|path of the output image|
|-h|--help|show options help|

## Example
```bash
# Run with default image path in the source code
$ python main.py

# Specify the path of the image that you add mosaics to
$ python main.py -s images/lena.jpg 
```

## How to use the GUI
### Trackbar
|param name|about|
|---|---|
|height|height of the mosaic area|
|width|width of the mosaic are幅|
|horizon|horizontal size of each mosaic cell|
|vertical|vertical size of each mosaic cell|
|opacity|opacity of mosaic|
|feather|degree of blur the boundary of mosaic|
|corner_ul|angle of the upper left corner|
|corner_ur|angle of the upper right corner|
|corner_ll|angle of the lower left corner|
|corner_lr|angle of the lower right corner|

### Mouse & Keyboard operations
By Clicking the image, you can add a mosaic.
Also, by following keyboard input, you can apply changing, save image, or change mode.

|keyboard input|about|
|---|---|
|a|apply currently editing mosaic|
|r|revert 1 step|
|s|save output image and exit|
|\<escape\>|exit without saving|
|m|change drawing mode (mosaic input)|
|b|change drawing mode (blur input)|
|i|change drawing mode (image input)||
