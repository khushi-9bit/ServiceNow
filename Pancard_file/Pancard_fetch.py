import cv2
import pytesseract

# Load image
img_path = r"D:\Uk_licence_model_training\Pan_card\PANCARD.jpg"
image = cv2.imread(img_path)
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# OCR config
custom_config = r'--oem 3 --psm 6'

# OCR with bounding boxes
data = pytesseract.image_to_data(gray, config=custom_config, output_type=pytesseract.Output.DICT)

# Step 1: Dynamically detect "Signature" as the landmark
landmark_positions = {}  # To store field positions
for i, text in enumerate(data["text"]):
    if "signature" in text.lower():  # Change to "signature"
        x = data["left"][i]
        y = data["top"][i]
        w = data["width"][i]
        h = data["height"][i]

        # Convert the absolute positions to percentages (relative to image dimensions)
        img_height, img_width = image.shape[:2]
        x_pct = x / img_width
        y_pct = y / img_height
        w_pct = w / img_width
        h_pct = h / img_height

        # Store the percentage-based coordinates for this field (landmark)
        landmark_positions['Signature'] = (x_pct, y_pct, w_pct, h_pct)

        # Draw bounding box for visualization
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.putText(image, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        break  # We only need the first match

# Step 2: Define the FIELD_OFFSETS relative to "Signature" in percentage
FIELD_OFFSETS = {
    "Your_Name":         (-2, -63, 50, 8),   # Field located above signature
    "Father's Name":      (-2, -50, 50, 8),   # Field above pan_number
    "Date_of_Birth":      (-2, -35, 50, 8),   # Field located further up
    "Pan_Number":         (-2, -22, 50, 8),   # Field above dob
}

# FIELD_OFFSETS = {
#     "Your_Name":         (-2, -45, 50, 8),   # Field located above signature
#     "Father's Name":      (-2, -35, 50, 8),   # Field above pan_number
#     "Date_of_Birth":      (-2, -28, 50, 8),   # Field located further up
#     "Pan_Number":         (-2, -17, 50, 8),   # Field above dob
# }

# Step 3: Use the signature position to calculate relative field positions
landmark_x, landmark_y, landmark_w, landmark_h = landmark_positions['Signature']
field_positions = {}

img_height, img_width = image.shape[:2]

for field, (x_offset, y_offset, w, h) in FIELD_OFFSETS.items():
    # Calculate the field's position relative to the signature position (using percentages)
    field_x = (landmark_x * img_width) + (x_offset * img_width / 100)
    field_y = (landmark_y * img_height) + (y_offset * img_height / 100)
    field_w = w * img_width / 100
    field_h = h * img_height / 100

    # Store the field's position
    field_positions[field] = (field_x, field_y, field_w, field_h)

    # Draw bounding box for each field
    cv2.rectangle(image, (int(field_x), int(field_y)), 
                  (int(field_x + field_w), int(field_y + field_h)), 
                  (255, 0, 0), 2)
    cv2.putText(image, field, (int(field_x), int(field_y) - 10), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)

# Step 4: Visualize the result with bounding boxes for each field
cv2.imshow("Detected Fields", image)
cv2.waitKey(0)
cv2.destroyAllWindows()

# Print field positions (in absolute coordinates)
for field, position in field_positions.items():
    print(f"{field}: {position}")

