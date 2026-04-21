import nuke
import nukescripts
from PySide2 import QtWidgets

def sort_channels():    
    selected_node = nuke.selectedNode()

    unpremult_node = nuke.createNode('Unpremult', inpanel = False)
    unpremult_node.setInput(0, selected_node)
    
    
    channels = selected_node.channels()
    channel = []

    for c in channels:
        c_split = c.split(".")[0]
        channel.append(c_split)

    sorted_channel = sorted(set(channel))

    create_checkbox_dialog(sorted_channel, selected_node,unpremult_node)


def sort_nodes(channel_names):
    material_aov_keywords = [
        "diffuse", "specular", "reflection", "refraction", "normal", "glossiness", 
        "roughness", "metallic", "ambient occlusion", "emission", "depth", 
        "shadow", "transmission", "displacement", "subsurface scattering", 
        "clearcoat", "sheen", "fresnel", "transmission depth", "specular roughness", 
        "anisotropy", "velocity"
    ]
    
    utilities = [
        "motion vectors", "z-depth", "cryptomatte", "object id", "material id", 
        "layer masks", "ambient light", "wireframe", "caustics", "light masking"
    ]
    
   
    sorted_channels = {
        "Material AOVs": [],
        "Light Groups": [],
        "Utilities": [],
        "IDs": []
    }
    
    for channel in channel_names:
        channel_lower = channel.lower() 

        if "light" in channel_lower or "rgba" in channel_lower:
            sorted_channels["Light Groups"].append(channel)
        elif "id" in channel_lower:
            sorted_channels["IDs"].append(channel)
        elif any(keyword in channel_lower for keyword in material_aov_keywords):
            sorted_channels["Material AOVs"].append(channel)
        elif any(keyword in channel_lower for keyword in utilities):
            sorted_channels["Utilities"].append(channel)

    return sorted_channels

def get_next_iteration_number():
    existing_names = [node.name() for node in nuke.allNodes('Shuffle2')]

    iteration = 1
    while any(name.endswith(str(iteration)) for name in existing_names):
        iteration += 1

    return iteration


def create_backdrop(nodes_dict, iteration_number):
    def create_group_backdrop(nodes, label):
        if not nodes:
            return None  # No nodes to group

        # Deselect all nodes first
        for node in nuke.allNodes():
            node['selected'].setValue(False)

        # Select only the nodes for this backdrop
        for node in nodes:
            node['selected'].setValue(True)
            print (node.name())

        backdrop = nukescripts.autoBackdrop()
        backdrop["label"].setValue(label)
        return backdrop

    Material_AOVs_List = nodes_dict["Material AOVs"]
    Light_Groups_List = nodes_dict["Light Groups"]
    Utilities_List = nodes_dict["Utilities"]
    ID_List = nodes_dict["IDs"]

    Material_AOVs_Node = []
    Light_Groups_Node = [] 
    Utilities_Node = []
    ID_Node = []

    for items in Material_AOVs_List:
        point_node = nuke.toNode(items + "_" + str(iteration_number))
        if point_node:
            Material_AOVs_Node.append(point_node) 
            downstream_nodes = point_node.dependent(nuke.INPUTS)
            Material_AOVs_Node.extend(downstream_nodes)
    
    for items in Light_Groups_List:
        point_node = nuke.toNode(items + "_" + str(iteration_number))
        if point_node:
            Light_Groups_Node.append(point_node) 
            downstream_nodes = point_node.dependent(nuke.INPUTS)
            Light_Groups_Node.extend(downstream_nodes)    

    for items in Utilities_List:
        point_node = nuke.toNode(items + "_" + str(iteration_number))
        if point_node:
            Utilities_Node.append(point_node) 
            downstream_nodes = point_node.dependent(nuke.INPUTS)
            Utilities_Node.extend(downstream_nodes)

    for items in ID_List:
        point_node = nuke.toNode(items + "_" + str(iteration_number))
        if point_node:
            ID_Node.append(point_node) 
            downstream_nodes = point_node.dependent(nuke.INPUTS)
            ID_Node.extend(downstream_nodes)

    print("Material AOVs Nodes:", Material_AOVs_Node)
    print("Light Groups Nodes:", Light_Groups_Node)
    print("Utilities Nodes:", Utilities_Node)
    print("ID Nodes:", ID_Node)

    create_group_backdrop(Material_AOVs_Node, "Material AOVs")
    create_group_backdrop(Light_Groups_Node, "Light Groups")
    create_group_backdrop(Utilities_Node, "Utilities")
    create_group_backdrop(ID_Node, "ID")

 

def create_checkbox_dialog(sorted_channel, selected_node, unpremult_node):
    class ChannelSelectionDialog(QtWidgets.QDialog):
        def __init__(self, channels, node):
            super().__init__()

            self.setWindowTitle("Select Channels")
            self.setGeometry(200, 200, 300, 400)

            self.node = node
            self.channels = channels
            self.checkboxes = []

            layout = QtWidgets.QVBoxLayout(self)

            label = QtWidgets.QLabel("Select the Channels:")
            layout.addWidget(label)

            for channel in self.channels:
                checkbox = QtWidgets.QCheckBox(channel)
                layout.addWidget(checkbox)
                self.checkboxes.append(checkbox)

            self.backdrop_label = QtWidgets.QLabel("Add Backdrop?")
            layout.addWidget(self.backdrop_label)

            self.backdrop_dropdown = QtWidgets.QComboBox()
            self.backdrop_dropdown.addItems(["No", "Yes"])
            layout.addWidget(self.backdrop_dropdown)

            ok_button = QtWidgets.QPushButton("OK")
            ok_button.clicked.connect(self.get_selected_channels)
            layout.addWidget(ok_button)

        def get_selected_channels(self):
            self.selected_channels = []
            shuffle_nodes = {}

            x_shuffle = nuke.selectedNode().xpos()
            y_shuffle = nuke.selectedNode().ypos()

            x_merge = nuke.selectedNode().xpos()
            y_merge = nuke.selectedNode().ypos()

            iteration_number = get_next_iteration_number()  

            for cb in self.checkboxes:
                if cb.isChecked():
                    self.selected_channels.append(cb.text())

            sorted_nodes = sort_nodes(self.selected_channels)
            combined_nodes = sorted_nodes["Material AOVs"] + sorted_nodes["Light Groups"] + sorted_nodes["Utilities"] + sorted_nodes["IDs"]

            for selection in combined_nodes:
                x_shuffle = x_shuffle + 110
                shuffle_node = nuke.createNode('Shuffle2')
                shuffle_node.knob('in1').setValue(selection)
                shuffle_node.knob('name').setValue(f"{selection}_{iteration_number}")  
                shuffle_node.setInput(0, unpremult_node)
                shuffle_node.setXpos(x_shuffle)
                shuffle_node.setYpos(y_shuffle + 60)
                

                base_name = selection.split('_')[0]

                if base_name in shuffle_nodes:
                    
                    merge_node = nuke.createNode('Merge2')
                    merge_node.knob('operation').setValue('plus')
                    merge_node.setInput(0, shuffle_nodes[base_name])
                    merge_node.setInput(1, shuffle_node)
                    shuffle_nodes[base_name] = merge_node
                    merge_node.setXpos(x_shuffle)
                    merge_node.setYpos(y_merge + 120)
                else:
                    shuffle_nodes[base_name] = shuffle_node

            if self.backdrop_dropdown.currentText() == "Yes":
                create_backdrop(sorted_nodes, iteration_number)


            self.accept()  

    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])

    dialog = ChannelSelectionDialog(sorted_channel, selected_node)
    dialog.exec_()


sort_channels()

nuke.menu('Nuke').addCommand('Tools/Sort Channels', sort_channels)
