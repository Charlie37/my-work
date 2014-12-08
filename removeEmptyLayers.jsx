/* 
 Name:
    removeEmptyLayers
 Version:
    1.0 (03 October 2014)
 Author:
    Arnaud Trouvé (AMFX)
 Description:  
    Remove empty layers (i.e. with dimensions equal to zero).
    TODO: this script only parses groups with a tree depth of 1.
 Usage:
    File > Scripts > Browse
 Requirements:
    Adobe Photoshop CS, or higher
*/

// enable double clicking from the Macintosh Finder or the Windows Explorer (CS2 and higher)
#target photoshop
app.bringToFront();

// global variables
var doc = app.activeDocument;

// TODO: print current time to check duration of process. Add progress bar.

function cTID(s) {return app.charIDToTypeID(s);}

function selectLayersRecursive(layerSet) {
    
    if( layerSet.artLayers.length > 0 )
    {
        for(var k=0; k < layerSet.artLayers.length; k++)
        {
                var layer = layerSet.artLayers[k];
                if(layer.bounds[0] == "0 px" && layer.bounds[1] == "0 px" && layer.bounds[2] == "0 px" && layer.bounds[3] == "0 px")
                    layer.remove();
        }
    }
}

//-------------------------------------------------------------------------//
// main
//-------------------------------------------------------------------------//

for(var i=0; i < doc.layerSets.length; i++)
{
    var layerSet = doc.layerSets[i];
    selectLayersRecursive(layerSet);

    // subfolder level 1
    if(layerSet.layerSets.length > 0)
   {
        for(var j=0; j < layerSet.layerSets.length; j++)
            selectLayersRecursive(layerSet.layerSets[j]);
    }
}

alert("Empty layers have been deleted.");

