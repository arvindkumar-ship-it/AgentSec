# import re
# import json
# import sys
# from typing import Dict, Any, Optional

# if 'json' not in sys.modules:
#     raise ImportError("json module not found - this should never happen")

# def parse_json_safe(body_str: str) -> Optional[Dict[str, Any]]:
#     """Parse JSON with error handling"""
#     try:
#         return json.loads(body_str)
#     except (json.JSONDecodeError, TypeError):
#         return None


# def parse_headers(self, curl_command: str) -> Dict[str, str]:
#     """
#     Parse headers with lexical scoping
#     Time: O(n), Space: O(n)
#     """
#     headers: Dict[str, str] = {}
#     auth: Optional[Dict[str, str]] = None
    
#     header_pattern = re.compile(r'-H\s+["\']([^"\']+)["\']')
    
#     for match in header_pattern.finditer(curl_command):
#         header_str = match.group(1)
        
#         if ": " not in header_str:
#             continue
        
#         key, value = header_str.split(": ", 1)
        
#         if not key or not key.strip():
#             continue
        
#         key = key.strip()
#         value = value.strip()
        
#         headers[key] = value
        
#         if key.lower() == "authorization":
#             auth = self._parse_auth_header(value)
    
#     return headers, auth




# from enum import Enum, auto
# from typing import Iterator, Tuple

# class CurlToken(Enum):
#     FLAG = auto()      # -d, -X, -H
#     VALUE = auto()     # "value", 'value', value
#     EOF = auto()

# class CurlFSM:
#     """
#     Finite State Machine for cURL parsing
#     Time: O(n), Space: O(1)
    
#     States: NORMAL, IN_SINGLE_QUOTE, IN_DOUBLE_QUOTE, IN_ESCAPE
#     """
    
#     def tokenize(self, curl_command: str) -> Iterator[Tuple[CurlToken, str]]:
#         """Tokenize cURL command into Flag/Value pairs"""
#         i = 0
#         n = len(curl_command)
        
#         while i < n:
#             while i < n and curl_command[i].isspace():
#                 i += 1
            
#             if i >= n:
#                 yield (CurlToken.EOF, "")
#                 return
            
#             if curl_command[i] == '-':
#                 j = i + 1
#                 while j < n and not curl_command[j].isspace():
#                     j += 1
                
#                 flag = curl_command[i:j]
#                 yield (CurlToken.FLAG, flag)
#                 i = j
#                 continue
            
#             if curl_command[i] in ('"', "'"):
#                 quote_char = curl_command[i]
#                 i += 1
#                 start = i
#                 value = ""
                
#                 while i < n:
#                     if curl_command[i] == '\\' and i + 1 < n:
#                         value += curl_command[i+1]
#                         i += 2
#                         continue
                    
#                     if curl_command[i] == quote_char:
#                         break
                    
#                     value += curl_command[i]
#                     i += 1
                
#                 yield (CurlToken.VALUE, value)
#                 i += 1
#                 continue
            
#             start = i
#             while i < n and not curl_command[i].isspace():
#                 i += 1
            
#             yield (CurlToken.VALUE, curl_command[start:i])
    
#     def parse(self, curl_command: str) -> Dict[str, Any]:
#         """
#         Parse cURL using FSM
#         Returns: {flag: value} mapping
#         """
#         tokens = list(self.tokenize(curl_command))
#         result = {}
#         current_flag = None
        
#         for token_type, token_value in tokens:
#             if token_type == CurlToken.FLAG:
#                 current_flag = token_value
#             elif token_type == CurlToken.VALUE and current_flag:
#                 if current_flag in ('-d', '--data', '--data-raw', '--data-binary'):
#                     result['body'] = token_value
#                 elif current_flag == '-X':
#                     result['method'] = token_value
#                 elif current_flag == '-H':
#                     if 'headers' not in result:
#                         result['headers'] = []
#                     result['headers'].append(token_value)
#                 current_flag = None
        
#         return result
#------------------------------------------------------------------------------------------------








import re
import json
import sys
from typing import Dict, Any, Optional

if 'json' not in sys.modules:
    raise ImportError("json module not found - this should never happen")

def parse_json_safe(body_str: str) -> Optional[Dict[str, Any]]:
    """Parse JSON with error handling"""
    try:
        return json.loads(body_str)
    except (json.JSONDecodeError, TypeError):
        return None


from enum import Enum, auto
from typing import Iterator, Tuple

class CurlToken(Enum):
    FLAG = auto()      # -d, -X, -H
    VALUE = auto()     # "value", 'value', value
    EOF = auto()

class CurlFSM:
    """
    Finite State Machine for cURL parsing
    Time: O(n), Space: O(1)
    
    States: NORMAL, IN_SINGLE_QUOTE, IN_DOUBLE_QUOTE, IN_ESCAPE
    """
    
    def tokenize(self, curl_command: str) -> Iterator[Tuple[CurlToken, str]]:
        """Tokenize cURL command into Flag/Value pairs"""
        i = 0
        n = len(curl_command)
        
        while i < n:
            while i < n and curl_command[i].isspace():
                i += 1
            
            if i >= n:
                yield (CurlToken.EOF, "")
                return
            
            if curl_command[i] == '-':
                j = i + 1
                while j < n and not curl_command[j].isspace():
                    j += 1
                
                flag = curl_command[i:j]
                yield (CurlToken.FLAG, flag)
                i = j
                continue
            
            if curl_command[i] in ('"', "'"):
                quote_char = curl_command[i]
                i += 1
                start = i
                value = ""
                
                while i < n:
                    if curl_command[i] == '\\' and i + 1 < n:
                        value += curl_command[i+1]
                        i += 2
                        continue
                    
                    if curl_command[i] == quote_char:
                        break
                    
                    value += curl_command[i]
                    i += 1
                
                yield (CurlToken.VALUE, value)
                i += 1
                continue
            
            start = i
            while i < n and not curl_command[i].isspace():
                i += 1
            
            yield (CurlToken.VALUE, curl_command[start:i])
    
    def parse(self, curl_command: str) -> Dict[str, Any]:
        """
        Parse cURL using FSM
        Returns: {flag: value} mapping
        """
        tokens = list(self.tokenize(curl_command))
        result = {}
        current_flag = None
        
        for token_type, token_value in tokens:
            if token_type == CurlToken.FLAG:
                current_flag = token_value
            elif token_type == CurlToken.VALUE and current_flag:
                if current_flag in ('-d', '--data', '--data-raw', '--data-binary'):
                    result['body'] = token_value
                elif current_flag == '-X':
                    result['method'] = token_value
                elif current_flag == '-H':
                    if 'headers' not in result:
                        result['headers'] = []
                    result['headers'].append(token_value)
                current_flag = None
        
        return result


class CurlParser:
    def _init_(self):
        self.fsm = CurlFSM()

    def _parse_auth_header(self, value: str) -> dict:
        if value.lower().startswith("bearer "):
            return {"type": "bearer", "token": value[7:].strip()}
        if value.lower().startswith("basic "):
            return {"type": "basic", "token": value[6:].strip()}
        return {"type": "raw", "token": value.strip()}

    def parse_headers(self, curl_command: str) -> Dict[str, str]:
        """
        Parse headers with lexical scoping
        Time: O(n), Space: O(n)
        """
        headers: Dict[str, str] = {}
        auth: Optional[Dict[str, str]] = None
        
        header_pattern = re.compile(r'-H\s+["\']([^"\']+)["\']')
        
        for match in header_pattern.finditer(curl_command):
            header_str = match.group(1)
            
            if ": " not in header_str:
                continue
            
            key, value = header_str.split(": ", 1)
            
            if not key or not key.strip():
                continue
            
            key = key.strip()
            value = value.strip()
            
            headers[key] = value
            
            if key.lower() == "authorization":
                auth = self._parse_auth_header(value)
        
        return headers, auth

    def parse(self, curl_command: str) -> dict:
        fsm_result = self.fsm.parse(curl_command)
        headers, auth = self.parse_headers(curl_command)

        url_match = re.search(r"curl\s+(?:-\w+\s+)*['\"]?(https?://[^\s'\"]+)", curl_command)
        url = url_match.group(1) if url_match else None

        body = None
        if fsm_result.get("body"):
            body = parse_json_safe(fsm_result["body"])

        return {
            "url": url,
            "method": fsm_result.get("method", "POST" if body else "GET"),
            "headers": headers,
            "body": body,
            "auth": auth,
        }