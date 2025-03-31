from fastapi import APIRouter, HTTPException
from app.schema.calls import CallRequest, CallResponse
from app.utils.esl import ESLConnection
from app.config.config import settings
import re
import uuid

router = APIRouter(
    prefix="/calls",
    tags=["calls"],
)

@router.post("/", response_model=CallResponse)
async def initiate_call(call_request: CallRequest):
    """
    Initiates an outbound call through FreeSWITCH
    """
    esl = ESLConnection()
    
    caller_id = call_request.caller_id or settings.CALLER_ID
    gateway = call_request.gateway or settings.GATEWAY
    
    if not caller_id:
        raise HTTPException(status_code=400, detail="Caller ID is required")
    
    if not gateway:
        raise HTTPException(status_code=400, detail="Gateway is required")
    
    # Generate a UUID for the call
    call_uuid = str(uuid.uuid4())
    
    variable_str = f"origination_uuid={call_uuid},origination_caller_id_number={caller_id}"
    
    if call_request.variables:
        for key, value in call_request.variables.items():
            variable_str += f",{key}={value}"

    command = f"originate {{{variable_str}}}sofia/gateway/{gateway}/{call_request.destination} &park()"
    
    result = esl.send_command(command)
    
    if result["success"]:
        # Check if there's a UUID in the response
        response_text = result.get("data", "")
        
        # Check for error messages in the response
        if "NORMAL_TEMPORARY_FAILURE" in response_text or "ERROR" in response_text:
            return CallResponse(
                success=False,
                message=f"Failed to initiate call: {response_text}",
                call_uuid=None
            )
        
        # Try to extract UUID if present in response
        uuid_match = re.search(r'([a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})', response_text)
        extracted_uuid = uuid_match.group(1) if uuid_match else call_uuid
        
        return CallResponse(
            success=True,
            message="Call initiated successfully",
            call_uuid=extracted_uuid
        )
    else:
        return CallResponse(
            success=False,
            message=f"Failed to initiate call: {result['message']}",
            call_uuid=None
        )

@router.get("/{call_uuid}/status")
async def get_call_status(call_uuid: str):
    """
    Get status information for a specific call
    """
    esl = ESLConnection()
    result = esl.send_command(f"uuid_exists {call_uuid}")
    
    if not result["success"]:
        raise HTTPException(status_code=500, detail=f"Failed to check call: {result['message']}")
    
    if "true" in result["data"].lower():
        # Call exists, get more details
        call_info = esl.send_command(f"uuid_dump {call_uuid}")
        return {
            "status": "active",
            "uuid": call_uuid,
            "details": call_info.get("data", "No details available")
        }
    else:
        return {
            "status": "not_found",
            "uuid": call_uuid,
            "message": "Call does not exist or has ended"
        }

@router.delete("/{call_uuid}")
async def hangup_call(call_uuid: str):
    """
    Hang up a specific call
    """
    esl = ESLConnection()
    result = esl.send_command(f"uuid_kill {call_uuid}")
    
    if result["success"]:
        return {"success": True, "message": "Call terminated successfully"}
    else:
        return {"success": False, "message": f"Failed to terminate call: {result['message']}"}