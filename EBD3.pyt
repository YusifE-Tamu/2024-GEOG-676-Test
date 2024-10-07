import arcpy

class Toolbox(object):
    def __init__(self):
        """
        Define the toolbox. The name of the toolbox is the name of the .pyt file.
        """
        self.label = "Environmental Buffers Toolbox"
        self.alias = "envbuffers"
        # List of tool classes associated with this toolbox
        self.tools = [EnvironmentalBuffers]

class EnvironmentalBuffers(object):
    def __init__(self):
        """
        Define the tool. The tool name is the name of the class.
        """
        self.label = "Environmental Buffers Tool"
        self.description = "Buffer polygons and/or polylines and optionally dissolve the buffered areas"
        self.canRunInBackground = False

    def getParameterInfo(self):
        """
        Define the tool parameters.
        """
        # Parameter for input features (polygons and/or polylines)
        param0 = arcpy.Parameter(
            displayName="Input Features",
            name="input_features",
            datatype="GPFeatureLayer",
            parameterType="Required",
            direction="Input",
            multiValue=True)
        param0.filter.list = ["Polygon", "Polyline"]
        param0.description = "Select the polygon and/or polyline features to buffer."

        # Parameter for buffer distance
        param1 = arcpy.Parameter(
            displayName="Buffer Distance",
            name="buffer_distance",
            datatype="GPLinearUnit",
            parameterType="Required",
            direction="Input")
        param1.description = "Enter the buffer distance (e.g., 50 Meters, 100 Feet)."

        # Parameter to decide whether to dissolve buffers
        param2 = arcpy.Parameter(
            displayName="Dissolve Buffers",
            name="dissolve_buffers",
            datatype="GPBoolean",
            parameterType="Required",
            direction="Input")
        param2.description = "Choose whether to dissolve the buffered features."

        # Parameter for dissolve field (optional)
        param3 = arcpy.Parameter(
            displayName="Dissolve Field",
            name="dissolve_field",
            datatype="Field",
            parameterType="Optional",
            direction="Input")
        param3.parameterDependencies = [param0.name]
        param3.description = "Select a field to dissolve by (optional)."

        # Parameter for output feature class
        param4 = arcpy.Parameter(
            displayName="Output Feature Class",
            name="output_features",
            datatype="DEFeatureClass",
            parameterType="Required",
            direction="Output")
        param4.description = "Specify the output feature class for the buffered (and optionally dissolved) features."

        params = [param0, param1, param2, param3, param4]
        return params

    def isLicensed(self):
        """Set whether the tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """
        Modify the values and properties of parameters before internal validation is performed.
        This method is called whenever a parameter has been changed.
        """
        # Enable/disable the dissolve field parameter based on whether dissolve is selected
        if parameters[2].value == False:
            parameters[3].enabled = False
        else:
            parameters[3].enabled = True
        return

    def updateMessages(self, parameters):
        """
        Modify the messages created by internal validation for each tool parameter.
        This method is called after internal validation.
        """
        return

    def execute(self, parameters, messages):
        """
        The source code of the tool.
        """
        print("Starting Environmental Buffers Tool...")
        arcpy.AddMessage("Starting Environmental Buffers Tool...")

        try:
            # Retrieve parameter values
            input_features = parameters[0].valueAsText
            buffer_distance = parameters[1].valueAsText
            dissolve_buffers = parameters[2].value
            dissolve_field = parameters[3].valueAsText if parameters[3].value else None
            output_features = parameters[4].valueAsText

            # Buffer the input features
            print(f"Buffering input features with distance: {buffer_distance}")
            arcpy.AddMessage(f"Buffering input features with distance: {buffer_distance}")
            arcpy.analysis.Buffer(input_features, output_features, buffer_distance)
            print("Buffering complete.")
            arcpy.AddMessage("Buffering complete.")

            # Dissolve if specified
            if dissolve_buffers:
                print("Dissolving buffered features...")
                arcpy.AddMessage("Dissolving buffered features...")
                if dissolve_field:
                    print(f"Dissolving based on field: {dissolve_field}")
                    arcpy.AddMessage(f"Dissolving based on field: {dissolve_field}")
                else:
                    print("Dissolving all features into a single feature")
                    arcpy.AddMessage("Dissolving all features into a single feature")
                
                dissolve_output = output_features + "_Dissolved"
                arcpy.management.Dissolve(output_features, dissolve_output, dissolve_field)
                
                # Replace the buffer output with the dissolved output
                print("Replacing buffer output with dissolved output...")
                arcpy.AddMessage("Replacing buffer output with dissolved output...")
                arcpy.management.Delete(output_features)
                arcpy.management.Rename(dissolve_output, output_features)
                print("Dissolve operation complete.")
                arcpy.AddMessage("Dissolve operation complete.")

            print("Environmental Buffers Tool completed successfully.")
            arcpy.AddMessage("Environmental Buffers Tool completed successfully.")
            
        except arcpy.ExecuteError:
            # Catch and report any ArcPy-specific errors
            error_msg = arcpy.GetMessages(2)
            print(f"ArcPy error: {error_msg}")
            arcpy.AddError(f"ArcPy error: {error_msg}")
        except Exception as e:
            # Catch and report any other unexpected errors
            error_msg = f"An unexpected error occurred: {str(e)}"
            print(error_msg)
            arcpy.AddError(error_msg)

        return

if __name__ == '__main__':
    # This allows the tool to be run from as a script tool in ArcGIS
    tool = EnvironmentalBuffers()
    tool.execute(tool.getParameterInfo(), None)