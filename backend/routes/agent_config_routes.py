# # from fastapi import APIRouter, HTTPException
# # from pydantic import BaseModel, Field
# # from typing import Dict, Any, List, Optional
# # from utils.api_format_detector import APIFormatDetector
# # from utils.curl_parser import CurlParser
# # from utils.api_format_detector import JSONPathExtractor
# # import httpx
# # import json

# # router = APIRouter()

# # detector = APIFormatDetector()
# # curl_parser = CurlParser()
# # json_extractor = JSONPathExtractor()

# # # === REQUEST MODELS ===

# # class DetectFormatRequest(BaseModel):
# #     url: str = Field(..., description="Agent API URL to probe")

# # class ParseCurlRequest(BaseModel):
# #     curl: str = Field(..., description="cURL command to parse")

# # class TestConnectionRequest(BaseModel):
# #     url: str = Field(..., description="Agent API URL")
# #     config: Dict[str, Any] = Field(..., description="Request configuration")

# # # === RESPONSE MODELS ===

# # class DetectFormatResponse(BaseModel):
# #     detected: bool
# #     request_format: Optional[Dict[str, Any]] = None
# #     content_type: Optional[str] = None
# #     response_key_path: Optional[str] = None
# #     confidence: Optional[str] = None
# #     warning: Optional[str] = None
# #     message: Optional[str] = None
# #     probes_tried: Optional[int] = None
# #     successful_probes: Optional[int] = None

# # class ParseCurlResponse(BaseModel):
# #     url: Optional[str]
# #     method: str
# #     headers: Dict[str, str]
# #     body: Optional[Dict[str, Any]]
# #     auth: Optional[Dict[str, str]]

# # class TestConnectionResponse(BaseModel):
# #     success: bool
# #     message: Optional[str] = None
# #     error: Optional[str] = None
# #     status_code: Optional[int] = None
# #     response_sample: Optional[str] = None

# # # === ROUTES ===

# # @router.post("/api/detect-format", response_model=DetectFormatResponse)
# # async def detect_format(request: DetectFormatRequest):
# #     """
# #     Auto-detect API format (6 probes: JSON + form-encoding)
    
# #     Returns detected format or suggests manual config
# #     """
# #     try:
# #         result = await detector.probe_endpoint(request.url)
        
# #         if not result.get("detected", False):
# #             return DetectFormatResponse(
# #                 detected=False,
# #                 message="Auto-detection failed. This is common for custom APIs.",
# #                 suggestion="Try cURL import or manual configuration",
# #                 probes_tried=result.get("all_probes_tried", 0)
# #             )
        
# #         return DetectFormatResponse(
# #             detected=True,
# #             request_format=result["request_format"],
# #             content_type=result["content_type"],
# #             response_key_path=result["response_key_path"],
# #             confidence=result.get("confidence", "medium"),
# #             warning=result.get("warning"),
# #             probes_tried=result.get("all_probes_tried", 0),
# #             successful_probes=result.get("successful_probes", 0)
# #         )
    
# #     except httpx.HTTPError as e:
# #         return DetectFormatResponse(
# #             detected=False,
# #             message=f"Network error: {str(e)}",
# #             probes_tried=0
# #         )
# #     except Exception as e:
# #         return DetectFormatResponse(
# #             detected=False,
# #             message=f"Unexpected error: {str(e)}",
# #             probes_tried=0
# #         )

# # @router.post("/api/parse-curl", response_model=ParseCurlResponse)
# # async def parse_curl(request: ParseCurlRequest):
# #     """
# #     Parse cURL command into structured request
    
# #     Handles: -d, --data-raw, --data-binary, -H, -X
# #     """
# #     try:
# #         parsed = curl_parser.parse(request.curl)
        
# #         if not parsed.get("url"):
# #             raise HTTPException(
# #                 status_code=400,
# #                 detail="Invalid cURL command: no URL found"
# #             )
        
# #         return ParseCurlResponse(
# #             url=parsed["url"],
# #             method=parsed.get("method", "GET"),
# #             headers=parsed.get("headers", {}),
# #             body=parsed.get("body"),
# #             auth=parsed.get("auth")
# #         )
    
# #     except HTTPException:
# #         raise
# #     except Exception as e:
# #         raise HTTPException(
# #             status_code=400,
# #             detail=f"Failed to parse cURL: {str(e)}"
# #         )

# # @router.post("/api/test-connection", response_model=TestConnectionResponse)
# # async def test_connection(request: TestConnectionRequest):
# #     """
# #     Test connection with manual configuration
    
# #     Sends test message and verifies response
# #     """
# #     try:
# #         url = request.url
# #         config = request.config
        
# #         if "bodyTemplate" not in config:
# #             raise HTTPException(
# #                 status_code=400,
# #                 detail="Missing required field: bodyTemplate"
# #             )
        
# #         if "responseKeyPath" not in config:
# #             raise HTTPException(
# #                 status_code=400,
# #                 detail="Missing required field: responseKeyPath"
# #             )
        
# #         test_payload = "Hello, this is a test message from AgentSec."
        
# #         try:
# #             body_template = config["bodyTemplate"]
# #             body = json.loads(
# #                 body_template.replace('{{PAYLOAD}}', test_payload)
# #             )
# #         except json.JSONDecodeError as e:
# #             return TestConnectionResponse(
# #                 success=False,
# #                 error=f"Invalid JSON in body template: {str(e)}"
# #             )
        
# #         headers = {"Content-Type": "application/json"}
# #         for header in config.get("headers", []):
# #             if isinstance(header, dict) and header.get("key"):
# #                 headers[header["key"]] = header["value"]
        
# #         async with httpx.AsyncClient() as client:
# #             response = await client.post(
# #                 url,
# #                 headers=headers,
# #                 json=body,
# #                 timeout=10
# #             )
            
# #             try:
# #                 response_data = response.json()
# #             except:
# #                 response_data = {"_text": response.text}
            
# #             message = json_extractor.extract(
# #                 response_data,
# #                 config["responseKeyPath"]
# #             )
            
# #             return TestConnectionResponse(
# #                 success=True,
# #                 message=str(message) if message else "",
# #                 status_code=response.status_code,
# #                 response_sample=str(response_data)[:200]
# #             )
    
# #     except httpx.HTTPError as e:
# #         return TestConnectionResponse(
# #             success=False,
# #             error=f"HTTP error: {str(e)}",
# #             status_code=e.response.status_code if hasattr(e, 'response') else None
# #         )
# #     except HTTPException:
# #         raise
# #     except Exception as e:
# #         return TestConnectionResponse(
# #             success=False,
# #             error=f"Unexpected error: {str(e)}"
# #         )
# #-------------------------------------------------------------------------------
# from fastapi import APIRouter, HTTPException
# from pydantic import BaseModel, Field
# from typing import Dict, Any, List, Optional
# from core.api_format_detector import APIFormatDetector, JSONPathExtractor
# from core.curl_parser import CurlParser
# import httpx
# import json

# router = APIRouter()

# detector = APIFormatDetector()
# curl_parser = CurlParser()
# json_extractor = JSONPathExtractor()

# # === REQUEST MODELS ===

# class DetectFormatRequest(BaseModel):
#     url: str = Field(..., description="Agent API URL to probe")

# class ParseCurlRequest(BaseModel):
#     curl: str = Field(..., description="cURL command to parse")

# class TestConnectionRequest(BaseModel):
#     url: str = Field(..., description="Agent API URL")
#     config: Dict[str, Any] = Field(..., description="Request configuration")

# # === RESPONSE MODELS ===

# class DetectFormatResponse(BaseModel):
#     detected: bool
#     request_format: Optional[Dict[str, Any]] = None
#     content_type: Optional[str] = None
#     response_key_path: Optional[str] = None
#     confidence: Optional[str] = None
#     warning: Optional[str] = None
#     message: Optional[str] = None
#     probes_tried: Optional[int] = None
#     successful_probes: Optional[int] = None

# class ParseCurlResponse(BaseModel):
#     url: Optional[str]
#     method: str
#     headers: Dict[str, str]
#     body: Optional[Dict[str, Any]]
#     auth: Optional[Dict[str, str]]

# class TestConnectionResponse(BaseModel):
#     success: bool
#     message: Optional[str] = None
#     error: Optional[str] = None
#     status_code: Optional[int] = None
#     response_sample: Optional[str] = None

# # === ROUTES ===

# @router.post("/api/detect-format", response_model=DetectFormatResponse)
# async def detect_format(request: DetectFormatRequest):
#     """
#     Auto-detect API format (6 probes: JSON + form-encoding)
    
#     Returns detected format or suggests manual config
#     """
#     try:
#         result = await detector.probe_endpoint(request.url)
        
#         if not result.get("detected", False):
#             return DetectFormatResponse(
#                 detected=False,
#                 message="Auto-detection failed. This is common for custom APIs.",
#                 probes_tried=result.get("all_probes_tried", 0)
#             )
        
#         return DetectFormatResponse(
#             detected=True,
#             request_format=result["request_format"],
#             content_type=result["content_type"],
#             response_key_path=result["response_key_path"],
#             confidence=result.get("confidence", "medium"),
#             warning=result.get("warning"),
#             probes_tried=result.get("all_probes_tried", 0),
#             successful_probes=result.get("successful_probes", 0)
#         )
    
#     except httpx.HTTPError as e:
#         return DetectFormatResponse(
#             detected=False,
#             message=f"Network error: {str(e)}",
#             probes_tried=0
#         )
#     except Exception as e:
#         return DetectFormatResponse(
#             detected=False,
#             message=f"Unexpected error: {str(e)}",
#             probes_tried=0
#         )

# @router.post("/api/parse-curl", response_model=ParseCurlResponse)
# async def parse_curl(request: ParseCurlRequest):
#     """
#     Parse cURL command into structured request
    
#     Handles: -d, --data-raw, --data-binary, -H, -X
#     """
#     try:
#         parsed = curl_parser.parse(request.curl)
        
#         if not parsed.get("url"):
#             raise HTTPException(
#                 status_code=400,
#                 detail="Invalid cURL command: no URL found"
#             )
        
#         return ParseCurlResponse(
#             url=parsed["url"],
#             method=parsed.get("method", "GET"),
#             headers=parsed.get("headers", {}),
#             body=parsed.get("body"),
#             auth=parsed.get("auth")
#         )
    
#     except HTTPException:
#         raise
#     except Exception as e:
#         raise HTTPException(
#             status_code=400,
#             detail=f"Failed to parse cURL: {str(e)}"
#         )

# @router.post("/api/test-connection", response_model=TestConnectionResponse)
# async def test_connection(request: TestConnectionRequest):
#     """
#     Test connection with manual configuration
    
#     Sends test message and verifies response
#     """
#     try:
#         url = request.url
#         config = request.config
        
#         if "bodyTemplate" not in config:
#             raise HTTPException(
#                 status_code=400,
#                 detail="Missing required field: bodyTemplate"
#             )
        
#         if "responseKeyPath" not in config:
#             raise HTTPException(
#                 status_code=400,
#                 detail="Missing required field: responseKeyPath"
#             )
        
#         test_payload = "Hello, this is a test message from AgentSec."
        
#         try:
#             body_template = config["bodyTemplate"]
#             body = json.loads(
#                 body_template.replace('{{PAYLOAD}}', test_payload)
#             )
#         except json.JSONDecodeError as e:
#             return TestConnectionResponse(
#                 success=False,
#                 error=f"Invalid JSON in body template: {str(e)}"
#             )
        
#         headers = {"Content-Type": "application/json"}
#         for header in config.get("headers", []):
#             if isinstance(header, dict) and header.get("key"):
#                 headers[header["key"]] = header["value"]
        
#         async with httpx.AsyncClient() as client:
#             response = await client.post(
#                 url,
#                 headers=headers,
#                 json=body,
#                 timeout=10
#             )
            
#             try:
#                 response_data = response.json()
#             except:
#                 response_data = {"_text": response.text}
            
#             message = json_extractor.extract(
#                 response_data,
#                 config["responseKeyPath"]
#             )
            
#             return TestConnectionResponse(
#                 success=True,
#                 message=str(message) if message else "",
#                 status_code=response.status_code,
#                 response_sample=str(response_data)[:200]
#             )
    
#     except httpx.HTTPError as e:
#         return TestConnectionResponse(
#             success=False,
#             error=f"HTTP error: {str(e)}",
#             status_code=e.response.status_code if hasattr(e, 'response') else None
#         )
#     except HTTPException:
#         raise
#     except Exception as e:
#         return TestConnectionResponse(
#             success=False,
#             error=f"Unexpected error: {str(e)}"
#         )



from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from core.api_format_detector import APIFormatDetector, JSONPathExtractor
from core.curl_parser import CurlParser
import httpx
import json

from auth import get_current_user
from models.sql_models import User

router = APIRouter()

detector = APIFormatDetector()
curl_parser = CurlParser()
json_extractor = JSONPathExtractor()


class DetectFormatRequest(BaseModel):
    url: str = Field(..., description="Agent API URL to probe")

class ParseCurlRequest(BaseModel):
    curl: str = Field(..., description="cURL command to parse")

class TestConnectionRequest(BaseModel):
    url: str = Field(..., description="Agent API URL")
    config: Dict[str, Any] = Field(..., description="Request configuration")


class DetectFormatResponse(BaseModel):
    detected: bool
    request_format: Optional[Dict[str, Any]] = None
    content_type: Optional[str] = None
    response_key_path: Optional[str] = None
    confidence: Optional[str] = None
    warning: Optional[str] = None
    message: Optional[str] = None
    probes_tried: Optional[int] = None
    successful_probes: Optional[int] = None

class ParseCurlResponse(BaseModel):
    url: Optional[str]
    method: str
    headers: Dict[str, str]
    body: Optional[Dict[str, Any]]
    auth: Optional[Dict[str, str]]

class TestConnectionResponse(BaseModel):
    success: bool
    message: Optional[str] = None
    error: Optional[str] = None
    status_code: Optional[int] = None
    response_sample: Optional[str] = None


@router.post("/api/detect-format", response_model=DetectFormatResponse)
async def detect_format(request: DetectFormatRequest, current_user: User = Depends(get_current_user)):
    try:
        result = await detector.probe_endpoint(request.url)
        if not result.get("detected", False):
            return DetectFormatResponse(
                detected=False,
                message="Auto-detection failed. This is common for custom APIs.",
                probes_tried=result.get("all_probes_tried", 0)
            )
        return DetectFormatResponse(
            detected=True,
            request_format=result["request_format"],
            content_type=result["content_type"],
            response_key_path=result["response_key_path"],
            confidence=result.get("confidence", "medium"),
            warning=result.get("warning"),
            probes_tried=result.get("all_probes_tried", 0),
            successful_probes=result.get("successful_probes", 0)
        )
    except httpx.HTTPError as e:
        return DetectFormatResponse(detected=False, message=f"Network error: {str(e)}", probes_tried=0)
    except Exception as e:
        return DetectFormatResponse(detected=False, message=f"Unexpected error: {str(e)}", probes_tried=0)


@router.post("/api/parse-curl", response_model=ParseCurlResponse)
async def parse_curl(request: ParseCurlRequest, current_user: User = Depends(get_current_user)):
    try:
        parsed = curl_parser.parse(request.curl)
        if not parsed.get("url"):
            raise HTTPException(status_code=400, detail="Invalid cURL command: no URL found")
        return ParseCurlResponse(
            url=parsed["url"],
            method=parsed.get("method", "GET"),
            headers=parsed.get("headers", {}),
            body=parsed.get("body"),
            auth=parsed.get("auth")
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse cURL: {str(e)}")


@router.post("/api/test-connection", response_model=TestConnectionResponse)
async def test_connection(request: TestConnectionRequest, current_user: User = Depends(get_current_user)):
    try:
        url = request.url
        config = request.config

        if "bodyTemplate" not in config:
            raise HTTPException(status_code=400, detail="Missing required field: bodyTemplate")
        if "responseKeyPath" not in config:
            raise HTTPException(status_code=400, detail="Missing required field: responseKeyPath")

        test_payload = "Hello, this is a test message from AgentSec."
        try:
            body_template = config["bodyTemplate"]
            body = json.loads(body_template.replace('{{PAYLOAD}}', test_payload))
        except json.JSONDecodeError as e:
            return TestConnectionResponse(success=False, error=f"Invalid JSON in body template: {str(e)}")

        headers = {"Content-Type": "application/json"}
        for header in config.get("headers", []):
            if isinstance(header, dict) and header.get("key"):
                headers[header["key"]] = header["value"]

        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=body, timeout=10)
            try:
                response_data = response.json()
            except:
                response_data = {"_text": response.text}

            message = json_extractor.extract(response_data, config["responseKeyPath"])

            return TestConnectionResponse(
                success=True,
                message=str(message) if message else "",
                status_code=response.status_code,
                response_sample=str(response_data)[:200]
            )
    except httpx.HTTPError as e:
        return TestConnectionResponse(
            success=False, error=f"HTTP error: {str(e)}",
            status_code=e.response.status_code if hasattr(e, 'response') else None
        )
    except HTTPException:
        raise
    except Exception as e:
        return TestConnectionResponse(success=False, error=f"Unexpected error: {str(e)}")