from flask import Flask, request, Response, render_template, jsonify
import uuid
import re
import os

app = Flask(__name__)

# Dictionary to store UDIDs temporarily in memory
device_store = {}

@app.route("/")
def home():
    # If the UDID is passed in the URL (from the redirect), show it
    udid = request.args.get('udid')
    return render_template("index.html", udid=udid)

@app.route('/api/get-profile', methods=['GET'])
def get_profile():
    uid = request.args.get("uid", "unknown")
    # Render automatically provides HTTPS, which is required by Apple
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
    <string>Device Identifier</string>
    <key>PayloadDisplayName</key>
    <string>Profile Service</string>
    <key>PayloadIdentifier</key>
    <string>com.render.udid.{uuid.uuid4()}</string>
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

    # 301 Redirect sends the user back to Safari automatically
    root_url = request.url_root.rstrip('/')
    return Response(status=301, headers={"Location": f"{root_url}/?udid={captured_udid}"})

@app.route('/api/check-status/<uid>')
def check_status(uid):
    return jsonify({"udid": device_store.get(uid)})

if __name__ == "__main__":
    # Port is handled by Render/Gunicorn in production
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)