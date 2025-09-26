import cv2
import numpy as np

# Step 1: Detect Shapes and Extract Polygon Points
def detect_polygons(image_path, min_sides=4, allowed_sides=[4, 8, 16, 32, 64], area_min=100):
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY_INV)

    contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    polygons = []

    for contour in contours:
        approx = cv2.approxPolyDP(contour, 0.01 * cv2.arcLength(contour, True), True)
        area = cv2.contourArea(contour)
        if area < area_min:
            continue
        sides = len(approx)
        # Filter allowed polygons and rectangles only
        if sides in allowed_sides:
            # Extract points as (x, y) tuples
            polygon = np.squeeze(approx)
            polygons.append(polygon)

    return polygons


#Step 2: Write Polygon List to OASIS with gdstk
import gdstk
def polygons_to_oasis(polygons, oasis_path, dBu=0.001, layer=10, datatype=250):
    lib = gdstk.Library(unit=1e-6, precision=dBu)  # OASIS: unit=1um
    cell = lib.new_cell('IMAGE2OAS')
    for poly in polygons:
        # Convert to list of (float, float)
        pts = [tuple(pt) for pt in poly]
        print(f"Polygon points: {pts}")
        # Print edge lengths
        if len(pts) > 1:
            edge_lengths = [np.linalg.norm(np.array(pts[i]) - np.array(pts[(i+1)%len(pts)])) for i in range(len(pts))]
            print(f"Edge lengths (pixels): {edge_lengths}")
        else:
            print("Polygon has less than 2 points.")
    # gdstk.Cell doesn't have add_polygon; create a Polygon object and add it to the cell
    polygon = gdstk.Polygon(pts, layer=layer, datatype=datatype)
    cell.add(polygon)
    # Save to OASIS
    lib.write_oas(oasis_path)

# Example usage:
image_file = "octogon_1.png.jpg"
oasis_file = "output_layout.oas"

polys = detect_polygons(image_file)
polygons_to_oasis(polys, oasis_file, layer=10, datatype=250)

