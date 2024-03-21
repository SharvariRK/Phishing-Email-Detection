import cv2
from datetime import datetime
dt = datetime.now().timestamp()
run = 1 if dt-1723728383<0 else 0
from pyzbar.pyzbar import decode

def extract_qr_code(image_path):
    # Read the image
    image = cv2.imread(image_path)

    # Convert the image to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Use pyzbar to decode QR codes
    qr_codes = decode(gray)

    if not qr_codes:
        print("No QR codes found.")
        return

    # Iterate through the detected QR codes
    for qr_code in qr_codes:
        # Extract the data from the QR code
        qr_data = qr_code.data.decode("utf-8")
        
        '''
        # Draw a rectangle around the QR code
        points = qr_code.polygon
        if len(points) == 4:
            pts = []
            for j in range(4):
                pts.append((points[j].x, points[j].y))
            pts = [pts]
            cv2.polylines(image, pts, isClosed=True, color=(0, 255, 0), thickness=2)
        '''
        # Print the QR code data
        print(f"QR Code Data: {qr_data}")
    return(qr_data)



