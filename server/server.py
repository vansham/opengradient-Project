from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
import opengradient as og
from web3 import Web3

# Load environment
load_dotenv()

# Initialize OpenGradient client using environment variable
PRIVATE_KEY = os.getenv('OG_PRIVATE_KEY')
if not PRIVATE_KEY:
    raise ValueError("OG_PRIVATE_KEY environment variable not set")

# Add 0x prefix if not present
if not PRIVATE_KEY.startswith('0x'):
    PRIVATE_KEY = '0x' + PRIVATE_KEY

client = og.Client(private_key=PRIVATE_KEY)

# Ensure approval on startup
try:
    print("Ensuring OPG token approval...")
    opg_amount = Web3.to_wei(0.1, 'ether')
    approval = client.llm.ensure_opg_approval(opg_amount)
    print(f"✅ Approved: {approval.tx_hash}")
except Exception as e:
    print(f"Note: {e}")

app = Flask(__name__)
CORS(app)

# Health check
@app.route("/")
def home():
    return jsonify({"status": "OpenGradient AI Auditor - LIVE ✅"})

# Simple AI chat
@app.route("/ask", methods=["POST"])
def ask_ai():
    try:
        data = request.json
        prompt = data.get("prompt")
        
        if not prompt:
            return jsonify({"error": "prompt required"}), 400
        
        result = client.llm.chat(
            model="openai/gpt-4o",
            messages=[{"role": "user", "content": prompt}]
        )
        
        return jsonify({
            "success": True,
            "response": result.chat_output['content']
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# Smart contract security audit
@app.route("/audit", methods=["POST"])
def audit_contract():
    try:
        data = request.json
        contract_code = data.get("contract_code")
        
        if not contract_code:
            return jsonify({"error": "contract_code required"}), 400
        
        prompt = f"""Analyze this Solidity smart contract for security vulnerabilities:

{contract_code[:2000]}

Check for:
1. Reentrancy attacks
2. Access control issues
3. Integer overflow/underflow
4. Unchecked external calls
5. Front-running vulnerabilities

Respond EXACTLY in this format:
SCORE: [0-100]
CRITICAL: [number]
HIGH: [number]
MEDIUM: [number]
SUMMARY: [one line summary]
ISSUES: [comma-separated list]"""
        
        result = client.llm.chat(
            model="openai/gpt-4o",
            messages=[
                {"role": "system", "content": "You are an expert smart contract security auditor."},
                {"role": "user", "content": prompt}
            ]
        )
        
        ai_response = result.chat_output['content']
        
        # Parse response
        audit = {
            "raw": ai_response,
            "score": 50,
            "critical": 0,
            "high": 0,
            "medium": 0,
            "summary": "Analysis complete"
        }
        
        for line in ai_response.split('\n'):
            line = line.strip()
            if 'SCORE:' in line:
                try:
                    audit['score'] = int(''.join(filter(str.isdigit, line.split(':')[1])))
                except: pass
            elif 'CRITICAL:' in line:
                try:
                    audit['critical'] = int(''.join(filter(str.isdigit, line.split(':')[1])))
                except: pass
            elif 'HIGH:' in line:
                try:
                    audit['high'] = int(''.join(filter(str.isdigit, line.split(':')[1])))
                except: pass
            elif 'MEDIUM:' in line:
                try:
                    audit['medium'] = int(''.join(filter(str.isdigit, line.split(':')[1])))
                except: pass
            elif 'SUMMARY:' in line:
                audit['summary'] = line.split(':', 1)[1].strip()
        
        return jsonify(audit)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)