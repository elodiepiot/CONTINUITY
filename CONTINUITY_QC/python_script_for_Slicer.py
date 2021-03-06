import argparse
import json
import os 
import vtk

##########################################################################################################################################
'''  
     CONTINUITY python script running by Slicer: Python script to load specific files and parameters
'''  
##########################################################################################################################################

# *****************************************
# Parameters
# *****************************************

parser = argparse.ArgumentParser(description='python script for Slicer')
parser.add_argument("user_json_filename", help = "json file with arguments like ID, OUTPATH and parameters for view controllers", type = str)
args = parser.parse_args()

user_json_filename = args.user_json_filename
with open(user_json_filename, "r") as user_Qt_file:
    json_user_object = json.load(user_Qt_file)

print("Execution of python script for Slicer")


# *****************************************
# DATA
# *****************************************

ID = json_user_object['Arguments']['ID']['value']
NAME_PARCELLATION_TABLE = json_user_object['Arguments']['PARCELLATION_TABLE_NAME']['value']
input_path = os.path.join( json_user_object['Parameters']['OUT_PATH']['value'], ID, "InputDataForSlicer")

# Find datas for B0_BiasCorrect
B0 = os.path.join( input_path, ID +"_DTI_B0_BiasCorrect_resample.nrrd")
if not os.path.exists(B0):
	B0 = os.path.join( input_path, ID +"_DTI_B0_BiasCorrect_original.nrrd")

# Find datas for B0
B0_with_biais = os.path.join( input_path, ID +"_DTI_B0_resample.nrrd")
if not os.path.exists(B0_with_biais):
	B0_with_biais = os.path.join( input_path, ID +"_DTI_B0_original.nrrd")

# Find data for T1 and T1_registered
T1_registered = os.path.join( input_path, ID + "_T1_SkullStripped_scaled_DWISpace.nrrd")

# Find data for AD: (AD_NRRD variable in the script)
AD = os.path.join( input_path, ID +"_DTI_AD_resample.nrrd")
if not os.path.exists(AD):
	AD = os.path.join( input_path,  ID +"_DTI_AD_original.nrrd")

# Find data for FA: 
FA = os.path.join( input_path, ID +"_DTI_FA_resample.nrrd")
if not os.path.exists(FA):
	FA = os.path.join( input_path, ID +"_DTI_FA_original.nrrd")

# Find data for labeled image: 
labeled_image = os.path.join( input_path, ID + "-T1_SkullStripped_scaled_label.nrrd")

# Find data for surface: 
registered_combine_surface         = os.path.join( input_path, "stx_" + ID + "_T1_CombinedSurface_white_" + NAME_PARCELLATION_TABLE + ".vtk")
registered_combine_surface_with_sc = os.path.join( input_path, "stx_" + ID + "_T1_CombinedSurface_white_" + NAME_PARCELLATION_TABLE + "_WithSubcorticals.vtk")


# Read and build polydata: 
reader = vtk.vtkPolyDataReader() #vtkPolyDataReader
reader.SetFileName(registered_combine_surface_with_sc)
reader.Update()
polydata_input = reader.GetOutput()  

polydata = vtk.vtkPolyData()
apd = vtk.vtkAppendPolyData()

if (vtk.VTK_MAJOR_VERSION < 6):
    apd.AddInput(polydata)
else:
    apd.AddInputData(polydata_input)
  
apd.Update()
output = apd.GetOutput()



# *****************************************
# Load data in Slicer (no show)
# *****************************************
if os.path.exists(B0):            loadedVolumeNode_B0            = slicer.util.loadVolume(B0,            properties={'name': 'B0',            'show': False})
if os.path.exists(B0_with_biais): loadedVolumeNode_B0_with_biais = slicer.util.loadVolume(B0_with_biais, properties={'name': 'B0_with_biais', 'show': False})
if os.path.exists(T1_registered): loadedVolumeNode_T1_registered = slicer.util.loadVolume(T1_registered, properties={'name': 'T1_registered', 'show': False})
if os.path.exists(AD):            loadedVolumeNode_AD            = slicer.util.loadVolume(AD,            properties={'name': 'AD',            'show': False})
if os.path.exists(FA):            loadedVolumeNode_FA            = slicer.util.loadVolume(FA,            properties={'name': 'FA',            'show': False})
if os.path.exists(labeled_image): loadedVolumeNode_labeled_image = slicer.util.loadVolume(labeled_image, properties={'name': 'labeled_image', 'show': False})

if os.path.exists(registered_combine_surface):         loadedVolumeNode_registered_combine_surface         = slicer.util.loadModel(registered_combine_surface)
if os.path.exists(registered_combine_surface_with_sc): loadedVolumeNode_registered_combine_surface_with_sc = slicer.util.loadModel(registered_combine_surface_with_sc)


# *****************************************
# Get not and display data in the good place
# *****************************************

#Set the view: 
slicer.app.layoutManager().setLayout(slicer.vtkMRMLLayoutNode.SlicerLayoutThreeByThreeSliceView)

list_view = ['Red', 'Yellow', 'Green', 'Slice4', 'Slice5', 'Slice6','Slice7', 'Slice8', 'Slice9']

sliceNodes = slicer.util.getNodesByClass('vtkMRMLSliceNode')
sliceNodes.append(slicer.mrmlScene.GetDefaultNodeByClass('vtkMRMLSliceNode'))

cpt = 0 
for sliceNode in sliceNodes:
	if cpt <= len(list_view)-1:
		place = list_view[cpt]

		# Get node and orientation
		node = slicer.util.getNode(str(json_user_object['View_Controllers'][place]['value']))
		orientationPresetName = sliceNode.GetOrientation()

		if place   == 'Red'      or place == "Slice4" or place == "Slice7": sliceNode.SetOrientation("Axial")
		elif place == 'Green'    or place == "Slice5" or place == "Slice8": sliceNode.SetOrientation("Sagittal")
		elif place == 'Sagittal' or place == "Slice6" or place == "Slice9": sliceNode.SetOrientation("Coronal")

	cpt += 1
		
	# Display foreground
	slicer.app.layoutManager().sliceWidget(place).sliceLogic().GetSliceCompositeNode().SetForegroundVolumeID( node.GetID() )  


# Create model node: 
model = slicer.vtkMRMLModelNode()
model.SetName('registered_combine_surface_with_sc_model')
model = slicer.mrmlScene.AddNode(model)
model.SetAndObservePolyData(output)

# Create display node: 
modelDisplay = slicer.vtkMRMLModelDisplayNode()
slicer.mrmlScene.AddNode(modelDisplay)
modelDisplay.VisibilityOn()
modelDisplay.SetVisibility2D(True) 

model.SetAndObserveDisplayNodeID(modelDisplay.GetID())
model.GetDisplayNode().SetActiveScalarName('label')
model.GetDisplayNode().SetAndObserveColorNodeID("vtkMRMLColorTableNodeLabels")
model.GetDisplayNode().ScalarVisibilityOn()
model.GetDisplayNode().AutoScalarRangeOn()