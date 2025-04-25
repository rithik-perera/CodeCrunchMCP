#!/usr/bin/env python
import json
import sys
import os
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# Set up logging to stderr
import logging
logging.basicConfig(stream=sys.stderr, level=logging.INFO)

# Directory for data files
DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

def load_csv(file_path):
    """Load a CSV file into a pandas DataFrame"""
    df = pd.read_csv(file_path)
    return df

def summarize_data(df):
    """Generate a summary of the data"""
    summary = f"Rows: {len(df)}\nColumns: {', '.join(df.columns)}\n\n"
    
    # Azure-specific summary
    if 'Cost' in df.columns:
        total_cost = df['Cost'].sum()
        summary += f"Total Cost: ${total_cost:.2f}\n"
        summary += f"Average Cost: ${df['Cost'].mean():.2f}\n"
    
    if 'ServiceName' in df.columns:
        top_services = df.groupby('ServiceName')['Cost'].sum().sort_values(ascending=False).head(5)
        summary += "\nTop 5 Services by Cost:\n"
        for service, cost in top_services.items():
            summary += f"- {service}: ${cost:.2f}\n"
    
    if 'ServiceRegion' in df.columns:
        top_regions = df.groupby('ServiceRegion')['Cost'].sum().sort_values(ascending=False).head(5)
        summary += "\nTop 5 Regions by Cost:\n"
        for region, cost in top_regions.items():
            summary += f"- {region}: ${cost:.2f}\n"
    
    return summary

def generate_chart(df, x_col, y_col, output_dir='reports/charts'):
    """Generate a chart from the data"""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_chart.png"
    path = os.path.join(output_dir, filename)

    # For Azure data, we might want to aggregate data
    if x_col in ['ServiceName', 'ServiceRegion', 'ServiceType']:
        # Group by the x column and sum the y column
        chart_data = df.groupby(x_col)[y_col].sum().sort_values(ascending=False).head(10).reset_index()
        
        # Create a bar chart
        plt.figure(figsize=(10, 6))
        plt.bar(chart_data[x_col], chart_data[y_col])
        plt.xticks(rotation=45, ha='right')
        plt.title(f"{y_col} by {x_col}")
        plt.tight_layout()
        plt.savefig(path)
        plt.close()
    else:
        # Default behavior for other columns
        df.plot(kind='bar', x=x_col, y=y_col, legend=False, figsize=(10, 6))
        plt.tight_layout()
        plt.savefig(path)
        plt.close()
    
    return path

def process_query(query):
    """Process a query about Azure usage data"""
    # Default to the BCAzureUsage file
    file_path = os.path.join(DATA_DIR, "BCAzureUsage 1.csv")
    
    if not os.path.exists(file_path):
        # Check if the file exists in the parent directory
        parent_file_path = os.path.join("..", "BCAzureUsage 1.csv")
        if os.path.exists(parent_file_path):
            # Copy the file to the data directory
            import shutil
            shutil.copy(parent_file_path, file_path)
        else:
            return {"error": "Dataset not found"}

    df = load_csv(file_path)
    
    # Basic response with summary and sample data
    response = {
        "query": query,
        "summary": summarize_data(df),
        "sample_data": df.head(5).to_dict(orient="records"),
        "columns": df.columns.tolist()
    }
    
    # Add cost information if relevant
    if any(term in query.lower() for term in ["cost", "expense", "spending", "bill"]) and 'Cost' in df.columns:
        total_cost = df['Cost'].sum()
        avg_cost = df['Cost'].mean()
        response["total_cost"] = f"${total_cost:.2f}"
        response["average_cost"] = f"${avg_cost:.2f}"
        
        # Add top services by cost
        top_services = df.groupby('ServiceName')['Cost'].sum().sort_values(ascending=False).head(5)
        response["top_services"] = [{"name": service, "cost": f"${cost:.2f}"} 
                                   for service, cost in top_services.items()]
    
    # Add region information if relevant
    if any(term in query.lower() for term in ["region", "location", "geography"]) and 'ServiceRegion' in df.columns:
        top_regions = df.groupby('ServiceRegion')['Cost'].sum().sort_values(ascending=False).head(5)
        response["top_regions"] = [{"name": region, "cost": f"${cost:.2f}"} 
                                  for region, cost in top_regions.items()]
        response["chart_path"] = generate_chart(df, 'ServiceRegion', 'Cost')
    
    # Add service information if relevant
    if any(term in query.lower() for term in ["service", "resource", "usage"]) and 'ServiceName' in df.columns:
        service_counts = df['ServiceName'].value_counts().head(5)
        response["top_services_by_count"] = [{"name": service, "count": int(count)} 
                                           for service, count in service_counts.items()]
    
    # Include basic visual if available and not already set
    if "chart_path" not in response and "ServiceName" in df.columns and "Cost" in df.columns:
        response["chart_path"] = generate_chart(df, 'ServiceName', 'Cost')
    
    return response

def main():
    """Main function to process input from Claude Desktop"""
    # For Claude Desktop integration, we'll just process a default query
    # This simplifies testing and ensures the script always works
    
    # Default query to use when testing
    default_query = "Show me Azure usage summary"
    
    try:
        # Process the query
        result = process_query(default_query)
        
        # Output the result to stdout
        print(json.dumps(result, indent=2))
        
        # Return success
        return 0
    except Exception as e:
        # Log errors to stderr
        logging.error(f"Error processing query: {str(e)}")
        print(json.dumps({"error": str(e)}))
        
        # Return error
        return 1

if __name__ == "__main__":
    main()
