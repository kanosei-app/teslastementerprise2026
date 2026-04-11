import logging

def get_agent_logger(agent_name):
    """
    Creates and returns a custom logger for an agent.
    """
    # Create a logger specific to the agent's name
    logger = logging.getLogger(agent_name)
   
    # Set the logging level (DEBUG catches everything, INFO catches general updates)
    logger.setLevel(logging.DEBUG)
   
    # Create console handler and set level to debug
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
   
    # Create a clean formatter: Time - Agent Name - Level - Message
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
   
    # Add formatter to the handler
    ch.setFormatter(formatter)
   
    # Add handler to logger (checking to prevent duplicate logs)
    if not logger.handlers:
        logger.addHandler(ch)
       
    return logger