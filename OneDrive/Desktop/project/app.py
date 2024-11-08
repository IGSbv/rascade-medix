from flask import Flask, request, jsonify
from eth_account.messages import encode_defunct
from eth_account import Account

app = Flask(__name__)

# Endpoint to verify the signature
@app.route('/verify', methods=['POST'])
def verify_signature():
    data = request.json
    message = data.get('message')
    address = data.get('address')
    signature = data.get('signature')

    try:
        # Encode the message for Ethereum signing
        encoded_message = encode_defunct(text=message)
        
        # Recover the address from the signed message
        recovered_address = Account.recover_message(encoded_message, signature=signature)

        if recovered_address.lower() == address.lower():
            return jsonify({"success": True, "message": "Login successful!"}), 200
        else:
            return jsonify({"success": False, "message": "Invalid signature"}), 401

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
