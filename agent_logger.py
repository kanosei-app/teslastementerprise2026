import logging
import json

def get_agent_logger(agent_name):
    """
    Creates and returns a custom logger for an agent.
    """
    logger = logging.getLogger(agent_name)
    logger.setLevel(logging.DEBUG)
    
    # Check if handlers already exist to prevent duplicate logs in the console
    if not logger.handlers:
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        
        # Clean standard formatter for general logs
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        logger.addHandler(ch)
        
    return logger

def log_inter_agent_message(logger, message, direction="SENDING"):
    """
    Specifically handles the standardized JSON schema for agent communication.
    
    Args:
        logger: The agent's logger instance.
        message (dict): The standardized JSON message dictionary.
        direction (str): Flow label, e.g. "SENDING", "RECEIVING", or from the
            message bus: "ROUTING" (persist + route).
    """
    try:
        # Extract the critical envelope data for a clean, high-level summary
        msg_id = message.get("id", "UNKNOWN_ID")
        sender = message.get("sender", "UNKNOWN_SENDER")
        recipient = message.get("recipient", "UNKNOWN_RECIPIENT")
        task_type = message.get("task_type", "UNKNOWN_TASK")
        status = message.get("status", "UNKNOWN_STATUS")
        
        # 1. Log a clean summary at the INFO level so you can track the conversation flow
        summary = f"[{direction}] {sender} -> {recipient} | Task: {task_type} | Status: {status} | ID: {msg_id}"
        logger.info(summary)
        
        # 2. Log the complete, pretty-printed JSON at the DEBUG level for detailed inspection
        pretty_json = json.dumps(message, indent=2)
        logger.debug(f"Full Message Envelope:\n{pretty_json}")
        
        # 3. Raise an alert if there's an error in the envelope
        if message.get("error"):
            logger.error(f"Message ID {msg_id} contains an error: {message['error']}")
            
    except Exception as e:
        logger.error(f"Failed to parse inter-agent message: {e}")