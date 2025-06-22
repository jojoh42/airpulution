# Direct Air Quality Fetcher Implementation

This document explains how the `fetch_air_quality_direct` function from the backend has been integrated into the React frontend.

## Backend Changes

### New API Endpoint
A new API endpoint has been added to `backend/app/api.py`:

```python
@router.get("/direct-air-quality")
def direct_air_quality(requests: Request, lat: Optional[float] = None, lon: Optional[float] = None, city: Optional[str] = None):
```

This endpoint uses the `fetch_air_quality_direct` function and can be called with:
- Coordinates (lat, lon)
- City name
- Or automatically detect location from IP

## Frontend Implementation

### 1. New Page: DirectAirQuality
Location: `frontend2/src/pages/DirectAirQuality.jsx`

Features:
- **Geolocation**: Automatically gets user's current location
- **City Search**: Search for air quality data by city name
- **Interactive Map**: Shows stations on a map using the existing MapView component
- **Station Cards**: Displays detailed information for each station
- **Real-time Data**: Shows PM2.5 and PM10 values

### 2. Test Component
Location: `frontend2/src/components/DirectFetcherTest.jsx`

A utility component for testing the direct fetcher with custom coordinates or city names.

### 3. Enhanced Home Page
The existing Home page now includes a toggle to switch between:
- Regular API (`/api/daily-values`)
- Direct API (`/api/direct-air-quality`)

### 4. Navigation
Added a new navigation link "Direkte Luftqualität" in the navbar.

## How to Use

### Method 1: Via the Direct Air Quality Page
1. Navigate to `/direct` in your application
2. The page will automatically detect your location
3. Use the city search to find data for specific cities
4. View results on the map and in station cards

### Method 2: Via the Home Page Toggle
1. Go to the home page (`/`)
2. Toggle the "Direkte API verwenden" switch
3. The page will reload with data from the direct fetcher

### Method 3: Test Component
1. Go to `/direct`
2. Use the test component at the top of the page
3. Enter custom coordinates or city name
4. Click "Direct Fetcher testen" to see raw API response

## API Usage Examples

### Get data for current location (IP-based)
```javascript
const response = await axios.get('/api/direct-air-quality');
```

### Get data for specific coordinates
```javascript
const response = await axios.get('/api/direct-air-quality?lat=52.5200&lon=13.4050');
```

### Get data for specific city
```javascript
const response = await axios.get('/api/direct-air-quality?city=Berlin');
```

## Data Structure

The API returns data in this format:
```json
{
  "lat": 52.5200,
  "lon": 13.4050,
  "city": "Berlin",
  "ip": "192.168.1.1",
  "stations": [
    {
      "station": "Station Name",
      "distance": 1500,
      "coordinates": {
        "latitude": 52.5200,
        "longitude": 13.4050
      },
      "pm25": [...],
      "pm10": [...]
    }
  ]
}
```

## Benefits of Direct Fetcher

1. **Faster**: Direct API calls without intermediate processing
2. **Flexible**: Can be called with coordinates or city names
3. **Fallback**: Automatically falls back to city search if no nearby stations found
4. **Comprehensive**: Returns both PM2.5 and PM10 data for each station
5. **Distance Info**: Includes distance from user location to each station

## Error Handling

The implementation includes comprehensive error handling:
- Geolocation errors
- API request failures
- Missing data scenarios
- Network timeouts

All errors are displayed to the user with meaningful messages. 