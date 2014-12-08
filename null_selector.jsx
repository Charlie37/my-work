/* 
 Name:
    NullSelector
 Version:
	1.0 (02 December 2014)
 Author:
    Arnaud Trouvé (AMFX)
 Description:  
    Select all nulls in project.
 Usage:
    Click "OK"
*/


var s = new Array(); // selected items
vers = "1.0";
var win = new Window('palette', 'NullSelector (v' + vers + ')',[300,100,645,236]);
var w = buildUI();
if (w != null) {
    w.show();
}

function buildUI() {
    if (win != null) {
        
        win.lbl = win.add("statictext", [40,20,266,40], 'Click \"OK\" to select my Null.', {multiline:true} ); 
     
        win.okBtn = win.add('button', [40,85,120,107], 'OK', {name:'OK'});
        win.okBtn.onClick = function () { doMain(this.parent); };
        
        win.cancBtn = win.add('button', [240,85,320,107], 'Close', {name:'Cancel'});
        win.cancBtn.onClick = function () {this.parent.close(1)};
    }
    return win;
}

function doMain(theDialog) {
    
    if ( ! app.project.items ) {
        alert("No item existing in the project. Please create one.");
        return;
    }
    else {
        for (var i = 1; i <= app.project.numItems; i++){
            if( app.project.item(i).typeName == "Footage" 
                &&  app.project.item(i).name.lastIndexOf("Null",0) == 0 // AE considers 3 Item types: Composition/Folder/Footage
                /*&& app.project.item(i).label == 1*/ ) // default labels may be changed by user
                if( ! app.project.item(i).selected )
                    app.project.item(i).selected = true;
        }

    }

    return;    
}


