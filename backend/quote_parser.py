"""Quote file parser for Excel and CSV files with LLM learning."""

import pandas as pd
import json
import os
import traceback
from pathlib import Path
from typing import List, Dict, Optional
from dotenv import load_dotenv
from anthropic import Anthropic

# Load environment variables
load_dotenv()

# Initialize Anthropic client
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
anthropic_client = None
if ANTHROPIC_API_KEY:
    anthropic_client = Anthropic(api_key=ANTHROPIC_API_KEY)


def parse_quote_file(file_path: str) -> Dict:
    """
    Parse a quote file (Excel or CSV) and extract quote items.
    
    Args:
        file_path: Path to the quote file
        
    Returns:
        Dictionary with quote data including items and total amount
    """
    file_ext = Path(file_path).suffix.lower()
    
    try:
        if file_ext in ['.xlsx', '.xls']:
            # Read Excel file
            df = pd.read_excel(file_path)
        elif file_ext == '.csv':
            # Read CSV file
            df = pd.read_csv(file_path, encoding='utf-8-sig')
        else:
            raise ValueError(f"Unsupported file format: {file_ext}")
        
        # Try to identify columns (flexible matching)
        items = []
        total_amount = 0
        
        # Common column name patterns
        name_cols = ['항목', 'item', 'name', '품목', '내용', 'description']
        price_cols = ['단가', 'price', 'unit_price', '단가(원)', '금액']
        quantity_cols = ['수량', 'quantity', 'qty', '개수']
        amount_cols = ['금액', 'amount', '합계', 'total', '소계']
        
        # Find actual column names
        name_col = None
        price_col = None
        quantity_col = None
        amount_col = None
        
        for col in df.columns:
            col_lower = str(col).lower()
            if not name_col and any(pattern in col_lower for pattern in name_cols):
                name_col = col
            if not price_col and any(pattern in col_lower for pattern in price_cols):
                price_col = col
            if not quantity_col and any(pattern in col_lower for pattern in quantity_cols):
                quantity_col = col
            if not amount_col and any(pattern in col_lower for pattern in amount_cols):
                amount_col = col
        
        # If columns not found, use first few columns as fallback
        if not name_col:
            name_col = df.columns[0]
        if not price_col and len(df.columns) > 1:
            price_col = df.columns[1]
        if not quantity_col and len(df.columns) > 2:
            quantity_col = df.columns[2]
        if not amount_col and len(df.columns) > 3:
            amount_col = df.columns[3]
        
        # Extract items
        for idx, row in df.iterrows():
            try:
                name = str(row[name_col]) if name_col else f"항목 {idx + 1}"
                
                # Skip empty rows or header-like rows
                if pd.isna(row[name_col]) or name.lower() in ['항목', 'item', 'name', '합계', 'total', '총계']:
                    continue
                
                unit_price = 0
                quantity = 1
                amount = 0
                
                if price_col and pd.notna(row[price_col]):
                    try:
                        unit_price = int(float(str(row[price_col]).replace(',', '').replace('원', '').strip()))
                    except:
                        unit_price = 0
                
                if quantity_col and pd.notna(row[quantity_col]):
                    try:
                        quantity = int(float(str(row[quantity_col]).replace(',', '').strip()))
                    except:
                        quantity = 1
                
                if amount_col and pd.notna(row[amount_col]):
                    try:
                        amount = int(float(str(row[amount_col]).replace(',', '').replace('원', '').strip()))
                    except:
                        amount = unit_price * quantity
                else:
                    amount = unit_price * quantity
                
                items.append({
                    'name': name,
                    'unit_price': unit_price,
                    'quantity': quantity,
                    'amount': amount
                })
                
                total_amount += amount
                
            except Exception as e:
                print(f"Error parsing row {idx}: {e}")
                continue
        
        return {
            'items': items,
            'total_amount': total_amount,
            'item_count': len(items)
        }
        
    except Exception as e:
        raise ValueError(f"Failed to parse quote file: {str(e)}")


def generate_quote_from_requirements(requirements: str, historical_quotes: List[Dict]) -> Dict:
    """
    Generate a new quote based on requirements and historical quotes.
    
    This is a simple pattern-matching approach. In production, you'd use ML/AI.
    
    Args:
        requirements: Text description of requirements
        historical_quotes: List of historical quote dictionaries
        
    Returns:
        Dictionary with generated quote items and total amount
    """
    # Extract keywords from requirements
    requirements_lower = requirements.lower()
    
    # Common item patterns from historical data
    item_patterns = {}
    price_ranges = {}
    
    # Analyze historical quotes to find patterns
    for quote in historical_quotes:
        if quote.get('items'):
            items = json.loads(quote['items']) if isinstance(quote['items'], str) else quote['items']
            for item in items:
                item_name = item.get('name', '').lower()
                unit_price = item.get('unit_price', 0)
                
                # Build pattern database
                for keyword in ['세미나', '강의', '회의', '식사', '숙박', '장소', '장비', '인쇄', '운송']:
                    if keyword in item_name:
                        if keyword not in item_patterns:
                            item_patterns[keyword] = []
                        item_patterns[keyword].append(unit_price)
    
    # Calculate average prices per pattern
    avg_prices = {}
    for keyword, prices in item_patterns.items():
        if prices:
            avg_prices[keyword] = sum(prices) / len(prices)
    
    # Generate quote items based on requirements
    generated_items = []
    total_amount = 0
    
    # Simple keyword matching and item generation
    if '세미나' in requirements_lower or 'seminar' in requirements_lower:
        # Estimate number of participants
        import re
        participant_match = re.search(r'(\d+)명', requirements)
        participants = int(participant_match.group(1)) if participant_match else 50
        
        # Add common seminar items
        if '강의실' in requirements_lower or 'classroom' in requirements_lower:
            room_count = requirements_lower.count('강의실') or requirements_lower.count('classroom') or 1
            room_price = avg_prices.get('장소', 50000) * room_count
            generated_items.append({
                'name': f'강의실 대여 ({room_count}개)',
                'unit_price': int(room_price / room_count),
                'quantity': room_count,
                'amount': int(room_price)
            })
            total_amount += int(room_price)
        
        if '식사' in requirements_lower or 'meal' in requirements_lower:
            meal_price = avg_prices.get('식사', 15000) * participants
            generated_items.append({
                'name': f'식사 제공 ({participants}명)',
                'unit_price': int(avg_prices.get('식사', 15000)),
                'quantity': participants,
                'amount': int(meal_price)
            })
            total_amount += int(meal_price)
        
        if '숙박' in requirements_lower or 'hotel' in requirements_lower:
            # Estimate days
            day_match = re.search(r'(\d+)일', requirements)
            days = int(day_match.group(1)) if day_match else 1
            
            hotel_price = avg_prices.get('숙박', 80000) * participants * days
            generated_items.append({
                'name': f'호텔 숙박 ({participants}명 × {days}일)',
                'unit_price': int(avg_prices.get('숙박', 80000)),
                'quantity': participants * days,
                'amount': int(hotel_price)
            })
            total_amount += int(hotel_price)
    
    # If no items generated, create a basic estimate
    if not generated_items:
        # Default estimate based on requirements length and keywords
        base_amount = 1000000  # 1 million KRW base
        if '대규모' in requirements_lower or 'large' in requirements_lower:
            base_amount *= 3
        elif '소규모' in requirements_lower or 'small' in requirements_lower:
            base_amount *= 0.5
        
        generated_items.append({
            'name': '프로젝트 예산',
            'unit_price': int(base_amount),
            'quantity': 1,
            'amount': int(base_amount)
        })
        total_amount = int(base_amount)
    
    return {
        'items': generated_items,
        'total_amount': total_amount
    }

