from flask import Blueprint, request, jsonify
from extensions import db
from models.call import Call
import requests
import os
from requests.auth import HTTPBasicAuth
from routes.auth_routes import token_required

call_bp = Blueprint('call_bp', __name__)

@call_bp.route("/make-call", methods=["POST"])
@token_required
def make_call(current_user):
    data = request.get_json()
    customer_number = data.get("phone_number")

    if not customer_number:
        return jsonify({"error": "Customer number required"}), 400

    agent_number = current_user.mobile_number  # 🔥 dynamic agent number

    if not agent_number:
        return jsonify({"error": "Agent mobile number is not set. Please update your profile."}), 400

    sid = os.getenv('EXOTEL_SID')
    api_key = os.getenv('EXOTEL_API_KEY')
    api_token = os.getenv('EXOTEL_API_TOKEN')
    caller_id = os.getenv('EXOTEL_CALLER_ID')

    url = f"https://api.exotel.com/v1/Accounts/{sid}/Calls/connect.json"

    payload = {
        "From": agent_number,
        "To": customer_number,
        "CallerId": caller_id
    }

    response = requests.post(
        url,
        data=payload,
        auth=HTTPBasicAuth(api_key, api_token)
    )

    return jsonify(response.json())

@call_bp.route("/incoming-call", methods=["POST"])
def incoming_call():
    # Exotel sends data as form-data
    caller = request.form.get("From")
    call_sid = request.form.get("CallSid")
    status = request.form.get("CallStatus")
    
    if caller:
        log = Call(
            customer_number=caller,
            direction="incoming",
            status=status,
            call_sid=call_sid
        )
        db.session.add(log)
        db.session.commit()

    return "OK", 200

@call_bp.route("/api/calls", methods=["GET"])
def get_calls():
    calls = Call.query.all()
    return jsonify([call.to_dict() for call in calls])