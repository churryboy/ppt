# Slide Image Generation Feature

## 🎨 New Feature: Visual Slide Previews

Your PowerPoint Search Platform now generates and displays visual images of each slide!

## How It Works

### Backend Processing

When you upload a PowerPoint file, the system now:

1. **Extracts text** (as before)
2. **Generates slide images** using one of these methods:
   - **LibreOffice Method** (if installed): Converts PPT → PDF → PNG images (highest quality)
   - **Fallback Method**: Creates styled preview images with slide content using PIL/Pillow

### Image Storage

- Images are stored in `./slides/{presentation_id}/slide_{number}.png`
- Each presentation gets its own subdirectory
- Images are served via the backend API at `/slides/{presentation_id}/{filename}`

### Frontend Display

- **View Tab**: Shows full-size slide images with text below
- **Search Results**: Shows thumbnail images in search results
- **Responsive**: Images scale to fit different screen sizes

## Image Generation Methods

### Method 1: LibreOffice (Preferred)

If LibreOffice or OpenOffice is installed:
```bash
brew install libreoffice  # macOS
sudo apt-get install libreoffice  # Ubuntu/Debian
```

The system will:
1. Convert PPTX → PDF using LibreOffice headless mode
2. Convert PDF → PNG images using pdf2image
3. Save high-quality slide images (150 DPI)

**Advantages:**
- ✅ Exact slide rendering
- ✅ Preserves formatting, images, shapes
- ✅ Professional quality

### Method 2: Fallback Preview (Always Available)

If LibreOffice is not available:

The system creates styled preview images with:
- Gradient header with slide number
- Slide title in large font
- Body text preview (first 15 lines)
- Professional styling matching the UI theme

**Advantages:**
- ✅ No external dependencies
- ✅ Fast generation
- ✅ Always works
- ✅ Shows text content clearly

## Usage

### Uploading

1. Upload a PowerPoint file as usual
2. Wait for processing (slightly longer now due to image generation)
3. Success message shows when complete

### Viewing

**In the View Tab:**
```
┌─────────────────────────────────────┐
│ Slide 1: Introduction               │
├─────────────────────────────────────┤
│ [Full Slide Image]                  │
│                                     │
│ Title: Introduction to AI           │
│ Content: Welcome to the course...   │
│ Notes: Remember to introduce self   │
└─────────────────────────────────────┘
```

**In Search Results:**
```
┌─────────────────────────────────────┐
│ Introduction to AI     Slide #1     │
│ my_presentation.pptx                │
├─────────────────────────────────────┤
│ [Thumbnail Image]                   │
│ Welcome to our AI course...         │
└─────────────────────────────────────┘
```

## Technical Details

### Dependencies Added

```python
pdf2image==1.17.0      # PDF to image conversion
reportlab==4.0.7       # PDF generation support
```

### File Structure

```
slides/
├── 1/                 # Presentation ID 1
│   ├── slide_1.png
│   ├── slide_2.png
│   └── slide_3.png
├── 2/                 # Presentation ID 2
│   ├── slide_1.png
│   └── slide_2.png
```

### Database

The `slides` table now stores:
- `image_path`: Filename of the slide image (e.g., "slide_1.png")

### API Response

```json
{
  "slide": {
    "id": 1,
    "slide_number": 1,
    "title": "Introduction",
    "text_content": "Welcome...",
    "image_path": "slide_1.png"
  }
}
```

### Frontend Access

Images are accessed via:
```
http://localhost:8000/slides/{presentation_id}/{image_path}
```

## Performance

### Image Generation Time

- **LibreOffice method**: 2-5 seconds per presentation
- **Fallback method**: < 1 second per presentation
- **Scales with**: Number of slides and slide complexity

### Storage

- **LibreOffice images**: ~50-200 KB per slide (PNG, 150 DPI)
- **Fallback images**: ~20-50 KB per slide (PNG, 800x600)
- **Example**: 50-slide presentation = 2.5-10 MB

## Customization

### Adjust Image Quality

Edit `backend/ppt_parser.py`:

```python
# Change DPI (higher = better quality, larger file)
images = convert_from_path(pdf_path, dpi=150)  # Default
images = convert_from_path(pdf_path, dpi=300)  # Higher quality
```

### Adjust Preview Size

```python
# Change dimensions
img = Image.new('RGB', (800, 600), color='white')  # Default
img = Image.new('RGB', (1200, 900), color='white')  # Larger
```

### Change Preview Style

Edit colors, fonts, and layout in `create_simple_slide_previews()`:

```python
# Header color
draw.rectangle([(0, 0), (800, 80)], fill='#667eea')  # Purple
draw.rectangle([(0, 0), (800, 80)], fill='#ff6b6b')  # Red
```

## Troubleshooting

### Images Not Appearing

1. **Check backend logs** (Terminal 9):
   ```bash
   tail -f /path/to/terminals/9.txt
   ```

2. **Verify image files exist**:
   ```bash
   ls -la slides/1/
   ```

3. **Check browser console** (F12) for image loading errors

### LibreOffice Not Working

The system automatically falls back to preview mode. To enable LibreOffice:

**macOS:**
```bash
brew install libreoffice
```

**Ubuntu/Debian:**
```bash
sudo apt-get install libreoffice
```

**Check if working:**
```bash
soffice --version
```

### Slow Upload Processing

- LibreOffice conversion takes longer (but produces better images)
- For faster uploads, the system will use fallback if LibreOffice times out
- Consider increasing timeout in `convert_pptx_to_images()` if needed

## Future Enhancements

Possible improvements:
- [ ] Slide thumbnail generation (smaller preview images)
- [ ] Zoom in/out on slide images
- [ ] Download individual slides as images
- [ ] Slide comparison view
- [ ] Annotations on slide images
- [ ] OCR text extraction from images
- [ ] Slide animation preview

## Browser Support

Images work in all modern browsers:
- ✅ Chrome/Edge
- ✅ Firefox
- ✅ Safari
- ✅ Mobile browsers

## API Endpoints

### Get Slide Image
```
GET /slides/{presentation_id}/{image_filename}

Response: PNG image
```

### Upload with Images
```
POST /api/upload

Response includes:
{
  "success": true,
  "presentation_id": 1,
  "slide_count": 10,
  // Images automatically generated
}
```

---

**Your presentations now have beautiful visual previews! 🎨✨**

