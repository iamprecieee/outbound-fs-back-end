import greenswitch
from app.config.config import settings
from typing import Optional, Tuple, Dict, Any

class ESLConnection:
    """
    Utility class to manage FreeSWITCH ESL connections using greenswitch
    """
    def __init__(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        password: Optional[str] = None
    ):
        self.host = host or settings.FREESWITCH_HOST
        self.port = port or settings.FREESWITCH_PORT
        self.password = password or settings.FREESWITCH_PASSWORD
        self.connection = None
        print(f"Connecting to FreeSWITCH at {self.host}:{self.port} with password {self.password}")

    def connect(self) -> bool:
        """
        Establish a connection to FreeSWITCH
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            self.connection = greenswitch.InboundESL(
                host=self.host, 
                port=self.port, 
                password=self.password
            )
            self.connection.connect()
            return True
        except Exception as e:
            print(f"Error connecting to FreeSWITCH: {str(e)}")
            return False

    def disconnect(self) -> None:
        """Disconnect from FreeSWITCH if connected"""
        if self.connection:
            try:
                self.connection.disconnect()
            except:
                pass
            self.connection = None

    def check_status(self) -> Tuple[bool, str]:
        """
        Check if FreeSWITCH is accessible
        
        Returns:
            Tuple[bool, str]: (is_connected, status_message)
        """
        try:
            is_connected = self.connect()
            if is_connected:
                message = "Successfully connected to FreeSWITCH"
                self.disconnect()
                return True, message
            else:
                return False, "Failed to connect to FreeSWITCH"
        except Exception as e:
            return False, f"Error connecting to FreeSWITCH: {str(e)}"

    def send_command(self, command: str) -> Dict[str, Any]:
        """
        Send a command to FreeSWITCH using api
        
        Args:
            command: The command to send
            
        Returns:
            Dict with response status and data
        """
        try:
            if not self.connection:
                if not self.connect():
                    return {
                        "success": False,
                        "message": "Failed to connect to FreeSWITCH"
                    }
            
            # Send command using send method
            response = self.connection.send(f'api {command}')
            
            if response:
                return {
                    "success": True,
                    "message": "Command executed successfully",
                    "data": response.data
                }
            else:
                return {
                    "success": False,
                    "message": "Command returned no response"
                }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error executing command: {str(e)}"
            }
        finally:
            self.disconnect()

    def execute(self, app: str, args: str, uuid: str) -> Dict[str, Any]:
        """
        Execute an application on a specific call UUID
        
        Args:
            app: The application to execute
            args: Arguments for the application
            uuid: Call UUID to execute on
            
        Returns:
            Dict with execution status
        """
        try:
            if not self.connection:
                if not self.connect():
                    return {
                        "success": False,
                        "message": "Failed to connect to FreeSWITCH"
                    }
            
            # Execute application on call using sendRecv
            response = self.connection.send(f'api uuid_execute {uuid} {app} {args}')
            
            if response and not response.is_error():
                return {
                    "success": True, 
                    "message": f"Application {app} executed successfully"
                }
            else:
                error_msg = response.data if response else "Unknown error"
                return {
                    "success": False,
                    "message": f"Failed to execute application {app}: {error_msg}"
                }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error executing application: {str(e)}"
            }
        finally:
            self.disconnect()
    
    def subscribe_events(self, event_format: str = "plain", events: str = "all") -> bool:
        """
        Subscribe to FreeSWITCH events
        
        Args:
            event_format: Format of events (plain, xml, json)
            events: Event types to subscribe to
            
        Returns:
            bool: True if subscription successful
        """
        try:
            if not self.connection:
                if not self.connect():
                    return False
            
            self.connection.send(f'event {event_format} {events}')
            return True
        except Exception as e:
            print(f"Error subscribing to events: {str(e)}")
            return False
    
    def get_event(self) -> Optional[Dict[str, Any]]:
        """
        Receive the next event from FreeSWITCH
        
        Returns:
            Dict containing event data or None
        """
        try:
            if not self.connection:
                if not self.connect():
                    return None
            
            event = self.connection.recv_event()
            if event:
                return {
                    "event_name": event.headers.get("Event-Name"),
                    "event_data": event.headers
                }
            return None
        except Exception as e:
            print(f"Error receiving event: {str(e)}")
            return None 