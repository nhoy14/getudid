from flask import Flask, request, Response, render_template
import uuid

app = Flask(__name__)

# ===============================
# HOME PAGE
# ===============================
@app.route("/")
def home():
    return render_template("index.html")


# ===============================
# GENERATE UDID PROFILE
# ===============================
@app.route('/api/get-profile', methods=['GET'])
def get_profile():
    uid = request.args.get("uid", "unknown")

    root_url = request.url_root.rstrip('/')
    enroll_url = f"{root_url}/api/enroll?uid={uid}"

    profile_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
"http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>PayloadContent</key>
    <dict>
        <key>URL</key>
        <string>{enroll_url}</string>
        <key>DeviceAttributes</key>
        <array>
            <string>UDID</string>
            <string>PRODUCT</string>
            <string>VERSION</string>
        </array>
    </dict>
    <key>PayloadOrganization</key>
    <string>IRRA ESIGN</string>
    <key>PayloadDisplayName</key>
    <string>Get Device UDID</string>
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
        headers={
            "Content-Disposition": "attachment; filename=udid.mobileconfig"
        }
    )


# ===============================
# RECEIVE UDID
# ===============================
@app.route('/api/enroll', methods=['POST'])
def enroll():
    udid = request.form.get('UDID')
    product = request.form.get('PRODUCT')
    version = request.form.get('VERSION')
    uid = request.args.get('uid')

    print("========== NEW DEVICE ==========")
    print("UID:", uid)
    print("UDID:", udid)
    print("Device:", product)
    print("iOS Version:", version)
    print("================================")

    return """
    <h2>✅ Device Registered Successfully</h2>
    <p>You can now close this page.</p>
    """


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)