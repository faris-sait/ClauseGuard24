from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
import os
from dotenv import load_dotenv
from typing import List, Dict, Any, Optional
import requests
from bs4 import BeautifulSoup
import json
import re
from urllib.parse import urljoin, urlparse
import time
from pymongo import MongoClient

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="ClauseGuard API",
    description="API for analyzing Terms of Service and Privacy Policies",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB connection
mongo_url = os.environ.get('MONGO_URL')
if mongo_url:
    client = MongoClient(mongo_url)
    db = client.clauseguard
    analyses_collection = db.analyses
else:
    client = None
    db = None
    analyses_collection = None

# OpenAI setup  
from openai import OpenAI
openai_client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))

# Request models
class AnalyzeRequest(BaseModel):
    url: HttpUrl

class AnalysisResponse(BaseModel):
    url: str
    title: str
    summary: List[str]
    risks: List[Dict[str, Any]]
    risk_score: int
    analysis_time: float

# Risk categories and their weights
RISK_CATEGORIES = {
    "data_sharing": {
        "name": "Data Sharing with Third Parties",
        "description": "Your personal data may be shared with external companies",
        "weight": 20,
        "keywords": ["share", "third party", "partner", "affiliate", "vendor", "service provider"]
    },
    "arbitration": {
        "name": "Mandatory Arbitration",
        "description": "You cannot sue the company in court, only through arbitration",
        "weight": 25,
        "keywords": ["arbitration", "binding arbitration", "dispute resolution", "no class action", "waive"]
    },
    "auto_renewal": {
        "name": "Automatic Subscription Renewal",
        "description": "Your subscription will automatically renew and charge you",
        "weight": 15,
        "keywords": ["auto-renew", "automatic renewal", "recurring", "subscription", "billing cycle"]
    },
    "no_liability": {
        "name": "Limited Company Liability",
        "description": "Company limits or excludes their liability for damages",
        "weight": 15,
        "keywords": ["no liability", "disclaim", "not liable", "exclude liability", "limitation of damages"]
    },
    "tracking": {
        "name": "Extensive Tracking & Advertising",
        "description": "Comprehensive tracking of your behavior for advertising",
        "weight": 10,
        "keywords": ["cookies", "tracking", "analytics", "advertising", "behavioral", "personalized ads"]
    },
    "content_rights": {
        "name": "Content Rights and Ownership",
        "description": "Company claims rights to content you create or upload",
        "weight": 10,
        "keywords": ["intellectual property", "license", "content ownership", "user content", "grant rights"]
    },
    "account_termination": {
        "name": "Account Termination Rights",
        "description": "Company can terminate your account without notice",
        "weight": 5,
        "keywords": ["terminate", "suspend", "disable account", "at our discretion", "without notice"]
    }
}

def extract_text_from_url(url: str) -> tuple[str, str]:
    """Extract text content from a given URL"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(str(url), headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "header", "footer", "aside"]):
            script.decompose()
        
        # Try to find the main content area
        main_content = None
        content_selectors = [
            'main', '[role="main"]', '.main-content', '.content', 
            '.terms', '.privacy', '.policy', '.legal', 'article'
        ]
        
        for selector in content_selectors:
            main_content = soup.select_one(selector)
            if main_content:
                break
        
        if not main_content:
            main_content = soup.find('body')
        
        if main_content:
            text = main_content.get_text()
        else:
            text = soup.get_text()
        
        # Clean up the text
        text = ' '.join(text.split())
        
        # Get title
        title_elem = soup.find('title')
        title = title_elem.get_text().strip() if title_elem else urlparse(str(url)).netloc
        
        return text, title
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error extracting content from URL: {str(e)}")

def analyze_with_gpt(text: str, title: str) -> Dict[str, Any]:
    """Analyze the terms and conditions text using OpenAI GPT"""
    try:
        # Create the prompt for analysis
        prompt = f"""
        Analyze the following Terms & Conditions or Privacy Policy document and provide:

        1. A summary of the key points in plain language (3-5 bullet points)
        2. Identify specific risky clauses in these categories:
           - Data Sharing with Third Parties
           - Mandatory Arbitration 
           - Automatic Subscription Renewal
           - Limited Company Liability
           - Extensive Tracking & Advertising
           - Content Rights and Ownership
           - Account Termination Rights

        For each risk found, provide:
        - The category name
        - A brief explanation of the risk
        - The specific text excerpt (if found)
        - A severity score from 1-10

        Document Title: {title}
        
        Document Text: {text[:4000]}...

        Please respond in JSON format:
        {{
            "summary": ["point 1", "point 2", "point 3"],
            "risks": [
                {{
                    "category": "category_name",
                    "title": "Risk Title",
                    "description": "What this means for users",
                    "excerpt": "Relevant text from document",
                    "severity": 7
                }}
            ]
        }}
        """

        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a legal expert specialized in analyzing Terms of Service, Privacy Policies, and EULAs. Provide clear, accurate analysis in the requested JSON format."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=2000,
            temperature=0.1
        )
        
        # Parse the JSON response
        content = response.choices[0].message.content
        
        # Clean up the response to extract JSON
        json_start = content.find('{')
        json_end = content.rfind('}') + 1
        json_str = content[json_start:json_end]
        
        analysis = json.loads(json_str)
        return analysis
        
    except Exception as e:
        # If AI analysis fails, provide a fallback pattern-based analysis
        print(f"AI analysis failed: {e}, using fallback analysis")
        return analyze_with_fallback(text, title)

def analyze_with_fallback(text: str, title: str) -> Dict[str, Any]:
    """Fallback analysis using pattern matching when AI is unavailable"""
    text_lower = text.lower()
    
    # Pattern-based risk detection
    risks = []
    
    # Check for data sharing
    if any(keyword in text_lower for keyword in ["share", "third party", "partner", "affiliate"]):
        risks.append({
            "category": "data_sharing",
            "title": "Data Sharing with Third Parties",
            "description": "This document indicates your data may be shared with external companies",
            "excerpt": "Data sharing terms detected in document",
            "severity": 6
        })
    
    # Check for arbitration
    if any(keyword in text_lower for keyword in ["arbitration", "binding arbitration", "dispute resolution"]):
        risks.append({
            "category": "arbitration", 
            "title": "Mandatory Arbitration",
            "description": "You may be required to resolve disputes through arbitration instead of courts",
            "excerpt": "Arbitration clauses detected in document",
            "severity": 7
        })
    
    # Check for auto renewal
    if any(keyword in text_lower for keyword in ["auto-renew", "automatic renewal", "recurring"]):
        risks.append({
            "category": "auto_renewal",
            "title": "Automatic Subscription Renewal", 
            "description": "Your subscription may automatically renew and charge you",
            "excerpt": "Auto-renewal terms detected in document",
            "severity": 5
        })
    
    # Check for liability limitations
    if any(keyword in text_lower for keyword in ["no liability", "disclaim", "not liable", "limitation of damages"]):
        risks.append({
            "category": "no_liability",
            "title": "Limited Company Liability",
            "description": "The company limits or excludes their liability for damages",
            "excerpt": "Liability limitation clauses detected in document", 
            "severity": 6
        })
    
    # Check for tracking
    if any(keyword in text_lower for keyword in ["cookies", "tracking", "analytics", "advertising"]):
        risks.append({
            "category": "tracking",
            "title": "Extensive Tracking & Advertising",
            "description": "The service may track your behavior for advertising purposes",
            "excerpt": "Tracking and advertising terms detected in document",
            "severity": 4
        })
    
    return {
        "summary": [
            "This is a legal document that governs your use of the service",
            "Terms include various rights and obligations for users",
            "Pattern-based analysis has identified several potential risk areas",
            "For detailed legal advice, please consult with a qualified attorney"
        ],
        "risks": risks
    }

def calculate_risk_score(risks: List[Dict[str, Any]]) -> int:
    """Calculate overall risk score based on identified risks"""
    total_score = 0
    max_possible_score = 100
    
    for risk in risks:
        category = risk.get('category', '').lower().replace(' ', '_')
        severity = risk.get('severity', 5)
        
        if category in RISK_CATEGORIES:
            weight = RISK_CATEGORIES[category]['weight']
            risk_contribution = (severity / 10) * weight
            total_score += risk_contribution
    
    # Normalize to 0-100 scale
    risk_score = min(int(total_score), 100)
    return risk_score

# Add root endpoint for health check
@app.get("/")
async def root():
    """Root endpoint - API health check"""
    return {
        "message": "ClauseGuard API is running",
        "status": "healthy",
        "version": "1.0.0",
        "endpoints": {
            "health": "/",
            "api_info": "/api/",
            "analyze": "/api/analyze",
            "docs": "/docs"
        }
    }

@app.get("/api/")
async def api_info():
    """API information endpoint"""
    return {
        "message": "ClauseGuard API - Protecting you from hidden risks",
        "description": "API for analyzing Terms of Service and Privacy Policies",
        "version": "1.0.0"
    }

# Add health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "database": "connected" if analyses_collection is not None else "not configured",
        "openai": "configured" if os.environ.get('OPENAI_API_KEY') else "not configured"
    }

@app.post("/api/analyze", response_model=AnalysisResponse)
async def analyze_terms(request: AnalyzeRequest):
    """Analyze terms and conditions from a given URL"""
    start_time = time.time()
    
    try:
        # Extract text from URL
        text, title = extract_text_from_url(str(request.url))
        
        if len(text) < 100:
            raise HTTPException(status_code=400, detail="Document appears to be too short or empty")
        
        # Analyze with GPT
        analysis = analyze_with_gpt(text, title)
        
        # Calculate risk score
        risk_score = calculate_risk_score(analysis.get('risks', []))
        
        # Prepare response
        response = AnalysisResponse(
            url=str(request.url),
            title=title,
            summary=analysis.get('summary', []),
            risks=analysis.get('risks', []),
            risk_score=risk_score,
            analysis_time=time.time() - start_time
        )
        
        # Save to database if available
        if analyses_collection is not None:
            try:
                analyses_collection.insert_one({
                    "url": str(request.url),
                    "title": title,
                    "summary": analysis.get('summary', []),
                    "risks": analysis.get('risks', []),
                    "risk_score": risk_score,
                    "analysis_time": time.time() - start_time,
                    "created_at": time.time()
                })
            except Exception as e:
                print(f"Database save error: {e}")
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
