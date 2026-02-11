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
    # Validate API key format
    if not ANTHROPIC_API_KEY.startswith("sk-ant-"):
        print(f"⚠️  Warning: Anthropic API key format seems invalid (should start with 'sk-ant-')")
        print(f"   Key starts with: {ANTHROPIC_API_KEY[:10]}...")
    else:
        try:
            anthropic_client = Anthropic(api_key=ANTHROPIC_API_KEY)
            print("✅ Anthropic client initialized successfully")
        except Exception as e:
            print(f"❌ Failed to initialize Anthropic client: {e}")
else:
    print("⚠️  ANTHROPIC_API_KEY not found in environment variables")
    print("   LLM features will use fallback method")
    print("   To enable LLM: Create .env file with ANTHROPIC_API_KEY=sk-ant-your-key")


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


def learn_quote_with_llm(quote_data: Dict) -> str:
    """
    Learn from a quote using LLM to extract patterns and insights.
    
    Args:
        quote_data: Dictionary with quote items and total amount
        
    Returns:
        Learning summary as string
    """
    if not anthropic_client:
        return "LLM not configured (ANTHROPIC_API_KEY not set)"
    
    try:
        items = quote_data.get('items', [])
        total_amount = quote_data.get('total_amount', 0)
        
        # Format items for LLM
        items_text = "\n".join([
            f"- {item.get('name', '')}: 단가 {item.get('unit_price', 0):,}원 × {item.get('quantity', 1)} = {item.get('amount', 0):,}원"
            for item in items
        ])
        
        prompt = f"""다음은 업로드된 견적서입니다. 이 견적서의 패턴과 특징을 분석하여 학습하세요.

총 예산: {total_amount:,}원

항목별 상세:
{items_text}

이 견적서에서 학습할 수 있는 주요 패턴, 항목별 가격 범위, 그리고 향후 견적 생성에 활용할 수 있는 인사이트를 요약해주세요.
한국어로 간결하게 작성해주세요."""

        message = anthropic_client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1000,
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )
        
        return message.content[0].text
    except Exception as e:
        print(f"Error in LLM learning: {e}")
        return f"LLM 학습 중 오류 발생: {str(e)}"


def generate_quote_from_requirements(requirements: str, historical_quotes: List[Dict]) -> Dict:
    """
    Generate a new quote based on requirements and historical quotes using LLM.
    
    Args:
        requirements: Text description of requirements
        historical_quotes: List of historical quote dictionaries
        
    Returns:
        Dictionary with generated quote items and total amount
    """
    print(f"🔍 Generating quote with LLM...")
    print(f"   Requirements: {requirements[:100]}...")
    print(f"   Historical quotes count: {len(historical_quotes)}")
    print(f"   Anthropic client available: {anthropic_client is not None}")
    print(f"   API Key set: {ANTHROPIC_API_KEY is not None and ANTHROPIC_API_KEY != ''}")
    
    if not anthropic_client:
        print("⚠️  Anthropic client not available, using fallback method")
        # Fallback to simple pattern matching if LLM not available
        return _generate_quote_simple(requirements, historical_quotes)
    
    print("✅ Using Anthropic Claude API for quote generation...")
    
    try:
        # Prepare historical data for LLM
        historical_context = []
        for quote in historical_quotes[:10]:  # Limit to 10 most recent
            if quote.get('items'):
                items = json.loads(quote['items']) if isinstance(quote['items'], str) else quote['items']
                items_text = "\n".join([
                    f"- {item.get('name', '')}: {item.get('unit_price', 0):,}원 × {item.get('quantity', 1)} = {item.get('amount', 0):,}원"
                    for item in items
                ])
                historical_context.append(f"총액: {quote.get('total_amount', 0):,}원\n{items_text}")
        
        historical_examples = "\n\n---\n\n".join(historical_context) if historical_context else "과거 견적서가 없습니다."
        
        prompt = f"""당신은 견적서 생성 전문가입니다. 사용자의 요구사항을 바탕으로 과거 견적서 패턴을 학습하여 새로운 견적을 생성해주세요.

요구사항:
{requirements}

과거 견적서 예시 (학습 참고용):
{historical_examples}

위의 과거 견적서 패턴을 참고하여, 요구사항에 맞는 견적서를 생성해주세요.

응답 형식은 반드시 다음 JSON 형식으로 해주세요:
{{
  "items": [
    {{"name": "항목명", "unit_price": 단가(숫자), "quantity": 수량(숫자), "amount": 금액(숫자)}},
    ...
  ],
  "total_amount": 총액(숫자)
}}

중요:
- 모든 금액은 원화(KRW) 기준입니다
- 단가는 정수로, 금액도 정수로 표시해주세요
- 수량도 정수로 표시해주세요
- 과거 견적서의 가격 패턴을 참고하여 현실적인 가격을 제시해주세요
- JSON만 응답하고 다른 설명은 포함하지 마세요"""

        print("📤 Sending request to Anthropic Claude API...")
        message = anthropic_client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=2000,
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )
        
        print("✅ Received response from Anthropic Claude API")
        
        # Parse LLM response
        response_text = message.content[0].text.strip()
        print(f"📝 LLM Response (first 200 chars): {response_text[:200]}...")
        
        # Extract JSON from response (handle markdown code blocks)
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()
        
        print(f"📋 Extracted JSON: {response_text[:200]}...")
        
        # Parse JSON
        quote_data = json.loads(response_text)
        print(f"✅ Successfully parsed LLM response: {len(quote_data.get('items', []))} items, total: {quote_data.get('total_amount', 0):,}원")
        
        # Validate and format
        items = quote_data.get('items', [])
        total_amount = quote_data.get('total_amount', 0)
        
        # Ensure all amounts are integers
        for item in items:
            item['unit_price'] = int(item.get('unit_price', 0))
            item['quantity'] = int(item.get('quantity', 1))
            item['amount'] = int(item.get('amount', item['unit_price'] * item['quantity']))
        
        total_amount = int(total_amount)
        
        return {
            'items': items,
            'total_amount': total_amount
        }
        
    except json.JSONDecodeError as e:
        print(f"❌ JSON parsing error: {e}")
        print(f"   Full response was: {response_text}")
        print("⚠️  Falling back to simple generation method")
        # Fallback to simple generation
        return _generate_quote_simple(requirements, historical_quotes)
    except Exception as e:
        error_type = type(e).__name__
        print(f"❌ Error in LLM quote generation: {error_type}: {e}")
        
        # Check for authentication errors
        if "AuthenticationError" in error_type or "401" in str(e) or "invalid" in str(e).lower():
            print("🔑 API Key authentication failed!")
            print("   Please check your ANTHROPIC_API_KEY in .env file")
            print("   Key should start with 'sk-ant-' and be valid")
        
        traceback.print_exc()
        print("⚠️  Falling back to simple generation method")
        # Fallback to simple generation
        return _generate_quote_simple(requirements, historical_quotes)


def _generate_quote_simple(requirements: str, historical_quotes: List[Dict]) -> Dict:
    """
    Simple fallback quote generation without LLM.
    """
    print("📝 Using simple pattern matching (fallback method)")
    import re
    requirements_lower = requirements.lower()
    
    # Extract participant count
    participant_match = re.search(r'(\d+)명', requirements)
    participants = int(participant_match.group(1)) if participant_match else 50
    
    # Extract days
    day_match = re.search(r'(\d+)일', requirements)
    days = int(day_match.group(1)) if day_match else 1
    
    generated_items = []
    total_amount = 0
    
    # Basic item generation
    if '강의실' in requirements_lower or 'classroom' in requirements_lower:
        room_count = requirements_lower.count('강의실') or requirements_lower.count('classroom') or 1
        room_price = 50000 * room_count
        generated_items.append({
            'name': f'강의실 대여 ({room_count}개)',
            'unit_price': 50000,
            'quantity': room_count,
            'amount': room_price
        })
        total_amount += room_price
    
    if '식사' in requirements_lower or 'meal' in requirements_lower:
        meal_price = 15000 * participants
        generated_items.append({
            'name': f'식사 제공 ({participants}명)',
            'unit_price': 15000,
            'quantity': participants,
            'amount': meal_price
        })
        total_amount += meal_price
    
    if '숙박' in requirements_lower or 'hotel' in requirements_lower:
        hotel_price = 80000 * participants * days
        generated_items.append({
            'name': f'호텔 숙박 ({participants}명 × {days}일)',
            'unit_price': 80000,
            'quantity': participants * days,
            'amount': hotel_price
        })
        total_amount += hotel_price
    
    if not generated_items:
        generated_items.append({
            'name': '프로젝트 예산',
            'unit_price': 1000000,
            'quantity': 1,
            'amount': 1000000
        })
        total_amount = 1000000
    
    return {
        'items': generated_items,
        'total_amount': total_amount
    }

