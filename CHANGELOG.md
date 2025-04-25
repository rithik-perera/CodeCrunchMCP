# Changelog for Azure Usage MCP Integration

## claude_mcp.py - MCP Integration Script

This script processes Azure usage data from a CSV file and provides analysis for Claude Desktop.

### What This Script Does

1. **Loads Azure Usage Data**: Reads the BCAzureUsage 1.csv file containing Azure cost and usage information
2. **Analyzes the Data**: Processes the data to extract insights about costs, services, and regions
3. **Generates Visualizations**: Creates charts showing cost distribution by service or region
4. **Returns Structured Results**: Outputs the analysis in JSON format for Claude Desktop to use

### Key Components

- **load_csv()**: Loads the CSV file into a pandas DataFrame
- **summarize_data()**: Creates a text summary of the Azure usage data
- **generate_chart()**: Creates visualizations of the data
- **process_query()**: Handles queries about the data and returns relevant information
- **main()**: Entry point that processes a default query and outputs the results

### How It Works with Claude Desktop

1. Claude Desktop runs this script when you ask about Azure usage
2. The script processes your Azure usage data
3. The script outputs the analysis as JSON
4. Claude Desktop reads this output and incorporates it into its response

### Integration Configuration

The script is configured to work with Claude Desktop through the `mcp-config.json` file:

```json
{
  "mcpServers": {
    "azure-usage-analyzer": {
      "command": "python",
      "args": ["claude_mcp.py"],
      "cwd": "c:/MCP Code crunch/mcp-server",
      "env": {}
    }
  }
}
```

### Design Decisions

1. **Command-based Approach**: The script runs once per query rather than as a persistent server
2. **Default Query**: Uses a default query to simplify testing and ensure reliability
3. **Stderr Logging**: All logs go to stderr to avoid interfering with the JSON output
4. **Comprehensive Analysis**: Provides multiple types of analysis (cost, service, region) in a single response

### How to Test

Simply run the script from the command line:
```
python claude_mcp.py
```

The script will process the data and output the analysis as JSON.
