"""
Spreadsheet Analyzer Tool for the Personal AI Agent System.

This module provides functionality to analyze, process, and extract insights
from spreadsheet files in various formats (CSV, Excel, Google Sheets).
"""

import os
import json
import time
import random
from typing import Dict, List, Any, Optional, Union
import logging
from datetime import datetime

# Configure logging
logger = logging.getLogger("spreadsheet_analyzer")

def run(
    file_path: str,
    operation: str = "analyze",
    sheet_name: Optional[str] = None,
    range: Optional[str] = None,
    columns: Optional[List[str]] = None,
    filters: Optional[Dict[str, Any]] = None,
    groupby: Optional[List[str]] = None,
    aggregations: Optional[Dict[str, str]] = None,
    output_format: str = "json",
    save_result: bool = False,
    output_path: Optional[str] = None,
    store_memory: bool = False,
    memory_manager = None,
    memory_tags: List[str] = ["spreadsheet", "data_analysis"],
    memory_scope: str = "agent"
) -> Dict[str, Any]:
    """
    Analyze and process spreadsheet data.
    
    Args:
        file_path: Path to the spreadsheet file
        operation: Operation to perform (analyze, filter, aggregate, pivot, etc.)
        sheet_name: Name of the sheet to process (for multi-sheet files)
        range: Cell range to process (e.g., "A1:D10")
        columns: List of columns to include in the result
        filters: Conditions to filter rows
        groupby: Columns to group by for aggregation
        aggregations: Aggregation functions to apply to columns
        output_format: Format for the output (json, csv, html)
        save_result: Whether to save the result to a file
        output_path: Path to save the result (if save_result is True)
        store_memory: Whether to store the analysis results in memory
        memory_manager: Memory manager instance for storing results
        memory_tags: Tags to apply to the memory entry
        memory_scope: Scope for the memory entry (agent or global)
        
    Returns:
        Dictionary containing analysis results and metadata
    """
    logger.info(f"Analyzing spreadsheet: {file_path}, operation: {operation}")
    
    try:
        # Check if file exists
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Spreadsheet file not found: {file_path}")
            
        # Validate operation
        if operation not in SUPPORTED_OPERATIONS:
            raise ValueError(f"Unsupported operation: {operation}. Supported operations: {', '.join(SUPPORTED_OPERATIONS)}")
            
        # In a real implementation, this would use pandas, openpyxl, or similar libraries
        # For now, we'll simulate the spreadsheet analysis
        
        # Detect file format
        file_format = _detect_file_format(file_path)
        
        # Load data (simulated)
        data, metadata = _simulate_load_data(file_path, file_format, sheet_name, range)
        
        # Perform the requested operation
        if operation == "analyze":
            result = _analyze_data(data, metadata)
        elif operation == "filter":
            result = _filter_data(data, filters, columns)
        elif operation == "aggregate":
            result = _aggregate_data(data, groupby, aggregations)
        elif operation == "pivot":
            result = _pivot_data(data, groupby, columns, aggregations)
        elif operation == "describe":
            result = _describe_data(data, columns)
        elif operation == "correlate":
            result = _correlate_data(data, columns)
        
        # Format the output
        formatted_result = _format_output(result, output_format)
        
        # Save the result if requested
        if save_result and output_path:
            _save_result(formatted_result, output_path, output_format)
            result["saved_to"] = output_path
        
        # Store in memory if requested
        if store_memory and memory_manager:
            try:
                # Create a summary of the analysis for memory storage
                memory_entry = {
                    "type": "spreadsheet_analysis",
                    "file_path": file_path,
                    "file_format": file_format,
                    "operation": operation,
                    "timestamp": datetime.now().isoformat(),
                    "summary": _generate_analysis_summary(result, operation)
                }
                
                memory_manager.add_memory(
                    content=json.dumps(memory_entry),
                    scope=memory_scope,
                    tags=memory_tags
                )
                
                logger.info(f"Stored spreadsheet analysis in memory with tags: {memory_tags}")
            except Exception as e:
                logger.error(f"Failed to store spreadsheet analysis in memory: {str(e)}")
        
        return {
            "success": True,
            "operation": operation,
            "file_path": file_path,
            "file_format": file_format,
            "metadata": metadata,
            "result": result
        }
    except Exception as e:
        error_msg = f"Error analyzing spreadsheet: {str(e)}"
        logger.error(error_msg)
        return {
            "success": False,
            "error": error_msg,
            "file_path": file_path,
            "operation": operation
        }

def _detect_file_format(file_path: str) -> str:
    """
    Detect the format of the spreadsheet file.
    
    Args:
        file_path: Path to the spreadsheet file
        
    Returns:
        Detected file format
    """
    # Get file extension
    _, ext = os.path.splitext(file_path)
    ext = ext.lower()
    
    if ext == ".csv":
        return "csv"
    elif ext in [".xls", ".xlsx", ".xlsm"]:
        return "excel"
    elif ext in [".ods"]:
        return "ods"
    elif ext in [".gsheet"]:
        return "google_sheets"
    else:
        # Default to CSV for unknown formats
        return "csv"

def _simulate_load_data(
    file_path: str,
    file_format: str,
    sheet_name: Optional[str],
    range: Optional[str]
) -> tuple:
    """
    Simulate loading data from a spreadsheet file.
    
    Args:
        file_path: Path to the spreadsheet file
        file_format: Format of the file
        sheet_name: Name of the sheet to load
        range: Cell range to load
        
    Returns:
        Tuple of (data, metadata)
    """
    # Extract filename for simulation purposes
    filename = os.path.basename(file_path)
    name_without_ext = os.path.splitext(filename)[0].replace("_", " ").replace("-", " ")
    
    # Generate simulated metadata
    metadata = {
        "filename": filename,
        "format": file_format,
        "size_kb": random.randint(10, 5000),
        "last_modified": _get_iso_time(days_ago=random.randint(0, 30))
    }
    
    # Add format-specific metadata
    if file_format == "excel":
        metadata["sheets"] = ["Sheet1", "Sheet2", "Data"] if not sheet_name else [sheet_name]
        metadata["active_sheet"] = sheet_name or "Sheet1"
    
    # Generate simulated data based on filename
    if "sales" in name_without_ext.lower():
        data = _generate_sales_data()
    elif "employee" in name_without_ext.lower() or "hr" in name_without_ext.lower():
        data = _generate_employee_data()
    elif "financial" in name_without_ext.lower() or "finance" in name_without_ext.lower():
        data = _generate_financial_data()
    elif "inventory" in name_without_ext.lower() or "product" in name_without_ext.lower():
        data = _generate_inventory_data()
    else:
        # Generic data
        data = _generate_generic_data()
    
    # Apply range filter if specified
    if range:
        # This is a simplified simulation of range filtering
        # In a real implementation, this would parse the range and extract the corresponding subset
        data = data[:min(len(data), 10)]
    
    return data, metadata

def _generate_sales_data() -> List[Dict[str, Any]]:
    """
    Generate simulated sales data.
    
    Returns:
        List of dictionaries representing sales data
    """
    products = ["Product A", "Product B", "Product C", "Product D", "Product E"]
    regions = ["North", "South", "East", "West", "Central"]
    channels = ["Online", "Retail", "Distributor", "Direct"]
    
    data = []
    
    for i in range(50):
        product = random.choice(products)
        region = random.choice(regions)
        channel = random.choice(channels)
        
        # Generate realistic sales figures
        quantity = random.randint(10, 100)
        unit_price = round(random.uniform(10, 500), 2)
        revenue = round(quantity * unit_price, 2)
        cost = round(revenue * random.uniform(0.4, 0.7), 2)
        profit = round(revenue - cost, 2)
        
        # Generate date within the last year
        date = _get_iso_time(days_ago=random.randint(0, 365)).split("T")[0]
        
        data.append({
            "Date": date,
            "Product": product,
            "Region": region,
            "Channel": channel,
            "Quantity": quantity,
            "UnitPrice": unit_price,
            "Revenue": revenue,
            "Cost": cost,
            "Profit": profit
        })
    
    return data

def _generate_employee_data() -> List[Dict[str, Any]]:
    """
    Generate simulated employee data.
    
    Returns:
        List of dictionaries representing employee data
    """
    departments = ["Engineering", "Marketing", "Sales", "HR", "Finance", "Operations"]
    positions = ["Manager", "Senior", "Junior", "Intern", "Director", "VP"]
    locations = ["New York", "San Francisco", "Chicago", "Austin", "Remote"]
    
    data = []
    
    for i in range(50):
        department = random.choice(departments)
        position = random.choice(positions)
        location = random.choice(locations)
        
        # Generate realistic employee data
        employee_id = f"EMP{1000 + i}"
        name = f"Employee {i+1}"
        age = random.randint(22, 65)
        salary = random.randint(40000, 200000)
        years_of_service = random.randint(0, 20)
        performance = round(random.uniform(1, 5), 1)
        
        data.append({
            "EmployeeID": employee_id,
            "Name": name,
            "Department": department,
            "Position": position,
            "Location": location,
            "Age": age,
            "Salary": salary,
            "YearsOfService": years_of_service,
            "PerformanceRating": performance
        })
    
    return data

def _generate_financial_data() -> List[Dict[str, Any]]:
    """
    Generate simulated financial data.
    
    Returns:
        List of dictionaries representing financial data
    """
    categories = ["Revenue", "Cost of Goods Sold", "Operating Expenses", "Marketing", "R&D", "Administrative"]
    quarters = ["Q1", "Q2", "Q3", "Q4"]
    years = [2023, 2024, 2025]
    
    data = []
    
    for year in years:
        for quarter in quarters:
            for category in categories:
                # Generate realistic financial figures
                amount = round(random.uniform(10000, 1000000), 2)
                budget = round(amount * random.uniform(0.8, 1.2), 2)
                variance = round(amount - budget, 2)
                variance_percent = round((variance / budget) * 100, 2)
                
                data.append({
                    "Year": year,
                    "Quarter": quarter,
                    "Category": category,
                    "Amount": amount,
                    "Budget": budget,
                    "Variance": variance,
                    "VariancePercent": variance_percent
                })
    
    return data

def _generate_inventory_data() -> List[Dict[str, Any]]:
    """
    Generate simulated inventory data.
    
    Returns:
        List of dictionaries representing inventory data
    """
    categories = ["Electronics", "Clothing", "Home Goods", "Sporting Goods", "Office Supplies"]
    warehouses = ["Warehouse A", "Warehouse B", "Warehouse C", "Distribution Center"]
    suppliers = ["Supplier 1", "Supplier 2", "Supplier 3", "Supplier 4"]
    
    data = []
    
    for i in range(50):
        category = random.choice(categories)
        warehouse = random.choice(warehouses)
        supplier = random.choice(suppliers)
        
        # Generate realistic inventory data
        product_id = f"PROD{1000 + i}"
        product_name = f"Product {i+1}"
        quantity = random.randint(0, 1000)
        unit_cost = round(random.uniform(5, 500), 2)
        total_value = round(quantity * unit_cost, 2)
        reorder_level = random.randint(10, 100)
        days_of_supply = random.randint(5, 60)
        
        data.append({
            "ProductID": product_id,
            "ProductName": product_name,
            "Category": category,
            "Warehouse": warehouse,
            "Supplier": supplier,
            "Quantity": quantity,
            "UnitCost": unit_cost,
            "TotalValue": total_value,
            "ReorderLevel": reorder_level,
            "DaysOfSupply": days_of_supply
        })
    
    return data

def _generate_generic_data() -> List[Dict[str, Any]]:
    """
    Generate generic simulated data.
    
    Returns:
        List of dictionaries representing generic data
    """
    categories = ["Category A", "Category B", "Category C", "Category D"]
    types = ["Type 1", "Type 2", "Type 3"]
    
    data = []
    
    for i in range(50):
        category = random.choice(categories)
        type_value = random.choice(types)
        
        # Generate generic data
        id_value = f"ID{1000 + i}"
        name = f"Item {i+1}"
        value1 = round(random.uniform(0, 100), 2)
        value2 = round(random.uniform(0, 100), 2)
        value3 = round(random.uniform(0, 100), 2)
        flag = random.choice([True, False])
        
        data.append({
            "ID": id_value,
            "Name": name,
            "Category": category,
            "Type": type_value,
            "Value1": value1,
            "Value2": value2,
            "Value3": value3,
            "Flag": flag
        })
    
    return data

def _analyze_data(data: List[Dict[str, Any]], metadata: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyze the spreadsheet data.
    
    Args:
        data: Spreadsheet data
        metadata: Spreadsheet metadata
        
    Returns:
        Dictionary with analysis results
    """
    # Get basic statistics
    row_count = len(data)
    
    # Get column information
    columns = {}
    if row_count > 0:
        for col_name in data[0].keys():
            # Determine column type
            col_type = _determine_column_type(data, col_name)
            
            # Get column statistics
            col_stats = _get_column_statistics(data, col_name, col_type)
            
            columns[col_name] = {
                "type": col_type,
                "statistics": col_stats
            }
    
    # Generate summary
    summary = {
        "row_count": row_count,
        "column_count": len(columns),
        "columns": columns,
        "metadata": metadata
    }
    
    # Add sample data
    summary["sample_data"] = data[:5] if row_count > 0 else []
    
    return summary

def _determine_column_type(data: List[Dict[str, Any]], column: str) -> str:
    """
    Determine the data type of a column.
    
    Args:
        data: Spreadsheet data
        column: Column name
        
    Returns:
        Data type of the column
    """
    # Check first few non-null values
    for row in data:
        if column in row and row[column] is not None:
            value = row[column]
            
            if isinstance(value, bool):
                return "boolean"
            elif isinstance(value, int):
                return "integer"
            elif isinstance(value, float):
                return "float"
            elif isinstance(value, str):
                # Try to determine if string is a date
                if "-" in value and len(value) >= 8:
                    try:
                        # Very simple date check
                        parts = value.split("-")
                        if len(parts) == 3 and all(part.isdigit() for part in parts):
                            return "date"
                    except:
                        pass
                return "string"
            else:
                return "unknown"
    
    return "unknown"

def _get_column_statistics(data: List[Dict[str, Any]], column: str, col_type: str) -> Dict[str, Any]:
    """
    Get statistics for a column.
    
    Args:
        data: Spreadsheet data
        column: Column name
        col_type: Column data type
        
    Returns:
        Dictionary with column statistics
    """
    # Extract column values
    values = [row[column] for row in data if column in row and row[column] is not None]
    
    # Basic statistics for all types
    stats = {
        "count": len(values),
        "null_count": len(data) - len(values),
        "null_percentage": round(((len(data) - len(values)) / len(data)) * 100, 2) if len(data) > 0 else 0
    }
    
    # Type-specific statistics
    if col_type in ["integer", "float"]:
        if values:
            stats.update({
                "min": min(values),
                "max": max(values),
                "mean": sum(values) / len(values),
                "sum": sum(values)
            })
            
            # Calculate median
            sorted_values = sorted(values)
            mid = len(sorted_values) // 2
            if len(sorted_values) % 2 == 0:
                stats["median"] = (sorted_values[mid-1] + sorted_values[mid]) / 2
            else:
                stats["median"] = sorted_values[mid]
    
    elif col_type == "string":
        if values:
            # Get unique values and their counts
            unique_values = {}
            for value in values:
                if value in unique_values:
                    unique_values[value] += 1
                else:
                    unique_values[value] = 1
            
            stats.update({
                "unique_count": len(unique_values),
                "most_common": max(unique_values.items(), key=lambda x: x[1])[0] if unique_values else None,
                "most_common_count": max(unique_values.values()) if unique_values else 0,
                "min_length": min(len(str(v)) for v in values),
                "max_length": max(len(str(v)) for v in values),
                "avg_length": sum(len(str(v)) for v in values) / len(values)
            })
    
    elif col_type == "boolean":
        if values:
            true_count = sum(1 for v in values if v)
            false_count = len(values) - true_count
            
            stats.update({
                "true_count": true_count,
                "false_count": false_count,
                "true_percentage": round((true_count / len(values)) * 100, 2)
            })
    
    return stats

def _filter_data(
    data: List[Dict[str, Any]],
    filters: Optional[Dict[str, Any]],
    columns: Optional[List[str]]
) -> Dict[str, Any]:
    """
    Filter the spreadsheet data.
    
    Args:
        data: Spreadsheet data
        filters: Filter conditions
        columns: Columns to include
        
    Returns:
        Dictionary with filtered data
    """
    filtered_data = data
    
    # Apply filters if provided
    if filters:
        filtered_rows = []
        
        for row in data:
            matches = True
            
            for column, condition in filters.items():
                if column not in row:
                    matches = False
                    break
                
                value = row[column]
                
                # Handle different condition types
                if isinstance(condition, dict):
                    # Complex condition with operators
                    for op, op_value in condition.items():
                        if op == "eq" and value != op_value:
                            matches = False
                            break
                        elif op == "ne" and value == op_value:
                            matches = False
                            break
                        elif op == "gt" and not (isinstance(value, (int, float)) and value > op_value):
                            matches = False
                            break
                        elif op == "lt" and not (isinstance(value, (int, float)) and value < op_value):
                            matches = False
                            break
                        elif op == "gte" and not (isinstance(value, (int, float)) and value >= op_value):
                            matches = False
                            break
                        elif op == "lte" and not (isinstance(value, (int, float)) and value <= op_value):
                            matches = False
                            break
                        elif op == "contains" and not (isinstance(value, str) and op_value in value):
                            matches = False
                            break
                        elif op == "startswith" and not (isinstance(value, str) and value.startswith(op_value)):
                            matches = False
                            break
                        elif op == "endswith" and not (isinstance(value, str) and value.endswith(op_value)):
                            matches = False
                            break
                else:
                    # Simple equality condition
                    if value != condition:
                        matches = False
                        break
            
            if matches:
                filtered_rows.append(row)
        
        filtered_data = filtered_rows
    
    # Select columns if provided
    if columns:
        filtered_data = [
            {col: row[col] for col in columns if col in row}
            for row in filtered_data
        ]
    
    return {
        "filtered_data": filtered_data,
        "row_count": len(filtered_data),
        "filters_applied": filters,
        "columns_selected": columns
    }

def _aggregate_data(
    data: List[Dict[str, Any]],
    groupby: Optional[List[str]],
    aggregations: Optional[Dict[str, str]]
) -> Dict[str, Any]:
    """
    Aggregate the spreadsheet data.
    
    Args:
        data: Spreadsheet data
        groupby: Columns to group by
        aggregations: Aggregation functions to apply
        
    Returns:
        Dictionary with aggregated data
    """
    if not groupby or not aggregations:
        return {
            "error": "Group by columns and aggregations are required for aggregation"
        }
    
    # Group data
    groups = {}
    
    for row in data:
        # Create group key
        group_values = []
        for col in groupby:
            if col in row:
                group_values.append(str(row[col]))
            else:
                group_values.append("None")
        
        group_key = tuple(group_values)
        
        # Add row to group
        if group_key in groups:
            groups[group_key].append(row)
        else:
            groups[group_key] = [row]
    
    # Apply aggregations
    result = []
    
    for group_key, group_rows in groups.items():
        group_result = {}
        
        # Add group by columns
        for i, col in enumerate(groupby):
            group_result[col] = group_key[i]
        
        # Apply aggregations
        for col, agg_func in aggregations.items():
            # Extract values
            values = [row[col] for row in group_rows if col in row and row[col] is not None]
            
            if not values:
                group_result[f"{col}_{agg_func}"] = None
                continue
            
            # Apply aggregation function
            if agg_func == "sum":
                group_result[f"{col}_{agg_func}"] = sum(values)
            elif agg_func == "avg":
                group_result[f"{col}_{agg_func}"] = sum(values) / len(values)
            elif agg_func == "min":
                group_result[f"{col}_{agg_func}"] = min(values)
            elif agg_func == "max":
                group_result[f"{col}_{agg_func}"] = max(values)
            elif agg_func == "count":
                group_result[f"{col}_{agg_func}"] = len(values)
            elif agg_func == "first":
                group_result[f"{col}_{agg_func}"] = values[0]
            elif agg_func == "last":
                group_result[f"{col}_{agg_func}"] = values[-1]
        
        result.append(group_result)
    
    return {
        "aggregated_data": result,
        "group_count": len(result),
        "groupby_columns": groupby,
        "aggregations_applied": aggregations
    }

def _pivot_data(
    data: List[Dict[str, Any]],
    groupby: List[str],
    columns: List[str],
    aggregations: Dict[str, str]
) -> Dict[str, Any]:
    """
    Create a pivot table from the spreadsheet data.
    
    Args:
        data: Spreadsheet data
        groupby: Columns to group by (rows)
        columns: Columns to pivot (columns)
        aggregations: Aggregation functions to apply
        
    Returns:
        Dictionary with pivot table data
    """
    if not groupby or not columns or not aggregations:
        return {
            "error": "Group by columns, pivot columns, and aggregations are required for pivot tables"
        }
    
    # This is a simplified pivot table implementation
    # In a real implementation, this would be more sophisticated
    
    # First, aggregate the data
    agg_result = _aggregate_data(data, groupby + columns, aggregations)
    
    # Then, pivot the result
    pivot_data = {}
    column_values = {}
    
    # Collect unique column values
    for row in agg_result["aggregated_data"]:
        for col in columns:
            if col in row:
                if col not in column_values:
                    column_values[col] = set()
                column_values[col].add(row[col])
    
    # Create pivot table
    for row in agg_result["aggregated_data"]:
        # Create row key
        row_key = tuple(row[col] for col in groupby if col in row)
        
        # Create column key
        col_key = tuple(row[col] for col in columns if col in row)
        
        # Get aggregation values
        for agg_col, agg_func in aggregations.items():
            agg_key = f"{agg_col}_{agg_func}"
            
            if agg_key in row:
                # Add to pivot data
                if row_key not in pivot_data:
                    pivot_data[row_key] = {}
                
                pivot_data[row_key][col_key] = row[agg_key]
    
    # Convert to list format
    result = []
    
    for row_key, row_data in pivot_data.items():
        row_result = {}
        
        # Add row keys
        for i, col in enumerate(groupby):
            row_result[col] = row_key[i] if i < len(row_key) else None
        
        # Add column values
        for col_key, value in row_data.items():
            col_name = "_".join(str(v) for v in col_key)
            row_result[col_name] = value
        
        result.append(row_result)
    
    return {
        "pivot_data": result,
        "row_count": len(result),
        "row_dimensions": groupby,
        "column_dimensions": columns,
        "aggregations_applied": aggregations
    }

def _describe_data(
    data: List[Dict[str, Any]],
    columns: Optional[List[str]]
) -> Dict[str, Any]:
    """
    Generate descriptive statistics for the spreadsheet data.
    
    Args:
        data: Spreadsheet data
        columns: Columns to describe
        
    Returns:
        Dictionary with descriptive statistics
    """
    # If columns not specified, use all numeric columns
    if not columns:
        columns = []
        if data:
            for col, value in data[0].items():
                if isinstance(value, (int, float)):
                    columns.append(col)
    
    # Calculate statistics for each column
    stats = {}
    
    for col in columns:
        # Extract values
        values = [row[col] for row in data if col in row and row[col] is not None and isinstance(row[col], (int, float))]
        
        if not values:
            continue
        
        # Calculate statistics
        count = len(values)
        mean = sum(values) / count
        
        # Calculate variance and standard deviation
        variance = sum((x - mean) ** 2 for x in values) / count
        std_dev = variance ** 0.5
        
        # Calculate percentiles
        sorted_values = sorted(values)
        
        def percentile(p):
            k = (count - 1) * p
            f = int(k)
            c = k - f
            if f + 1 < count:
                return sorted_values[f] + c * (sorted_values[f+1] - sorted_values[f])
            else:
                return sorted_values[f]
        
        stats[col] = {
            "count": count,
            "mean": mean,
            "std": std_dev,
            "min": min(values),
            "25%": percentile(0.25),
            "50%": percentile(0.5),
            "75%": percentile(0.75),
            "max": max(values)
        }
    
    return {
        "descriptive_statistics": stats,
        "columns_analyzed": list(stats.keys())
    }

def _correlate_data(
    data: List[Dict[str, Any]],
    columns: Optional[List[str]]
) -> Dict[str, Any]:
    """
    Calculate correlations between columns.
    
    Args:
        data: Spreadsheet data
        columns: Columns to correlate
        
    Returns:
        Dictionary with correlation matrix
    """
    # If columns not specified, use all numeric columns
    if not columns:
        columns = []
        if data:
            for col, value in data[0].items():
                if isinstance(value, (int, float)):
                    columns.append(col)
    
    # Calculate correlation matrix
    correlation_matrix = {}
    
    for col1 in columns:
        correlation_matrix[col1] = {}
        
        for col2 in columns:
            # Extract paired values
            pairs = [
                (row[col1], row[col2])
                for row in data
                if col1 in row and col2 in row
                and row[col1] is not None and row[col2] is not None
                and isinstance(row[col1], (int, float)) and isinstance(row[col2], (int, float))
            ]
            
            if not pairs:
                correlation_matrix[col1][col2] = None
                continue
            
            # Calculate correlation coefficient
            x_values = [p[0] for p in pairs]
            y_values = [p[1] for p in pairs]
            
            n = len(pairs)
            
            if n <= 1:
                correlation_matrix[col1][col2] = None
                continue
            
            # Calculate means
            x_mean = sum(x_values) / n
            y_mean = sum(y_values) / n
            
            # Calculate covariance and variances
            covariance = sum((x - x_mean) * (y - y_mean) for x, y in pairs) / n
            x_variance = sum((x - x_mean) ** 2 for x in x_values) / n
            y_variance = sum((y - y_mean) ** 2 for y in y_values) / n
            
            # Calculate correlation coefficient
            if x_variance > 0 and y_variance > 0:
                correlation = covariance / ((x_variance * y_variance) ** 0.5)
            else:
                correlation = None
            
            correlation_matrix[col1][col2] = correlation
    
    return {
        "correlation_matrix": correlation_matrix,
        "columns_analyzed": columns
    }

def _format_output(result: Dict[str, Any], output_format: str) -> Any:
    """
    Format the output in the specified format.
    
    Args:
        result: Result to format
        output_format: Output format
        
    Returns:
        Formatted result
    """
    # In a real implementation, this would convert to different formats
    # For now, we'll just return the result as is
    
    if output_format == "json":
        return result
    elif output_format == "csv":
        # Simulate CSV output
        return {"format": "csv", "data": result}
    elif output_format == "html":
        # Simulate HTML output
        return {"format": "html", "data": result}
    else:
        return result

def _save_result(result: Any, output_path: str, output_format: str) -> None:
    """
    Save the result to a file.
    
    Args:
        result: Result to save
        output_path: Path to save the result
        output_format: Output format
    """
    # In a real implementation, this would actually save the file
    # For now, we'll just simulate it
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Simulate saving
    logger.info(f"Would save result to {output_path} in {output_format} format")

def _get_iso_time(days_ago: int = 0) -> str:
    """
    Get ISO formatted time string.
    
    Args:
        days_ago: Number of days to subtract from current time
        
    Returns:
        ISO formatted time string
    """
    current_time = time.time() - (days_ago * 86400)  # 86400 seconds in a day
    return time.strftime("%Y-%m-%dT%H:%M:%S.000Z", time.gmtime(current_time))

def _generate_analysis_summary(result: Dict[str, Any], operation: str) -> str:
    """
    Generate a summary of the analysis results for memory storage.
    
    Args:
        result: Analysis result
        operation: Operation performed
        
    Returns:
        Summary string
    """
    if operation == "analyze":
        return f"Analyzed spreadsheet with {result.get('row_count', 0)} rows and {result.get('column_count', 0)} columns."
    
    elif operation == "filter":
        return f"Filtered data resulting in {result.get('row_count', 0)} rows."
    
    elif operation == "aggregate":
        return f"Aggregated data into {result.get('group_count', 0)} groups."
    
    elif operation == "pivot":
        return f"Created pivot table with {result.get('row_count', 0)} rows."
    
    elif operation == "describe":
        columns = result.get('columns_analyzed', [])
        return f"Generated descriptive statistics for {len(columns)} columns."
    
    elif operation == "correlate":
        columns = result.get('columns_analyzed', [])
        return f"Calculated correlation matrix for {len(columns)} columns."
    
    return f"Performed {operation} operation on spreadsheet data."

# Define supported operations
SUPPORTED_OPERATIONS = [
    "analyze",
    "filter",
    "aggregate",
    "pivot",
    "describe",
    "correlate"
]
