from flask import Flask, request, Response, render_template, jsonify
import uuid
import re
import os
import requests

app = Flask(__name__)

# Dictionary to store UDIDs temporarily in memory
device_store = {}

# --- YOUR TELEGRAM BOT CONFIGURATION ---
TELEGRAM_BOT_TOKEN = "8334804183:AAFCqfdeVJVuDlmpqH1r5JowpjaSc8gAktg"
TELEGRAM_CHAT_ID = "8052258612"

@app.route("/")
def home():
    # Capture the UDID from the URL if it exists
    udid = request.args.get('udid', '')
    return render_template("index.html", udid=udid)

@app.route('/api/get-profile', methods=['GET'])
def get_profile():
    uid = request.args.get("uid", "unknown")
    root_url = request.url_root.rstrip('/')
    enroll_url = f"{root_url}/api/enroll?uid={uid}"

    profile_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>PayloadContent</key>
    <dict>
        <key>URL</key>
        <string>{enroll_url}</string>
        <key>DeviceAttributes</key>
        <array>
            <string>UDID</string>
        </array>
    </dict>
    <key>PayloadOrganization</key>
    <string>Nhoy Esign</string>
    <key>PayloadDisplayName</key>
    <string>UDID Retrieval Service</string>
    <key>PayloadIdentifier</key>
    <string>com.irra.udid.{uuid.uuid4()}</string>
    <key>PayloadUUID</key>
    <string>{uuid.uuid4()}</string>
    <key>PayloadVersion</key>
    <integer>1</integer>
    <key>PayloadType</key>
    <string>Profile Service</string>
</dict>
</plist>"""

    return Response(
        profile_xml,
        mimetype="application/x-apple-aspen-config",
        headers={"Content-Disposition": "attachment; filename=udid.mobileconfig"}
    )

@app.route('/api/enroll', methods=['POST'])
def enroll():
    uid = request.args.get('uid')
    
    # Apple sends signed data. We extract the UDID using Regex.
    raw_data = request.data.decode('latin-1')
    udid_match = re.search(r'<key>UDID</key>\s*<string>([^<]+)</string>', raw_data)
    
    captured_udid = udid_match.group(1) if udid_match else "NOT_FOUND"
    
    if uid:
        device_store[uid] = captured_udid

    # 301 Redirect sends the user back to Safari automatically with the UDID in the URL
    root_url = request.url_root.rstrip('/')
    return Response(status=301, headers={"Location": f"{root_url}/?udid={captured_udid}"})

@app.route('/api/check-status/<uid>')
def check_status(uid):
    return jsonify({"udid": device_store.get(uid)})

@app.route('/api/submit-order', methods=['POST'])
def submit_order():
    data = request.json
    udid = data.get('udid', 'N/A')
    email = data.get('email', 'N/A')

    # Send notification to Telegram
    message = f"🔔 *New Certificate Order!*\n\n📱 *UDID:* `{udid}`\n📧 *Email:* `{email}`\n💰 *Status:* User clicked Paid"
    telegram_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    
    try:
        response = requests.post(telegram_url, json={
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message,
            "parse_mode": "Markdown"
        })
        print(f"Telegram API Response: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Telegram error: {e}")

    return jsonify({"status": "success", "message": "Order processed"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    # Running on 0.0.0.0 so Ngrok can access it
    app.run(host="0.0.0.0", port=port, debug=True)