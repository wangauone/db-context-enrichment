import argparse
import json
import sys

def main():
    parser = argparse.ArgumentParser(description="Generate gemini-extension.json for release archives")
    parser.add_argument("--version", required=True, help="Extension version (e.g. 1.0.0)")
    parser.add_argument("--platform", required=True, help="Target platform (win32, darwin, linux)")
    args = parser.parse_args()

    # Load the source manifest from root
    try:
        with open("../gemini-extension.json", "r") as f:
            config = json.load(f)
    except FileNotFoundError:
        print("Error: Could not find ../gemini-extension.json")
        sys.exit(1)

    # Update version
    config["version"] = args.version

    # Determine binary name
    binary_name = "${extensionPath}/db-context-enrichment.exe" if args.platform == "win32" else "${extensionPath}/db-context-enrichment"

    # Update mcpServers to use binary
    for server_name, server_config in config.get("mcpServers", {}).items():
        server_config["command"] = binary_name
        server_config["args"] = []

    # Inject mcp-toolbox configuration
    toolbox_binary_name = "${extensionPath}/toolbox.exe" if args.platform == "win32" else "${extensionPath}/toolbox"
    if "mcpServers" not in config:
        config["mcpServers"] = {}
    
    config["mcpServers"]["mcp_toolbox"] = {
        "command": toolbox_binary_name,
        "args": ["--stdio"]
    }

    # Update contextFileName to be relative to the binary (flat structure)
    if "contextFileName" in config:
        config["contextFileName"] = "GEMINI.md"

    with open("gemini-extension.json", "w") as f:
        json.dump(config, f, indent=2)
    
    print(f"Generated gemini-extension.json for {args.platform} version {args.version}")

if __name__ == "__main__":
    main()
