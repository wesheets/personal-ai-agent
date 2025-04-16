"""
Slack Messenger Tool for the Personal AI Agent System.

This module provides functionality to compose, format, and send
messages to Slack channels and users.
"""

import os
import json
import time
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

# Configure logging
logger = logging.getLogger("slack_messenger")

def run(
    message: str,
    channel: str = None,
    user: str = None,
    thread_ts: str = None,
    blocks: List[Dict[str, Any]] = None,
    attachments: List[Dict[str, Any]] = None,
    emoji_reactions: List[str] = None,
    scheduled_time: str = None,
    message_type: str = "text",
    formatting: str = "default",
    include_mentions: List[str] = None,
    include_links: List[Dict[str, str]] = None,
    include_code_snippet: Dict[str, str] = None,
    dry_run: bool = False,
    store_memory: bool = False,
    memory_manager = None,
    memory_tags: List[str] = ["slack", "communication"],
    memory_scope: str = "agent"
) -> Dict[str, Any]:
    """
    Compose and optionally send a message to Slack.
    
    Args:
        message: Main message text content
        channel: Channel name or ID to send the message to
        user: User ID to send a direct message to
        thread_ts: Thread timestamp to reply to a thread
        blocks: Slack Block Kit blocks for rich formatting
        attachments: Slack message attachments
        emoji_reactions: List of emoji reactions to add to the message
        scheduled_time: ISO datetime string for scheduling the message
        message_type: Type of message (text, announcement, update)
        formatting: Formatting style (default, minimal, rich)
        include_mentions: List of users to mention in the message
        include_links: List of links to include in the message
        include_code_snippet: Code snippet to include in the message
        dry_run: If True, compose but don't send the message
        store_memory: Whether to store the message in memory
        memory_manager: Memory manager instance for storing results
        memory_tags: Tags to apply to the memory entry
        memory_scope: Scope for the memory entry (agent or global)
        
    Returns:
        Dictionary containing the composed message and send status
    """
    logger.info(f"Composing Slack message for {'channel: ' + channel if channel else 'user: ' + user if user else 'unknown destination'}")
    
    try:
        # Validate inputs
        if not message and not blocks:
            raise ValueError("Either message text or blocks must be provided")
        
        if not channel and not user:
            raise ValueError("Either channel or user must be specified as the destination")
        
        if channel and user:
            logger.warning("Both channel and user specified; channel will take precedence")
        
        # Process message formatting
        formatted_message = _format_message(
            message,
            message_type,
            formatting,
            include_mentions,
            include_links,
            include_code_snippet
        )
        
        # Generate blocks if not provided
        if not blocks:
            blocks = _generate_blocks(
                formatted_message,
                message_type,
                formatting,
                include_code_snippet
            )
        
        # Generate attachments if not provided but links are included
        if not attachments and include_links:
            attachments = _generate_attachments(include_links)
        
        # Compose the final message payload
        message_payload = {
            "text": formatted_message,
            "blocks": blocks if blocks else None,
            "attachments": attachments if attachments else None,
            "thread_ts": thread_ts if thread_ts else None,
            "channel": channel if channel else user,
            "scheduled_time": scheduled_time
        }
        
        # Clean up None values
        message_payload = {k: v for k, v in message_payload.items() if v is not None}
        
        # Send the message if not a dry run
        if not dry_run:
            send_result = _send_slack_message(message_payload)
            message_ts = send_result.get("ts") if send_result.get("ok") else None
            
            # Add emoji reactions if specified and message was sent successfully
            if emoji_reactions and message_ts:
                for emoji in emoji_reactions:
                    _add_reaction(emoji, channel or user, message_ts)
        else:
            send_result = {"ok": True, "dry_run": True}
            message_ts = None
        
        # Store in memory if requested
        if store_memory and memory_manager:
            try:
                # Create a memory entry with the message content
                memory_entry = {
                    "type": "slack_message",
                    "destination": channel or user,
                    "message_type": message_type,
                    "content_preview": message[:100] + ("..." if len(message) > 100 else ""),
                    "thread_ts": thread_ts,
                    "timestamp": datetime.now().isoformat()
                }
                
                memory_manager.add_memory(
                    content=json.dumps(memory_entry),
                    scope=memory_scope,
                    tags=memory_tags + [f"channel_{channel}" if channel else f"user_{user}", f"type_{message_type}"]
                )
                
                logger.info(f"Stored Slack message in memory with tags: {memory_tags}")
            except Exception as e:
                logger.error(f"Failed to store Slack message in memory: {str(e)}")
        
        return {
            "success": send_result.get("ok", False),
            "message": formatted_message,
            "blocks": blocks,
            "attachments": attachments,
            "destination": channel or user,
            "message_ts": message_ts,
            "thread_ts": thread_ts,
            "scheduled_time": scheduled_time,
            "dry_run": dry_run,
            "error": send_result.get("error") if not send_result.get("ok", False) else None
        }
    except Exception as e:
        error_msg = f"Error composing Slack message: {str(e)}"
        logger.error(error_msg)
        return {
            "success": False,
            "error": error_msg,
            "destination": channel or user
        }

def _format_message(
    message: str,
    message_type: str,
    formatting: str,
    include_mentions: Optional[List[str]],
    include_links: Optional[List[Dict[str, str]]],
    include_code_snippet: Optional[Dict[str, str]]
) -> str:
    """
    Format the message text based on specified parameters.
    
    Args:
        message: Original message text
        message_type: Type of message
        formatting: Formatting style
        include_mentions: List of users to mention
        include_links: List of links to include
        include_code_snippet: Code snippet to include
        
    Returns:
        Formatted message text
    """
    formatted_message = message
    
    # Add mentions if specified
    if include_mentions:
        mentions_text = " ".join([f"<@{user}>" for user in include_mentions])
        formatted_message = f"{mentions_text} {formatted_message}"
    
    # Add message type formatting
    if message_type == "announcement":
        formatted_message = f":loudspeaker: *ANNOUNCEMENT*: {formatted_message}"
    elif message_type == "update":
        formatted_message = f":arrows_counterclockwise: *UPDATE*: {formatted_message}"
    
    # Add links if specified and not using blocks
    if include_links and formatting != "rich":
        links_text = []
        for link in include_links:
            if "url" in link and "title" in link:
                links_text.append(f"<{link['url']}|{link['title']}>")
            elif "url" in link:
                links_text.append(f"<{link['url']}>")
        
        if links_text:
            formatted_message = f"{formatted_message}\n\nLinks: {' | '.join(links_text)}"
    
    # Add code snippet if specified and not using blocks
    if include_code_snippet and formatting != "rich":
        code_language = include_code_snippet.get("language", "")
        code_content = include_code_snippet.get("content", "")
        
        if code_content:
            formatted_message = f"{formatted_message}\n\n```{code_language}\n{code_content}\n```"
    
    return formatted_message

def _generate_blocks(
    formatted_message: str,
    message_type: str,
    formatting: str,
    include_code_snippet: Optional[Dict[str, str]]
) -> List[Dict[str, Any]]:
    """
    Generate Slack Block Kit blocks for rich formatting.
    
    Args:
        formatted_message: Formatted message text
        message_type: Type of message
        formatting: Formatting style
        include_code_snippet: Code snippet to include
        
    Returns:
        List of Slack Block Kit blocks
    """
    blocks = []
    
    # Only generate blocks for rich formatting
    if formatting == "rich":
        # Add header for announcements and updates
        if message_type in ["announcement", "update"]:
            header_text = "ANNOUNCEMENT" if message_type == "announcement" else "UPDATE"
            blocks.append({
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": header_text,
                    "emoji": True
                }
            })
        
        # Add main message section
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": formatted_message
            }
        })
        
        # Add divider if we're adding more content
        if include_code_snippet:
            blocks.append({
                "type": "divider"
            })
        
        # Add code snippet if specified
        if include_code_snippet:
            code_language = include_code_snippet.get("language", "")
            code_content = include_code_snippet.get("content", "")
            code_title = include_code_snippet.get("title", "Code Snippet")
            
            if code_content:
                # Add title for code snippet
                blocks.append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*{code_title}*"
                    }
                })
                
                # Add the code snippet
                blocks.append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"```{code_language}\n{code_content}\n```"
                    }
                })
    
    return blocks if blocks else None

def _generate_attachments(include_links: List[Dict[str, str]]) -> List[Dict[str, Any]]:
    """
    Generate Slack message attachments for links.
    
    Args:
        include_links: List of links to include
        
    Returns:
        List of Slack message attachments
    """
    attachments = []
    
    for link in include_links:
        if "url" in link:
            attachment = {
                "fallback": link.get("title", link["url"]),
                "title": link.get("title", link["url"]),
                "title_link": link["url"],
                "text": link.get("description", ""),
                "color": link.get("color", "#36C5F0")  # Default Slack blue
            }
            attachments.append(attachment)
    
    return attachments if attachments else None

def _send_slack_message(message_payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Send a message to Slack using the Slack API.
    
    Args:
        message_payload: Message payload to send
        
    Returns:
        API response from Slack
    """
    # In a real implementation, this would use the Slack API
    # For this example, we'll simulate a successful response
    logger.info(f"Would send message to Slack: {json.dumps(message_payload)}")
    
    # Simulate API call
    time.sleep(0.5)
    
    # Return simulated response
    return {
        "ok": True,
        "channel": message_payload.get("channel"),
        "ts": f"{time.time()}",
        "message": {
            "text": message_payload.get("text"),
            "user": "U12345678",  # Simulated bot user ID
            "bot_id": "B12345678",  # Simulated bot ID
            "ts": f"{time.time()}"
        }
    }

def _add_reaction(
    emoji: str,
    channel: str,
    timestamp: str
) -> Dict[str, Any]:
    """
    Add an emoji reaction to a message.
    
    Args:
        emoji: Emoji name (without colons)
        channel: Channel or user ID
        timestamp: Message timestamp
        
    Returns:
        API response from Slack
    """
    # In a real implementation, this would use the Slack API
    # For this example, we'll simulate a successful response
    logger.info(f"Would add reaction {emoji} to message {timestamp} in {channel}")
    
    # Simulate API call
    time.sleep(0.2)
    
    # Return simulated response
    return {
        "ok": True
    }

def get_channel_history(
    channel: str,
    limit: int = 10,
    oldest: str = None,
    latest: str = None
) -> Dict[str, Any]:
    """
    Get message history for a channel.
    
    Args:
        channel: Channel ID
        limit: Maximum number of messages to return
        oldest: Start of time range (timestamp)
        latest: End of time range (timestamp)
        
    Returns:
        Dictionary containing channel history
    """
    logger.info(f"Getting history for channel {channel}")
    
    try:
        # In a real implementation, this would use the Slack API
        # For this example, we'll simulate a successful response
        
        # Simulate API call
        time.sleep(0.5)
        
        # Generate simulated messages
        messages = []
        current_time = time.time()
        
        for i in range(limit):
            message_time = current_time - (i * 3600)  # One hour intervals
            messages.append({
                "type": "message",
                "user": f"U{10000000 + i}",
                "text": f"Sample message {i + 1}",
                "ts": str(message_time)
            })
        
        return {
            "success": True,
            "messages": messages,
            "has_more": limit >= 10,
            "channel": channel
        }
    except Exception as e:
        error_msg = f"Error getting channel history: {str(e)}"
        logger.error(error_msg)
        return {
            "success": False,
            "error": error_msg,
            "channel": channel
        }

def get_thread_replies(
    channel: str,
    thread_ts: str,
    limit: int = 10
) -> Dict[str, Any]:
    """
    Get replies in a thread.
    
    Args:
        channel: Channel ID
        thread_ts: Parent message timestamp
        limit: Maximum number of replies to return
        
    Returns:
        Dictionary containing thread replies
    """
    logger.info(f"Getting replies for thread {thread_ts} in channel {channel}")
    
    try:
        # In a real implementation, this would use the Slack API
        # For this example, we'll simulate a successful response
        
        # Simulate API call
        time.sleep(0.5)
        
        # Generate simulated replies
        replies = []
        thread_start_time = float(thread_ts)
        
        for i in range(limit):
            reply_time = thread_start_time + ((i + 1) * 300)  # 5 minute intervals
            replies.append({
                "type": "message",
                "user": f"U{20000000 + i}",
                "text": f"Thread reply {i + 1}",
                "ts": str(reply_time),
                "thread_ts": thread_ts
            })
        
        return {
            "success": True,
            "messages": replies,
            "has_more": limit >= 10,
            "channel": channel,
            "thread_ts": thread_ts
        }
    except Exception as e:
        error_msg = f"Error getting thread replies: {str(e)}"
        logger.error(error_msg)
        return {
            "success": False,
            "error": error_msg,
            "channel": channel,
            "thread_ts": thread_ts
        }

def search_messages(
    query: str,
    channels: List[str] = None,
    sort: str = "timestamp",
    sort_dir: str = "desc",
    limit: int = 20
) -> Dict[str, Any]:
    """
    Search for messages in Slack.
    
    Args:
        query: Search query
        channels: List of channel IDs to search in
        sort: Sort field (timestamp, score)
        sort_dir: Sort direction (asc, desc)
        limit: Maximum number of results to return
        
    Returns:
        Dictionary containing search results
    """
    logger.info(f"Searching for messages with query: {query}")
    
    try:
        # In a real implementation, this would use the Slack API
        # For this example, we'll simulate a successful response
        
        # Simulate API call
        time.sleep(1.0)
        
        # Generate simulated search results
        matches = []
        current_time = time.time()
        
        for i in range(min(5, limit)):  # Simulate finding fewer results than limit
            message_time = current_time - (i * 86400)  # One day intervals
            channel_id = channels[i % len(channels)] if channels else f"C{30000000 + i}"
            
            matches.append({
                "type": "message",
                "channel": {
                    "id": channel_id,
                    "name": f"channel-{i + 1}"
                },
                "user": f"U{40000000 + i}",
                "username": f"user{i + 1}",
                "text": f"Message containing {query} - result {i + 1}",
                "ts": str(message_time),
                "permalink": f"https://slack.com/archives/{channel_id}/p{int(message_time * 1000000)}"
            })
        
        return {
            "success": True,
            "total": len(matches),
            "matches": matches,
            "query": query
        }
    except Exception as e:
        error_msg = f"Error searching messages: {str(e)}"
        logger.error(error_msg)
        return {
            "success": False,
            "error": error_msg,
            "query": query
        }

def update_message(
    channel: str,
    ts: str,
    text: str = None,
    blocks: List[Dict[str, Any]] = None,
    attachments: List[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Update an existing message.
    
    Args:
        channel: Channel ID
        ts: Message timestamp
        text: New message text
        blocks: New Slack Block Kit blocks
        attachments: New Slack message attachments
        
    Returns:
        Dictionary containing update status
    """
    logger.info(f"Updating message {ts} in channel {channel}")
    
    try:
        # Validate inputs
        if not text and not blocks:
            raise ValueError("Either text or blocks must be provided")
        
        # Prepare update payload
        update_payload = {
            "channel": channel,
            "ts": ts,
            "text": text,
            "blocks": blocks,
            "attachments": attachments
        }
        
        # Clean up None values
        update_payload = {k: v for k, v in update_payload.items() if v is not None}
        
        # In a real implementation, this would use the Slack API
        # For this example, we'll simulate a successful response
        logger.info(f"Would update message with: {json.dumps(update_payload)}")
        
        # Simulate API call
        time.sleep(0.5)
        
        return {
            "success": True,
            "channel": channel,
            "ts": ts,
            "text": text
        }
    except Exception as e:
        error_msg = f"Error updating message: {str(e)}"
        logger.error(error_msg)
        return {
            "success": False,
            "error": error_msg,
            "channel": channel,
            "ts": ts
        }

def delete_message(
    channel: str,
    ts: str
) -> Dict[str, Any]:
    """
    Delete a message.
    
    Args:
        channel: Channel ID
        ts: Message timestamp
        
    Returns:
        Dictionary containing deletion status
    """
    logger.info(f"Deleting message {ts} in channel {channel}")
    
    try:
        # In a real implementation, this would use the Slack API
        # For this example, we'll simulate a successful response
        
        # Simulate API call
        time.sleep(0.5)
        
        return {
            "success": True,
            "channel": channel,
            "ts": ts
        }
    except Exception as e:
        error_msg = f"Error deleting message: {str(e)}"
        logger.error(error_msg)
        return {
            "success": False,
            "error": error_msg,
            "channel": channel,
            "ts": ts
        }

def schedule_message(
    channel: str,
    text: str,
    post_at: int,
    blocks: List[Dict[str, Any]] = None,
    attachments: List[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Schedule a message to be sent later.
    
    Args:
        channel: Channel ID
        text: Message text
        post_at: Unix timestamp for when to send the message
        blocks: Slack Block Kit blocks
        attachments: Slack message attachments
        
    Returns:
        Dictionary containing scheduling status
    """
    logger.info(f"Scheduling message in channel {channel} for timestamp {post_at}")
    
    try:
        # Validate inputs
        if not text:
            raise ValueError("Message text must be provided")
        
        # Prepare schedule payload
        schedule_payload = {
            "channel": channel,
            "text": text,
            "post_at": post_at,
            "blocks": blocks,
            "attachments": attachments
        }
        
        # Clean up None values
        schedule_payload = {k: v for k, v in schedule_payload.items() if v is not None}
        
        # In a real implementation, this would use the Slack API
        # For this example, we'll simulate a successful response
        logger.info(f"Would schedule message with: {json.dumps(schedule_payload)}")
        
        # Simulate API call
        time.sleep(0.5)
        
        return {
            "success": True,
            "channel": channel,
            "scheduled_message_id": f"Q{int(time.time())}",
            "post_at": post_at,
            "text": text
        }
    except Exception as e:
        error_msg = f"Error scheduling message: {str(e)}"
        logger.error(error_msg)
        return {
            "success": False,
            "error": error_msg,
            "channel": channel
        }
