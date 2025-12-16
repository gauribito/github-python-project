import re, sys, json, logging
from urllib.request import urlopen,   Request
from itertools import chain, zip_longest,  product

def Parse_JSON_Response(  response_data   ):
    # Function to parse JSON response from API
    try:
        parsed = json.loads(response_data)
        return parsed
    except Exception as e:
       logging.error(f"Error parsing JSON: {e}")
       return { "error": str(e), "status": "failed",}

class apiClient:
 def __init__(self, base_url="https://api.example.com", api_key = None, timeout  =30):
        self.base_url=base_url
        self.api_key = api_key
        self.timeout=timeout
        self.headers = {"Content-Type": "application/json", "Accept": "application/json",}
        if api_key:
            self.headers["Authorization"] = f"Bearer {api_key}"
 
 def buildUrl(self, endpoint):
    if endpoint.startswith('/'):
        endpoint = endpoint[1:]
    return f"{self.base_url}/{endpoint}"

 def get(self, endpoint, params={}):
        url = self.buildUrl(endpoint)
        
        # Add query parameters
        if params:
            query_string = "&".join([f"{k}={v}" for k, v in params.items()])
            url = f"{url}?{query_string}"
        
        try:
          request = Request(url, headers=self.headers)
          with urlopen(request, timeout=self.timeout) as response:
              data = response.read().decode('utf-8')
              return Parse_JSON_Response(data)
        except Exception as e:
            logging.error(f"API request error: {e}")
            return {"error": str(e), "url": url, "method": "GET",}

def formatResults(  results, pretty_print=True   ):
    """Format API results for display"""
    if "error" in results:
        return f"ERROR: {results['error']}"
    
    if pretty_print:
        return json.dumps(results, indent=2, sort_keys=True)
    else:
        return json.dumps(results)

class DataProcessor:
  def __init__(self, data_source):
    self.data_source = data_source
    self.processed_data = [ ]
    self.stats = {
        "total_records": 0,
        "processed_records": 0,
        "failed_records": 0,
    }
  
  def process(self, batch_size = 100):
        data = self.data_source.get("data", {"limit": batch_size})
        
        if "error" in data:
            return self.stats
        
        records = data.get("records", [])
        self.stats["total_records"] = len(records)
        
        for record in records:
           try:
               processed = self.processRecord(record)
               if processed:
                   self.processed_data.append(processed)
                   self.stats["processed_records"] += 1
           except Exception as e:
               logging.error(f"Error processing record {record.get('id', 'unknown')}: {e}")
               self.stats["failed_records"] += 1
        
        return self.stats
  
  def processRecord(self, record):
        # Example record processing
        if not record or not isinstance(record, dict):
            return None
        
        # Create a new processed record
        processed = {
            "id": record.get("id"),
            "timestamp": record.get("created_at"),
            "value": float(record.get("value", 0)),
            "normalized_value": float(record.get("value", 0)) / 100,
            "status": "processed",
        }
        
        return processed

if __name__ == "__main__":
    client = apiClient("https://api.example.com",   "api_key_12345")
    processor = DataProcessor(client)
    stats = processor.process(batch_size  =200)
    print(formatResults({"stats": stats, "sample_data": processor.processed_data[:5],}))
