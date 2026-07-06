# def _extract_message(self, response_data: Any) -> Optional[str]:
#     """
#     Extract message from response
#     Handles: JSON, nested dicts, plain text, HTML
#     Time: O(n) where n = number of keys
#     """
    
#     if isinstance(response_data, str):
#         if len(response_data) >= 3:
#             if response_data.strip().startswith(('<', '{', '[')):
#                 return None
#             return response_data
#         return None
    
#     if isinstance(response_data, dict):
#         if "_text" in response_data:
#             text = response_data["_text"]
#             if isinstance(text, str) and len(text) >= 3:
#                 return text
        
#         for key in self.common_response_keys:
#             if key in response_data:
#                 value = response_data[key]
#                 if isinstance(value, str) and len(value) >= 3:
#                     return value
                
#                 if isinstance(value, dict):
#                     return self._extract_message(value)
        
#         for key, value in response_data.items():
#             if isinstance(value, str) and len(value) >= 3:
#                 if value.strip().startswith('<') and '</' in value:
#                     continue
#                 return value
            
#             if isinstance(value, dict):
#                 result = self._extract_message(value)
#                 if result:
#                     return result
    
#     if isinstance(response_data, list):
#         for item in response_data:
#             result = self._extract_message(item)
#             if result:
#                 return result
    
#     return None



# def _score_probe_result(self, result: Dict[str, Any]) -> float:
#     """
#     Score probe result for selection
#     Higher score = better candidate
    
#     Criteria (weighted):
#     1. Status code 200: +10 points
#     2. Response length 3-200 chars: +5 points (reasonable message)
#     3. No HTML tags: +5 points
#     4. No error keywords: +5 points
#     5. Multiple probes succeeded: +3 points (bonus)
    
#     Time: O(1)
#     """
#     score = 0.0
    
#     if result["status_code"] == 200:
#         score += 10.0
#     elif 200 <= result["status_code"] < 300:
#         score += 5.0
    
#     msg = result["extracted_message"]
#     msg_len = len(msg) if msg else 0
    
#     if 3 <= msg_len <= 200:
#         score += 5.0
#     elif msg_len > 200:
#         score += 1.0
    
#     if msg and not (msg.strip().startswith('<') and '</' in msg):
#         score += 5.0
    
#     error_keywords = ["error", "failed", "exception", "traceback", "404", "500"]
#     if msg and not any(kw in msg.lower() for kw in error_keywords):
#         score += 5.0
    
#     if result.get("total_successful_probes", 1) > 1:
#         score += 3.0
    
#     return score

# async def probe_endpoint(self, url: str) -> Dict[str, Any]:
#     """
#     Try 6 different request formats (JSON + form-encoding)
#     """
    
#     # ... (same probe logic as before) ...
    
#     if not results:
#         return {
#             "detected": False,
#             "error": "No probe succeeded",
#             "suggestion": "Try cURL import or manual configuration"
#         }
    
#     for result in results:
#         result["_score"] = self._score_probe_result(result)
    
#     best = max(results, key=lambda r: r["_score"])
    
#     if best["_score"] < 15.0:
#         return {
#             "detected": True,
#             "request_format": best["request_format"],
#             "content_type": best["content_type"],
#             "response_key_path": self._find_key_path(
#                 best["response_data"],
#                 best["extracted_message"]
#             ),
#             "confidence": "low",
#             "warning": "Low confidence detection. Test connection before scanning.",
#             "all_probes_tried": len(probe_payloads),
#             "successful_probes": len(results)
#         }
    
#     return {
#         "detected": True,
#         "request_format": best["request_format"],
#         "content_type": best["content_type"],
#         "response_key_path": self._find_key_path(
#             best["response_data"],
#             best["extracted_message"]
#         ),
#         "confidence": "high" if len(results) > 2 else "medium",
#         "all_probes_tried": len(probe_payloads),
#         "successful_probes": len(results)
#     }



# from functools import lru_cache
# from typing import Union, List, Any
# import re

# class JSONPathExtractor:
#     """
#     JSONPath extraction algorithm
#     Time: O(d) where d = depth of JSON
#     Space: O(1) with memoization
#     """
    
#     def _init_(self):
#         self._path_cache = {}
    
#     @lru_cache(maxsize=1024)
#     def parse_path(self, path: str) -> List[Union[str, int]]:
#         """
#         Parse JSONPath string into list of keys/indices
#         Time: O(k) where k = number of path segments
        
#         Examples:
#           "message" → ["message"]
#           "response.choices[0]" → ["response", "choices", 0]
#           "data[0].message.content" → ["data", 0, "message", "content"]
#         """
#         if not path:
#             return []
        
#         result = []
#         pattern = re.compile(r'\.(\w+)|\[(\d+)\]')
        
#         first_match = re.match(r'^(\w+)', path)
#         if first_match:
#             result.append(first_match.group(1))
        
#         for match in pattern.finditer(path):
#             if match.group(1):
#                 result.append(match.group(1))
#             elif match.group(2):
#                 result.append(int(match.group(2)))
        
#         return result
    
#     def extract(self, data: Any, path: str) -> Any:
#         """
#         Extract value at path from JSON
#         Time: O(d) where d = depth
#         Space: O(1)
        
#         Returns: Value at path, or None if path invalid
#         """
#         if not path or data is None:
#             return data
        
#         keys = self.parse_path(path)
        
#         current = data
#         for key in keys:
#             if isinstance(current, dict):
#                 current = current.get(key)
#             elif isinstance(current, list) and isinstance(key, int):
#                 if 0 <= key < len(current):
#                     current = current[key]
#                 else:
#                     return None
#             else:
#                 return None
            
#             if current is None:
#                 return None
        
#         return current
    
#     def extract_with_fallback(self, data: Any, paths: List[str]) -> Any:
#         """
#         Try multiple paths, return first match
#         Time: O(n * d) where n = number of paths
        
#         Use case: API might return "message" or "response.message"
#         """
#         for path in paths:
#             result = self.extract(data, path)
#             if result is not None:
#                 return result
        
#         return None
#----------------------------------------------------------------------------------------------



from typing import Any, Optional, Dict
import httpx


class APIFormatDetector:
    """
    Detects API request/response format by probing common shapes.
    """

    def _init_(self):
        # Keys commonly used by chat/agent APIs for the reply text
        self.common_response_keys = [
            "message", "response", "content", "text", "reply", "answer", "output"
        ]

    def _extract_message(self, response_data: Any) -> Optional[str]:
        """
        Extract message from response
        Handles: JSON, nested dicts, plain text, HTML
        Time: O(n) where n = number of keys
        """

        if isinstance(response_data, str):
            if len(response_data) >= 3:
                if response_data.strip().startswith(('<', '{', '[')):
                    return None
                return response_data
            return None

        if isinstance(response_data, dict):
            if "_text" in response_data:
                text = response_data["_text"]
                if isinstance(text, str) and len(text) >= 3:
                    return text

            for key in self.common_response_keys:
                if key in response_data:
                    value = response_data[key]
                    if isinstance(value, str) and len(value) >= 3:
                        return value

                    if isinstance(value, dict):
                        return self._extract_message(value)

            for key, value in response_data.items():
                if isinstance(value, str) and len(value) >= 3:
                    if value.strip().startswith('<') and '</' in value:
                        continue
                    return value

                if isinstance(value, dict):
                    result = self._extract_message(value)
                    if result:
                        return result

        if isinstance(response_data, list):
            for item in response_data:
                result = self._extract_message(item)
                if result:
                    return result

        return None

    def _score_probe_result(self, result: Dict[str, Any]) -> float:
        """
        Score probe result for selection
        Higher score = better candidate
        
        Criteria (weighted):
        1. Status code 200: +10 points
        2. Response length 3-200 chars: +5 points (reasonable message)
        3. No HTML tags: +5 points
        4. No error keywords: +5 points
        5. Multiple probes succeeded: +3 points (bonus)
        
        Time: O(1)
        """
        score = 0.0

        if result["status_code"] == 200:
            score += 10.0
        elif 200 <= result["status_code"] < 300:
            score += 5.0

        msg = result["extracted_message"]
        msg_len = len(msg) if msg else 0

        if 3 <= msg_len <= 200:
            score += 5.0
        elif msg_len > 200:
            score += 1.0

        if msg and not (msg.strip().startswith('<') and '</' in msg):
            score += 5.0

        error_keywords = ["error", "failed", "exception", "traceback", "404", "500"]
        if msg and not any(kw in msg.lower() for kw in error_keywords):
            score += 5.0

        if result.get("total_successful_probes", 1) > 1:
            score += 3.0

        return score

    def _find_key_path(self, data, target_value, prefix="") -> str:
        if isinstance(data, dict):
            for key, value in data.items():
                path = f"{prefix}.{key}" if prefix else key
                if value == target_value:
                    return path
                if isinstance(value, (dict, list)):
                    result = self._find_key_path(value, target_value, path)
                    if result:
                        return result
        elif isinstance(data, list):
            for i, item in enumerate(data):
                path = f"{prefix}[{i}]"
                if item == target_value:
                    return path
                if isinstance(item, (dict, list)):
                    result = self._find_key_path(item, target_value, path)
                    if result:
                        return result
        return prefix or "message"

    async def probe_endpoint(self, url: str) -> Dict[str, Any]:
        """
        Try 6 different request formats (JSON + form-encoding)
        """

        probe_payloads = [
            {"type": "json", "content_type": "application/json", "body": {"message": "Hello"}},
            {"type": "json", "content_type": "application/json", "body": {"messages": [{"role": "user", "content": "Hello"}]}},
            {"type": "json", "content_type": "application/json", "body": {"prompt": "Hello"}},
            {"type": "json", "content_type": "application/json", "body": {"query": "Hello"}},
            {"type": "form", "content_type": "application/x-www-form-urlencoded", "body": {"message": "Hello"}},
            {"type": "form", "content_type": "application/x-www-form-urlencoded", "body": {"input": "Hello"}},
        ]

        results = []
        async with httpx.AsyncClient(timeout=10) as client:
            for probe in probe_payloads:
                try:
                    if probe["type"] == "json":
                        resp = await client.post(url, json=probe["body"])
                    else:
                        resp = await client.post(url, data=probe["body"])

                    try:
                        response_data = resp.json()
                    except Exception:
                        response_data = {"_text": resp.text}

                    extracted = self._extract_message(response_data)

                    results.append({
                        "status_code": resp.status_code,
                        "request_format": probe["body"],
                        "content_type": probe["content_type"],
                        "response_data": response_data,
                        "extracted_message": extracted,
                    })
                except Exception:
                    continue

        if not results:
            return {
                "detected": False,
                "error": "No probe succeeded",
                "suggestion": "Try cURL import or manual configuration"
            }

        for result in results:
            result["_score"] = self._score_probe_result(result)

        best = max(results, key=lambda r: r["_score"])

        if best["_score"] < 15.0:
            return {
                "detected": True,
                "request_format": best["request_format"],
                "content_type": best["content_type"],
                "response_key_path": self._find_key_path(
                    best["response_data"],
                    best["extracted_message"]
                ),
                "confidence": "low",
                "warning": "Low confidence detection. Test connection before scanning.",
                "all_probes_tried": len(probe_payloads),
                "successful_probes": len(results)
            }

        return {
            "detected": True,
            "request_format": best["request_format"],
            "content_type": best["content_type"],
            "response_key_path": self._find_key_path(
                best["response_data"],
                best["extracted_message"]
            ),
            "confidence": "high" if len(results) > 2 else "medium",
            "all_probes_tried": len(probe_payloads),
            "successful_probes": len(results)
        }


from functools import lru_cache
from typing import Union, List
import re

class JSONPathExtractor:
    """
    JSONPath extraction algorithm
    Time: O(d) where d = depth of JSON
    Space: O(1) with memoization
    """

    def _init_(self):
        self._path_cache = {}

    @lru_cache(maxsize=1024)
    def parse_path(self, path: str) -> List[Union[str, int]]:
        """
        Parse JSONPath string into list of keys/indices
        Time: O(k) where k = number of path segments
        
        Examples:
          "message" → ["message"]
          "response.choices[0]" → ["response", "choices", 0]
          "data[0].message.content" → ["data", 0, "message", "content"]
        """
        if not path:
            return []

        result = []
        pattern = re.compile(r'\.(\w+)|\[(\d+)\]')

        first_match = re.match(r'^(\w+)', path)
        if first_match:
            result.append(first_match.group(1))

        for match in pattern.finditer(path):
            if match.group(1):
                result.append(match.group(1))
            elif match.group(2):
                result.append(int(match.group(2)))

        return result

    def extract(self, data: Any, path: str) -> Any:
        """
        Extract value at path from JSON
        Time: O(d) where d = depth
        Space: O(1)
        
        Returns: Value at path, or None if path invalid
        """
        if not path or data is None:
            return data

        keys = self.parse_path(path)

        current = data
        for key in keys:
            if isinstance(current, dict):
                current = current.get(key)
            elif isinstance(current, list) and isinstance(key, int):
                if 0 <= key < len(current):
                    current = current[key]
                else:
                    return None
            else:
                return None

            if current is None:
                return None

        return current

    def extract_with_fallback(self, data: Any, paths: List[str]) -> Any:
        """
        Try multiple paths, return first match
        Time: O(n * d) where n = number of paths
        
        Use case: API might return "message" or "response.message"
        """
        for path in paths:
            result = self.extract(data, path)
            if result is not None:
                return result

        return None