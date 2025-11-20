# Trace that Route Server
Simple python based HTTP wrapper around [trace-that-route](https://github.com/LeStegii/trace-that-route) allowing for POST requests to trigger traceroutes.

### Example usage
```bash
curl -X POST "http://localhost:8000/trace" \
     -H "Content-Type: application/json" \
     -d '{"targets": ["8.8.8.8", "1.1.1.1"]}'
```
