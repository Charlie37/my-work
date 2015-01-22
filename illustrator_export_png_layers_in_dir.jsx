/* 
 Name:
    ExportPngLayers
 Version:
    1.1 (21 January 2015)
  Licence:
    GNU General Public License Version 3. (http://www.gnu.org/licenses/gpl-3.0-standalone.html)
 Author:
    Arnaud Trouvé (AMFX)
    based on work by William Ngan (www.metaphorical.net)
 Description:  
    Export each layer as a separate PNG image file, in the directory you selected.
 Usage:
    Layer name is the PNG file name. Rename layers if necessary..
    Select the directory where to export PNG files.
*/

var doc = app.activeDocument;

// prepare layers
for(var i=0; i<doc.layers.length; i++) {
		doc.layers[i].visible = false;
}

// choose location where to save layers
var loc = "";
var saveLocation = new Folder();
saveLocation = saveLocation.selectDlg('Where would you like to save your images?');
if (saveLocation != null) loc = saveLocation;


// go through each layers
for(var i=0; i<doc.layers.length; i++) {
	doc.layers[i].visible = true;
	if (i>0) doc.layers[i-1].visible = false;

	var fpath = doc.path; // save to document's folder
    fpath.changePath( loc + '/' + doc.layers[i].name+'.png' );
    
	savePNG( fpath );
}

/**
	* Save PNG file
	* @param file File object
*/
function savePNG( file ) {
	// export SAVE-FOR-WEB options
	var exp = new ExportOptionsPNG24();
	exp.transparency = true;
	exp.artBoardClipping = true;

	// export as SAVE-FOR-WEB
	doc.exportFile( file, ExportType.PNG24, exp);
}
