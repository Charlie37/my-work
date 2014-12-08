/* 
 Name:
    toolbox
 Version:
    1.1 (15 October 2014)
 Author:
    Arnaud Trouvé (AMFX)
 Description:  
    Select layers defined as smart objects (then right click on selection> Pixelate).
    Remove empty layers.
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
var emptyLayers = [];

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

function multiRasterize(layerNames) {

    var layers = new Array();
    var idrasterizeLayer = stringIDToTypeID( "rasterizeLayer" );
    var desc30 = new ActionDescriptor();
    var idnull = charIDToTypeID( "null" );
    var ref27 = new ActionReference();
        for (var i = 0; i < layerNames.length; i++) {
        layers[i] = charIDToTypeID( "Lyr " );
        ref27.putName(layers[i], layerNames[i]);
    }
    var idLyr = charIDToTypeID( "Lyr " );
    var idOrdn = charIDToTypeID( "Ordn" );
    var idTrgt = charIDToTypeID( "Trgt" );
    ref27.putEnumerated( idLyr, idOrdn, idTrgt );
    desc30.putReference( idnull, ref27 );
    executeAction( idrasterizeLayer, desc30, DialogModes.NO );

    alert( layerNames.length + " layers have been rasterized.");
}

function multiDelete(layerNames) {

    var layers = new Array();
    var idDlt = charIDToTypeID( "Dlt " );
    var desc14 = new ActionDescriptor();
    var idnull = charIDToTypeID( "null" );
    var ref13 = new ActionReference();
    for (var i = 0; i < layerNames.length; i++) {
        layers[i] = charIDToTypeID( "Lyr " );
        ref13.putName(layers[i], layerNames[i]);
    }
    var idLyr = charIDToTypeID( "Lyr " );
    var idOrdn = charIDToTypeID( "Ordn" );
    var idTrgt = charIDToTypeID( "Trgt" );
    ref13.putEnumerated( idLyr, idOrdn, idTrgt );
    desc14.putReference( idnull, ref13 );
    executeAction( idDlt, desc14, DialogModes.NO );

    alert( layerNames.length + " empty layers have been deleted.");
}

function setBlendModeNormal(layerSet) {
    // TODO: without selecting -> "la commande définir n'est pas disponible" ?

    // select layerSet
    var idslct = charIDToTypeID( "slct" );
    var desc149 = new ActionDescriptor();
    var idnull = charIDToTypeID( "null" );
    var ref117 = new ActionReference();
    var idLyr = charIDToTypeID( "Lyr " );
    ref117.putName( idLyr, layerSet.name );
    desc149.putReference( idnull, ref117 );
    var idMkVs = charIDToTypeID( "MkVs" );
    desc149.putBoolean( idMkVs, false );
    executeAction( idslct, desc149, DialogModes.NO );

    // set blend mode to normal
    var idsetd = charIDToTypeID( "setd" );
    var desc123 = new ActionDescriptor();
    var ref97 = new ActionReference();
    var idOrdn = charIDToTypeID( "Ordn" );
    var idTrgt = charIDToTypeID( "Trgt" );
    ref97.putEnumerated( idLyr, idOrdn, idTrgt );
    desc123.putReference( idnull, ref97 );
    var idT = charIDToTypeID( "T   " );
    var desc124 = new ActionDescriptor();
    var idMd = charIDToTypeID( "Md  " );
    var idBlnM = charIDToTypeID( "BlnM" );
    var idNrml = charIDToTypeID( "Nrml" );
    desc124.putEnumerated( idMd, idBlnM, idNrml );
    var idLyr = charIDToTypeID( "Lyr " );
    desc123.putObject( idT, idLyr, desc124 );
    executeAction( idsetd, desc123, DialogModes.NO );
}

function selectSmartObject(layerSet) {
    
    if( layerSet.artLayers.length > 0 )
    {
        for(var k=0; k < layerSet.artLayers.length; k++)
        {
                var layer = layerSet.artLayers[k];
                if (layer.kind == "LayerKind.SMARTOBJECT")
                    smartObjects.push(layer.name);
                else
                if(layer.bounds[0] == "0 px" && layer.bounds[1] == "0 px" && layer.bounds[2] == "0 px" && layer.bounds[3] == "0 px")
                    emptyLayers.push(layer.name);

                // TODO: detect effects and blend mode
                // var idCpFX = charIDToTypeID( "CpFX" );
                //executeAction( idCpFX, undefined, DialogModes.NO );
        }
    }

    setBlendModeNormal(layerSet);
}

//-------------------------------------------------------------------------//
// main
//-------------------------------------------------------------------------//

alert("Setting blend mode of layer sets to normal...");

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

alert("Rasterization of smart objects...");

if( smartObjects.length > 0 )
    multiRasterize(smartObjects);
else
    alert("No layer defined as a smart object.");

alert("Deletion of empty layers...");

if( emptyLayers.length > 0 )
    multiDelete(emptyLayers);
else
    alert("No empty layer found.");


