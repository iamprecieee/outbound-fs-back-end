from fastapi import APIRouter
from app.utils.esl import ESLConnection

router = APIRouter(
    prefix="/fs",
    tags=["freeswitch-status"],
    responses={404: {"description": "Not found"}},
)

@router.get("/check-connection")
async def check_freeswitch_connection():
    """Check if FreeSWITCH is accessible with the current settings"""
    esl = ESLConnection()
    is_connected, message = esl.check_status()
    
    if is_connected:
        return {"status": "connected", "message": message}
    else:
        return {"status": "error", "message": message}

@router.get("/status")
async def get_freeswitch_status():
    """Get FreeSWITCH status information"""
    esl = ESLConnection()
    result = esl.send_command("status")
    
    if result["success"]:
        return {"status": "success", "data": result["data"]}
    else:
        return {"status": "error", "message": result["message"]}

@router.get("/sofia-gateway/{gateway_name}")
async def get_gateway_status(gateway_name: str):
    """Get Sofia gateway status for a specific gateway"""
    esl = ESLConnection()
    result = esl.send_command(f"sofia status gateway {gateway_name}")
    
    if result["success"]:
        return {
            "status": "success",
            "gateway": gateway_name,
            "data": result["data"]
        }
    else:
        return {
            "status": "error",
            "gateway": gateway_name,
            "message": result["message"]
        } 