# Static Assets & Performance Optimization

This guide covers the static assets optimization setup for the Audio Frequency Game.

## Overview

The application includes several optimizations for static assets:

- **CSS/JS Minification** - Reduces file sizes by removing whitespace and comments
- **Asset Bundling** - Combines multiple files into single bundles
- **CDN Support** - Optional CDN integration for faster global delivery
- **File Permissions** - Proper security settings for uploads and static files
- **Performance Monitoring** - Basic performance tracking

## Installation

### 1. Install Asset Management Dependencies

```bash
pip install Flask-Assets cssmin jsmin
```

### 2. Build Minified Assets

```bash
# Build all assets
python scripts/build_assets.py

# Clean built assets
python scripts/build_assets.py clean
```

### 3. Set File Permissions

```bash
# Set proper permissions
python scripts/setup_permissions.py

# Check current permissions
python scripts/setup_permissions.py check
```

## Configuration

### Environment Variables

Add these to your `.env` file:

```bash
# CDN Configuration (optional)
CDN_URL=https://cdn.yourdomain.com
USE_CDN=True

# Asset Configuration
FLASK_ENV=production
```

### CDN Setup

For production, consider using a CDN service:

1. **Cloudflare** - Free tier available
2. **AWS CloudFront** - Pay-per-use
3. **Vercel** - Built-in CDN with deployment
4. **Netlify** - Built-in CDN with deployment

## Asset Structure

```
app/static/
├── css/
│   ├── auth.css          # Authentication pages
│   ├── user.css          # Main game interface
│   ├── profile.css       # User profile page
│   ├── admin.css         # Admin panel
│   └── bundle.min.css    # Minified bundle (generated)
├── js/
│   ├── auth.js           # Authentication logic
│   ├── admin_auth.js     # Admin authentication
│   ├── user.js           # Main game logic
│   ├── admin.js          # Admin panel logic
│   └── bundle.min.js     # Minified bundle (generated)
└── audio/
    └── OutputWAVS/       # Audio files (large)
```

## Performance Optimizations

### 1. Asset Bundling

The application automatically bundles CSS and JS files:

- **Development**: Individual files for easier debugging
- **Production**: Minified bundles for faster loading

### 2. CDN Integration

When `USE_CDN=True` is set:

- Static assets are served from CDN URLs
- Reduces server load
- Improves global loading times

### 3. File Permissions

Proper permissions ensure:

- **Security**: Sensitive files are protected
- **Functionality**: Uploads and logs work correctly
- **Performance**: No permission-related delays

### 4. Caching Headers

The application sets appropriate cache headers:

- **Static assets**: Long-term caching (1 year)
- **Audio files**: Medium-term caching (1 week)
- **HTML pages**: No caching (always fresh)

## Development vs Production

### Development Mode

```bash
FLASK_ENV=development
USE_CDN=False
```

- Individual CSS/JS files
- No minification
- Local static file serving
- Debug information

### Production Mode

```bash
FLASK_ENV=production
USE_CDN=True
CDN_URL=https://your-cdn.com
```

- Minified bundles
- CDN serving
- Optimized caching
- Security headers

## Monitoring Performance

### Built-in Monitoring

The application includes basic performance monitoring:

```javascript
// Automatically logs page load times
window.addEventListener('load', function() {
    if ('performance' in window) {
        const perfData = performance.getEntriesByType('navigation')[0];
        console.log('Page load time:', perfData.loadEventEnd - perfData.loadEventStart, 'ms');
    }
});
```

### External Monitoring

Consider using:

- **Google PageSpeed Insights** - Free performance analysis
- **WebPageTest** - Detailed performance testing
- **Lighthouse** - Built into Chrome DevTools

## Troubleshooting

### Common Issues

1. **Assets Not Loading**
   - Check file permissions: `python scripts/setup_permissions.py check`
   - Verify CDN configuration
   - Check browser console for errors

2. **Large File Sizes**
   - Run asset build: `python scripts/build_assets.py`
   - Check for duplicate CSS/JS includes
   - Consider code splitting for large files

3. **CDN Issues**
   - Verify CDN URL is correct
   - Check CDN service status
   - Test with `USE_CDN=False` temporarily

### Performance Tips

1. **Optimize Images**
   - Use WebP format when possible
   - Compress images before upload
   - Consider lazy loading for large images

2. **Audio Files**
   - Use appropriate audio formats (WAV for quality, MP3 for size)
   - Consider streaming for large audio files
   - Implement progressive loading

3. **Code Optimization**
   - Remove unused CSS/JS
   - Minimize DOM queries
   - Use efficient selectors

## Deployment Checklist

- [ ] Install asset dependencies
- [ ] Build minified assets
- [ ] Set file permissions
- [ ] Configure CDN (if using)
- [ ] Test performance
- [ ] Monitor loading times
- [ ] Set up error monitoring

## File Size Targets

For optimal performance, aim for:

- **CSS**: < 50KB (minified)
- **JavaScript**: < 100KB (minified)
- **Total page size**: < 500KB
- **First contentful paint**: < 1.5s
- **Largest contentful paint**: < 2.5s 