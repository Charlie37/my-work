/* 
 Name:
    pixelate
 Version:
    1.0 (03 October 2014)
 Author:
    Arnaud Trouvé (AMFX)
 Description:  
    Select layers defined as smart objects (then right click on selection> Pixelate).
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
var smartObjects = [];

// TODO: print current time to check duration of process

function cTID(s) {return app.charIDToTypeID(s);}

function multiSelect(layerNames) {
    var layers = new Array();
    var id54 = charIDToTypeID( "slct" );
    var desc12 = new ActionDescriptor();
    var id55 = charIDToTypeID( "null" );
    var ref9 = new ActionReference();
    for (var i = 0; i < layerNames.length; i++) {
        layers[i] = charIDToTypeID( "Lyr " );
        ref9.putName(layers[i], layerNames[i]);
    }
    desc12.putReference( id55, ref9 );
    var id58 = charIDToTypeID( "MkVs" );
    desc12.putBoolean( id58, false );
    executeAction( id54, desc12, DialogModes.NO );
}

function selectSmartObject(layerSet) {
    
    if( layerSet.artLayers.length > 0 )
    {
        for(var k=0; k < layerSet.artLayers.length; k++)
        {
                var layer = layerSet.artLayers[k];
                if (layer.kind == "LayerKind.SMARTOBJECT")
                    smartObjects.push(layer.name);
        }
    }
}

//-------------------------------------------------------------------------//
// main
//-------------------------------------------------------------------------//

for(var i=0; i < doc.layerSets.length; i++)
{
    var layerSet = doc.layerSets[i];
    selectSmartObject(layerSet);

    // subfolder level 1
    if(layerSet.layerSets.length > 0)
   {
        for(var j=0; j < layerSet.layerSets.length; j++)
            selectSmartObject(layerSet.layerSets[j]);
    }
}

if( smartObjects.length > 0 )
    multiSelect(smartObjects);
else
    alert("No layer is defined as a smart object.");

