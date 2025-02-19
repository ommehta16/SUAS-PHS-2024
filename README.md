# SUAS-PHS-2024

<h2>Object Detection</h2>

**TODO**

 - try ML stuff??///1??????1?????
   - no
 - MORE TEST IMAGES
   - FROM ACTUAL PLANE!!!!!!///!!!


<h2>MISSION PLANNING</h2>

**DESIGN:**

 - Main
 - Planner
   - `plan` runs in background:
     - Stores initial waypoint route
     - Returns waypoints for map
     - Takes map made by Mapper
     - Asks object detector for objects
     - Returns waypoints for drop
     - Returns drop locations
 - Mapper
   - Makes map
   - `pixel_to_coord` takes pixel index and returns corresponding coordinate
 - Object Detector
   - `object_detect` returns pixel index rects for all objects on finished map
 - Plane
   - Just has plane class (stores plane info)