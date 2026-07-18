#!/usr/bin/env python3
"""
Local MCP server for retrieving host information.
Implements the Model Context Protocol over stdio.
"""

import json
import socket
import platform
import subprocess
import sys
from typing import Any

# MCP protocol helpers
def send_response(response: dict):
    """Send a JSON response to stdout."""
    print(json.dumps(response))
    sys.stdout.flush()

def get_hostname() -> str:
    """Get the system hostname."""
    return socket.gethostname()

def get_fqdn() -> str:
    """Get the fully qualified domain name."""
    return socket.getfqdn()

def get_ip_address() -> str:
    """Get the primary local IP address."""
    try:
        # Connect to a non-routable address to determine default interface
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

def get_system_info() -> dict:
    """Get system platform and version info."""
    return {
        "system": platform.system(),
        "release": platform.release(),
        "version": platform.version(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "python_version": platform.python_version(),
    }

def get_docker_info() -> dict:
    """Get Docker daemon info."""
    try:
        result = subprocess.run(
            ["docker", "version", "--format", "json"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            return json.loads(result.stdout)
    except (FileNotFoundError, subprocess.TimeoutExpired, json.JSONDecodeError):
        pass
    return {"error": "Docker not available or not running"}

def get_docker_stats() -> dict:
    """Get Docker resource usage stats."""
    try:
        result = subprocess.run(
            ["docker", "stats", "--all", "--no-stream", "--format", "json"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            return {"containers": json.loads(result.stdout)}
    except (FileNotFoundError, subprocess.TimeoutExpired, json.JSONDecodeError):
        pass
    return {"error": "Could not retrieve Docker stats"}

def handle_call_tool(name: str, arguments: dict) -> Any:
    """Handle tool calls based on tool name."""
    if name == "get_hostname":
        return {"hostname": get_hostname()}
    elif name == "get_fqdn":
        return {"fqdn": get_fqdn()}
    elif name == "get_ip":
        return {"ip": get_ip_address()}
    elif name == "get_system_info":
        return get_system_info()
    elif name == "get_docker_info":
        return get_docker_info()
    elif name == "get_docker_stats":
        return get_docker_stats()
    elif name == "get_host_details":
        return {
            "hostname": get_hostname(),
            "fqdn": get_fqdn(),
            "ip": get_ip_address(),
            "system": get_system_info(),
            "docker": get_docker_info(),
        }
    else:
        return {"error": f"Unknown tool: {name}"}

def main():
    """Main MCP server loop."""
    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                break
            
            request = json.loads(line)
            method = request.get("method")
            
            if method == "tools/list":
                response = {
                    "tools": [
                        {
                            "name": "get_hostname",
                            "description": "Get the system hostname",
                            "inputSchema": {"type": "object", "properties": {}}
                        },
                        {
                            "name": "get_fqdn",
                            "description": "Get the fully qualified domain name",
                            "inputSchema": {"type": "object", "properties": {}}
                        },
                        {
                            "name": "get_ip",
                            "description": "Get the primary local IP address",
                            "inputSchema": {"type": "object", "properties": {}}
                        },
                        {
                            "name": "get_system_info",
                            "description": "Get system platform and version information",
                            "inputSchema": {"type": "object", "properties": {}}
                        },
                        {
                            "name": "get_docker_info",
                            "description": "Get Docker daemon version and info",
                            "inputSchema": {"type": "object", "properties": {}}
                        },
                        {
                            "name": "get_docker_stats",
                            "description": "Get Docker container resource usage statistics",
                            "inputSchema": {"type": "object", "properties": {}}
                        },
                        {
                            "name": "get_host_details",
                            "description": "Get all host and Docker information in one call",
                            "inputSchema": {"type": "object", "properties": {}}
                        },
                    ]
                }
                send_response(response)
            
            elif method == "tools/call":
                tool_name = request.get("params", {}).get("name")
                arguments = request.get("params", {}).get("arguments", {})
                result = handle_call_tool(tool_name, arguments)
                send_response({"content": [{"type": "text", "text": json.dumps(result, indent=2)}]})
            
            elif method == "initialize":
                send_response({
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "serverInfo": {
                        "name": "local-host-mcp",
                        "version": "1.0.0"
                    }
                })
        
        except (json.JSONDecodeError, KeyError, EOFError):
            continue
        except Exception as e:
            send_response({"error": str(e)})

if __name__ == "__main__":
    main()
