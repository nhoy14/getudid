from flask import Flask, request, Response, render_template
import uuid
import os

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
@app.route("/api/get-profile", methods=["GET"])
def get_profile():
    uid = request.args.get("uid", str(uuid.uuid4()))

    root_url = request.url_root.rstrip("/")
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
    <string>GET UDID SERVICE</string>
    <key>PayloadDisplayName</key>
    <string>Get Device UDID</string>
    <key>PayloadIdentifier</key>
    <string>com.getudid.profile.{uuid.uuid4()}</string>
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
# RECEIVE DEVICE DATA
# ===============================
@app.route("/api/enroll", methods=["POST"])
def enroll():
    udid = request.form.get("UDID")
    product = request.form.get("PRODUCT")
    version = request.form.get("VERSION")
    uid = request.args.get("uid")

    print("========== NEW DEVICE ==========")
    print("UID:", uid)
    print("UDID:", udid)
    print("Device:", product)
    print("iOS Version:", version)
    print("================================")

    return """
    <html>
        <body style="text-align:center;padding-top:50px;font-family:Arial;">
            <h2>✅ Device Registered Successfully</h2>
            <p>You can now close this page.</p>
        </body>
    </html>
    """


# ===============================
# RUN SERVER (RENDER COMPATIBLE)
# ===============================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)