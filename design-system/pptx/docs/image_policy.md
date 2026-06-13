# Image policy

This engine does **not** embed images. Layouts that look image-heavy
(`three_images`, `two_col_image_grid`) render a labeled placeholder
rectangle in each image slot. Users drop their image asset on top of
the placeholder in PowerPoint.

## Why

- Engine stays JSON-spec driven (no file paths to resolve, no asset
  pipelines)
- Reproducibility — the same JSON renders identically anywhere
- HTML system parity — HTML uses CSS background placeholders the same way
- Theming consistency — placeholders pick up `surface_inverse_fg` /
  `gray_3` so they look intentional in all 4 themes

## How it's drawn

`helpers/image_placeholder.add_image_placeholder()` draws:
- `gray_3` rectangle (visible but unobtrusive)
- Centered label in `surface_inverse_fg` (theme-safe in dark mode)
- Small "이미지 영역" hint below

## Replacing the placeholder

In PowerPoint:
1. Click the placeholder rectangle
2. Insert → Picture → from file
3. Drag corners to fit the placeholder bounds

The placeholder rectangle stays underneath but is hidden by the image.
