import json
data = {"name": "John", "age": 30, "city": "New York"}
json_data = json.dumps(data,ensure_ascii=False,indent=2)
print(json_data)