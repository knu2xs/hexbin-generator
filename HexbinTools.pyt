import arcpy
from hexbin_generator import get_hexbins_from_block_groups

class HexbinTools(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "HexbinTools"
        self.alias = "Hexbin Tools"

        # List of tool classes associated with this toolbox
        self.tools = [GetHexbinsForCbsa]


class GetHexbinsForCbsa(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Get Hexbins for CBSA"
        self.description = "Get hexbins covering the area of a CBSA"
        self.canRunInBackground = True

    def getParameterInfo(self):
        """Define parameter definitions"""
        param0 = arcpy.Parameter(
            name='cbsaLayer',
            displayName='Layer with CBSA Selected',
            direction='INPUT',
            datatype='GPFeatureLayer',
            parameterType='REQUIRED',
            enabled=True
        )
        param1 = arcpy.Parameter(
            name='outFeatureClass',
            displayName='Output Hexbin Feature Class',
            direction='OUTPUT',
            datatype='DEFeatureClass',
            parameterType='REQUIRED',
            enabled=True
        )
        params = [param0, param1]
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        get_hexbins_from_block_groups(parameters[0].valueAsText, parameters[1].valueAsText)
        return
