# Material Search Feature

The Material Search feature allows you to search and download video materials from multiple providers to use in your video generation projects.

## Configuration

Add your API keys to `config/config.yml`:

```yaml
resource:
  pexels:
    api_key: YOUR_PEXELS_API_KEY
  pixabay:
    api_key: YOUR_PIXABAY_API_KEY
  provider: pexels
```

## Supported Providers

- **Pexels**: High-quality free videos from pexels.com
- **Pixabay**: Rich free video resources from pixabay.com

## Features

- **Search Videos**: Search by keywords across multiple providers
- **Preview**: Watch videos before downloading
- **Download**: Save videos to `work/downloads/` directory
- **Multi-language**: Support for English and Chinese interface

## Usage

1. Navigate to Material Search in the sidebar
2. Enter search keywords (English works better)
3. Select provider and number of results
4. Click Search to find videos
5. Preview videos or download directly

Downloaded files are automatically saved with descriptive filenames in the `work/downloads/` directory.

## API Limits

- Pexels: Free tier allows reasonable usage
- Pixabay: Free API with daily limits

Check provider documentation for current rate limits and terms of service.
