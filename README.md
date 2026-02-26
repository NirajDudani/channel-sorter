# Channel-Sorter  

A Nuke Python GUI tool that automatically sorts and organizes AOV channels into categorized Shuffle2 nodes, builds merge trees, and optionally groups them with backdrops — making multi-pass compositing cleaner and faster.

---

## Features  

### Scan & Detect Channels  
- Reads all available channels from the selected node  
- Extracts unique AOV layers  
- Displays them in a selection dialog  

### Channel Categorization  
Automatically sorts selected channels into:

- Material AOVs  
- Light Groups  
- Utilities  
- IDs  

Sorting is based on common AOV keywords such as diffuse, specular, reflection, cryptomatte, motion vectors, etc.

### Automatic Node Creation  
- Creates an Unpremult node  
- Generates Shuffle2 nodes for selected channels  
- Automatically names nodes with iteration numbers  
- Merges related AOVs using Merge2 (plus operation)  

### Iteration Detection  
- Prevents naming conflicts  
- Automatically increments version numbers for Shuffle nodes  

### Optional Backdrop Creation  
- Automatically creates labeled backdrops:
  - Material AOVs  
  - Light Groups  
  - Utilities  
  - IDs  
- Groups Shuffle and downstream nodes visually  

---

## Usage  

1. Select a Read node with multiple AOVs  
2. Go to:  
   `Nuke → Tools → Sort Channels`  
3. Choose the channels you want  
4. Select whether to add backdrops  
5. Click OK  

The tool will automatically build the node structure in the Node Graph.

---

## Installation  

1. Download the script file  
2. Place it inside your `.nuke` directory  
3. Add it to your `menu.py` if needed:

```python
import channel_sorter
```

4. Restart Nuke  

You will find it under:

`Nuke → Tools → Sort Channels`

---

## Prerequisites  

- Nuke  
- Python (Nuke embedded)  
- PySide2  

---

## Contribution  

Contributions are welcome! Feel free to submit pull requests or raise issues for any suggestions or bugs.