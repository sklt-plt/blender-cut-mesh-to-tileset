A simple script to cut 3d mesh into 27 separate "blocks", if possible.
The result is collection of objects arranged like a 3x3x3 Rubic's Cube.

Currently requires HardOPS
Non-HardOPS and customization is todo

For best results, target object should be placed inside single octant in world coordinates, and fit inside 3*grid lenght, but it is not required. See example scene for reference.

Supports variable grid size, but needs to be overriden in code for now.
Best works if it's multiple of 2 (default)

By default the script will try to guess on which octant the object is present, by averaging vertices. This is so that we can calculate each element's origin, as the closest point in grid towards world origin.

Empty elements may occur, when cutting into exactly 27 objects is not possible (this may happen, for example, when the object has no geometry inside). These elements are skipped and feedback is provided (in console for now)

Usage:
Install addon.zip in blender in Preferences->Add-ons->Install from Disk
Select mesh to cut
Open panels in 3D View (default 'n') and navigate to tab "Cut to tileset" 
CLik preferred option
Yay

Contributing:
Feel free to create merge request or issue
