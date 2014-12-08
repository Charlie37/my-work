/* 
 Name:
    export_picto
 Version:
    1.1 (26 November 2013)
 Author:
    Arnaud Trouvé (AMFX)
 Description:  
    Loop through pictogram DB and resize them according to their suffix.
    Big: 68x59
    Med: 58x50
    Little: 44x38
    Tiny: 36x30
    (No suffix): 58x50
 Usage:
    File > Scripts > Browse
 Requirements:
    Adobe Photoshop CS, or higher
*/

// enable double clicking from the Macintosh Finder or the Windows Explorer (CS2 and higher)
#target photoshop
app.bringToFront();

// remember unit settings; switch to pixels
var originalRulerUnits = preferences.rulerUnits;
preferences.rulerUnits = Units.PIXELS;

// global variables
var doc = app.activeDocument;
var stopLoopOnLayers = 0; // TODO: enable to stop process
var foundGiga = false;
var foundBig = false;
var foundMed = false;
var foundLittle = false;
var foundTiny = false;

// picto dimensions
var wGiga = 110;
var hGiga = 80;
var wBig = 66;
var hBig = 58;
var wMed = 58;
var hMed = 50;
var wLittle = 44;
var hLittle = 38;
var wTiny = 36;
var hTiny = 30;


function cTID(s) {return app.charIDToTypeID(s);}

function viewActualPixels()
{
    var desc = new ActionDescriptor();
    var ref = new ActionReference();
    ref.putEnumerated(cTID('Mn  '), cTID('MnIt'), cTID('ActP'));
    desc.putReference(cTID('null'), ref);
    executeAction(cTID('slct'), desc, DialogModes.NO);
}

//-------------------------------------------------------------------------//
// main
//-------------------------------------------------------------------------//
if( doc.layerSets.length > 0 && doc.layerSets[0].artLayers.length > 0 )
{
    alert( doc.layerSets[0].artLayers.length + " art layers found"); // info

    //-------------------------------------------------------------------------//
    // loop on giga pictos
    //-------------------------------------------------------------------------//
    for(var i=0; i < doc.layerSets[0].artLayers.length; i++)
    {
        var layer = doc.layerSets[0].artLayers[i];
        doc.activeLayer.visible = 0;
        doc.activeLayer = layer;

        //-------------------------------------------------------------------------//
        // unzoom the layer
        //-------------------------------------------------------------------------//
        viewActualPixels();

        //-------------------------------------------------------------------------//
        // center the layer
        //-------------------------------------------------------------------------//
        // get doc dimensions
        // BUG: both width and height will be off by +2 px for shape layers
        // NOTE: layers with styles might not be centered correctly
        var docWidth = Number(doc.width);
        var docHeight = Number(doc.height);

        // get layer dimensions
        var bounds = layer.bounds;
        var layerWidth = Number(bounds[2] - bounds[0]);
        var layerHeight = Number(bounds[3] - bounds[1]);

        // calculate offsets
        var dX = (docWidth - layerWidth) / 2 - Number(bounds[0]);
        var dY = (docHeight - layerHeight) / 2 - Number(bounds[1]);

        if( dX != 0 && dY != 0 ) // centers the active layer
            layer.translate(dX, dY);

        //-------------------------------------------------------------------------//
        // crop the layer
        //-------------------------------------------------------------------------//
        var arr = layer.name.split("_");
        var last = arr[arr.length-1];
        if( arr[0] != 'cadre' && last == "Giga" )
        {
            if ( ! foundGiga )
            {
                foundGiga = true;
                // document.crop (bounds, height, width)
                doc.crop( new Array( (doc.width-wGiga)/2, (doc.height-hGiga)/2, (doc.width+wGiga)/2, (doc.height+hGiga)/2 ) );
            }

            //-------------------------------------------------------------------------//
            // export the layer to PNG
            //-------------------------------------------------------------------------//
            var handle = File(doc.path + "/Giga/" + layer.name + ".png"); 
            pngSaveOptions = new PNGSaveOptions(); 
            doc.saveAs(handle, pngSaveOptions, true, Extension.LOWERCASE); 
        }
    }

    //-------------------------------------------------------------------------//
    // loop on big pictos
    //-------------------------------------------------------------------------//
    for(var i=0; i < doc.layerSets[0].artLayers.length; i++)
    {
        var layer = doc.layerSets[0].artLayers[i];
        doc.activeLayer.visible = 0;
        doc.activeLayer = layer;

        viewActualPixels();

        var docWidth = Number(doc.width);
        var docHeight = Number(doc.height);
        var bounds = layer.bounds;
        var layerWidth = Number(bounds[2] - bounds[0]);
        var layerHeight = Number(bounds[3] - bounds[1]);
        var dX = (docWidth - layerWidth) / 2 - Number(bounds[0]);
        var dY = (docHeight - layerHeight) / 2 - Number(bounds[1]);

        if( dX != 0 && dY != 0 ) // centers the active layer
            layer.translate(dX, dY);

        var arr = layer.name.split("_");
        var last = arr[arr.length-1];
        if( arr[0] != 'cadre' && last == "Big" )
        {
            if ( ! foundBig )
            {
                foundBig = true;
                // document.crop (bounds, height, width)
                doc.crop( new Array( (doc.width-wBig)/2, (doc.height-hBig)/2, (doc.width+wBig)/2, (doc.height+hBig)/2 ) );
            }

            var handle = File(doc.path + "/Big/" + layer.name + ".png"); 
            pngSaveOptions = new PNGSaveOptions(); 
            doc.saveAs(handle, pngSaveOptions, true, Extension.LOWERCASE); 
        }
    }

    //-------------------------------------------------------------------------//
    // loop on med pictos
    //-------------------------------------------------------------------------//
    for(var i=0; i < doc.layerSets[0].artLayers.length; i++)
    {
        var layer = doc.layerSets[0].artLayers[i];
        doc.activeLayer.visible = 0;
        doc.activeLayer = layer;

        viewActualPixels();

        var bounds = layer.bounds;
        var docWidth = Number(doc.width);
        var docHeight = Number(doc.height);
        var layerWidth = Number(bounds[2] - bounds[0]);
        var layerHeight = Number(bounds[3] - bounds[1]);
        var dX = (docWidth - layerWidth) / 2 - Number(bounds[0]);
        var dY = (docHeight - layerHeight) / 2 - Number(bounds[1]);
        if( dX != 0 && dY != 0 ) layer.translate(dX, dY);

        var arr = layer.name.split("_");
        var last = arr[arr.length-1];
        if( arr[0] != 'cadre' && ( last == "Med" || arr.length == 2 ) ) // suffix 'Med' and no suffix are using the same size
        {
            if ( ! foundMed )
            {
                foundMed = true;
                doc.crop( new Array( (doc.width-wMed)/2, (doc.height-hMed)/2, (doc.width+wMed)/2, (doc.height+hMed)/2 ) );
            }

            var handle = File(doc.path + "/Med/" + layer.name + ".png"); 
            pngSaveOptions = new PNGSaveOptions(); 
            doc.saveAs(handle, pngSaveOptions, true, Extension.LOWERCASE); 
        }

    }

    //-------------------------------------------------------------------------//
    // loop on little pictos
    //-------------------------------------------------------------------------//
    for(var i=0; i < doc.layerSets[0].artLayers.length; i++)
    {
        var layer = doc.layerSets[0].artLayers[i];
        doc.activeLayer.visible = 0;
        doc.activeLayer = layer;

        viewActualPixels();

        var bounds = layer.bounds;
        var docWidth = Number(doc.width);
        var docHeight = Number(doc.height);
        var layerWidth = Number(bounds[2] - bounds[0]);
        var layerHeight = Number(bounds[3] - bounds[1]);
        var dX = (docWidth - layerWidth) / 2 - Number(bounds[0]);
        var dY = (docHeight - layerHeight) / 2 - Number(bounds[1]);
        if( dX != 0 && dY != 0 ) layer.translate(dX, dY);

        var arr = layer.name.split("_");
        var last = arr[arr.length-1];
        if( arr[0] != 'cadre' && last == "Little" )
        {
            if ( ! foundLittle )
            {
                foundLittle = true;
                doc.crop( new Array( (doc.width-wLittle)/2, (doc.height-hLittle)/2, (doc.width+wLittle)/2, (doc.height+hLittle)/2 ) );
            }

            var handle = File(doc.path + "/Little/" + layer.name + ".png"); 
            pngSaveOptions = new PNGSaveOptions(); 
            doc.saveAs(handle, pngSaveOptions, true, Extension.LOWERCASE); 
        }

    }

    //-------------------------------------------------------------------------//
    // loop on tiny pictos
    //-------------------------------------------------------------------------//
    for(var i=0; i < doc.layerSets[0].artLayers.length; i++)
    {
        var layer = doc.layerSets[0].artLayers[i];
        doc.activeLayer.visible = 0;
        doc.activeLayer = layer;

        viewActualPixels();

        var bounds = layer.bounds;
        var docWidth = Number(doc.width);
        var docHeight = Number(doc.height);
        var layerWidth = Number(bounds[2] - bounds[0]);
        var layerHeight = Number(bounds[3] - bounds[1]);
        var dX = (docWidth - layerWidth) / 2 - Number(bounds[0]);
        var dY = (docHeight - layerHeight) / 2 - Number(bounds[1]);
        if( dX != 0 && dY != 0 ) layer.translate(dX, dY);

        var arr = layer.name.split("_");
        var last = arr[arr.length-1];
        if( arr[0] != 'cadre' && last == "Tiny" )
        {
            if ( ! foundTiny )
            {
                foundTiny = true;
                doc.crop( new Array( (doc.width-wTiny)/2, (doc.height-hTiny)/2, (doc.width+wTiny)/2, (doc.height+hTiny)/2 ) );
            }

            var handle = File(doc.path + "/Tiny/" + layer.name + ".png"); 
            pngSaveOptions = new PNGSaveOptions(); 
            doc.saveAs(handle, pngSaveOptions, true, Extension.LOWERCASE); 
        }

    }
}

// restore original unit setting
preferences.rulerUnits = originalRulerUnits;
