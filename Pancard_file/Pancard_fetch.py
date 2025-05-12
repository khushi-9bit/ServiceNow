import cv2
import pytesseract

def extract_pan_fields(img_path):
    # Load image and convert to grayscale
    image = cv2.imread(img_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # OCR config
    custom_config = r'--oem 3 --psm 4'
    data = pytesseract.image_to_data(gray, config=custom_config, output_type=pytesseract.Output.DICT)

    print("OCR text found:")
    print([t for t in data["text"] if t.strip()])

    img_height, img_width = image.shape[:2]
    landmark_positions = {}

    # Step 1: Detect 'INCOME' landmark
    for i, text in enumerate(data["text"]):
        if "income" in text.lower():
            x, y, w, h = data["left"][i], data["top"][i], data["width"][i], data["height"][i]
            x_pct, y_pct = x / img_width, y / img_height
            w_pct, h_pct = w / img_width, h / img_height
            landmark_positions['INCOME'] = (x_pct, y_pct, w_pct, h_pct)

            cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(image, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
            print(f"Found landmark 'INCOME' at: ({x}, {y})")
            break

    if 'INCOME' not in landmark_positions:
        print("Income landmark not found.")
        return

    # Step 2: Define field box offsets in % relative to IMAGE dimensions (not landmark)
    FIELD_OFFSETS = {
        "Your_Name":        (0, 10, 50, 8),
        "Father's Name":    (0, 23, 50, 8),
        "Date_of_Birth":    (0, 36, 50, 8),
        "Pan_Number":       (0, 50, 50, 8),
    }

    landmark_x, landmark_y, landmark_w, landmark_h = landmark_positions['INCOME']

    field_positions = {}
    for field, (x_offset_pct, y_offset_pct, w_pct, h_pct) in FIELD_OFFSETS.items():
        field_x = (landmark_x * img_width) + (x_offset_pct * img_width / 100)
        field_y = (landmark_y * img_height) + (y_offset_pct * img_height / 100)
        field_w = w_pct * img_width / 100
        field_h = h_pct * img_height / 100
        field_positions[field] = (field_x, field_y, field_w, field_h)

        # Visual debugging
        cv2.rectangle(image, (int(field_x), int(field_y)), 
                      (int(field_x + field_w), int(field_y + field_h)), 
                      (255, 0, 0), 2)
        cv2.putText(image, field, (int(field_x), int(field_y) - 10), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)

        # Optional: draw line from landmark to field box
        cv2.line(image,
                 (int(landmark_x * img_width), int(landmark_y * img_height)),
                 (int(field_x), int(field_y)),
                 (0, 255, 255), 1)

    # Step 3: Extract text from field regions
    extracted_fields = {}
    for field_name, (fx, fy, fw, fh) in field_positions.items():
        field_text = []
        for i in range(len(data['text'])):
            word = data['text'][i]
            if word.strip() == "":
                continue
            x, y = data['left'][i], data['top'][i]
            if fx <= x <= fx + fw and fy <= y <= fy + fh:
                field_text.append(word)
        extracted_fields[field_name] = " ".join(field_text)

    # Step 4: Show image and print results
    cv2.imshow("Detected Fields", image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    print("\nExtracted Field Values:")
    for field, value in extracted_fields.items():
        print(f"{field}: {value}")


def main():
    img_path = r"D:\Uk_licence_model_training\Pan_card\pan_card.jpg"
    extract_pan_fields(img_path)


if __name__ == "__main__":
    main()
