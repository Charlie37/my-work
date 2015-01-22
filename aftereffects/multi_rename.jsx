/* 
 Name:
    MultiRename
 Version:
	1.1 (18 February 2014)
 Author:
    Arnaud Trouvé (AMFX)
    based in part on other works by CR Green (crgreen.com)
    Thanks to him, and as always, thanks to creativecow.net and aenhancers.com
 Description:  
    Rename groups, precomps and layers.
 Usage:
    Select an item type, then describe the change to apply
    Click "OK"
*/

function MultiRename()
{
    // Variable used to keep track of 'this' reference
	var multiRename = this;
    
    // Script infos
    this.vers = "1.1";
	this.scriptMinSupportVersion = "9.0";
    
    this.s = new Array(); // selected items

     // Creates and displays the script interface
	this.buildUI = function (thisObj)
	{
		// dockable panel or palette
        this.pal = (thisObj instanceof Panel) ? thisObj : new Window("palette", this.scriptTitle, undefined, {resizeable:false});
        
        this.pal.folderRad =this.pal.add('radiobutton',  [14,20,123,40], 'Folder');
        this.pal.precompRad =this.pal.add('radiobutton', [124,20,233,40], 'Precomp');
        this.pal.precompRad.value = true;
        this.pal.layerRad = this.pal.add('radiobutton', [234,20,343,40], 'Layer Name');
    
        this.pal.nameSearchLabel = this.pal.add('statictext', [14,60,24,77], 'A:');
        this.pal.nameSearchT = this.pal.add('edittext', [25,55,325,77], '');
        this.pal.nameReplaceLabel = this.pal.add('statictext', [14,98,24,115], 'B:');
        this.pal.nameReplaceT = this.pal.add('edittext', [25,98,325,115], '');

        this.pal.typePnl = this.pal.add('panel', [16,128,350,233], 'Action:');
        this.pal.progLbl = this.pal.add('statictext', [20,311,206,348], '');
        
        this.pal.repRad = this.pal.typePnl.add('radiobutton', [14,13,274,35], 'Search A in Names and Replace with B');
        this.pal.repRad.value = true;
        this.pal.appRad = this.pal.typePnl.add('radiobutton', [14,39,274,61], 'Append Head with A and Tail with B');
        this.pal.remRad = this.pal.typePnl.add('radiobutton', [14,65,324,87], 'Remove A characters from Head and B characters from Tail');
      
        this.pal.okBtn = this.pal.add('button', [14,250,94,272], 'OK', {name:'OK'});
        this.pal.okBtn.onClick = function () { multiRename.doRenaming(); };
    };


    this.doRenaming = function()
    {
        var type = "";
        this.s.length = 0; // reinit
        
        if (this.pal.precompRad.value)
        {           
           type = "precomp";
           for (i = app.project.numItems; i >= 1; i--)
           { 
                var myItem = app.project.item(i);
                if (myItem.selected && myItem instanceof CompItem) 
                        this.s.push(myItem);
            }
        }
        else
        if (this.pal.folderRad.value)
        {
           type = "folder";
           for (i = app.project.numItems; i >= 1; i--)
           { 
                var myItem = app.project.item(i);
                if (myItem.selected && myItem instanceof FolderItem) 
                        this.s.push(myItem);
            }
        }
        else
        if (this.pal.layerRad.value)
        {
           type = "layer";
           for (i = app.project.numItems; i >= 1; i--)
           { 
                var myItem = app.project.item(i);
                if (myItem instanceof CompItem) 
                {
                    for(j = 1; j <=  myItem.layers.length;j++)
                        if( myItem.layer(j).selected )
                            this.s.push(myItem.layer(j));
                }
            }
        }   
    
        var selNum = this.s.length;
        if (selNum < 1)
        {
            alert("You need to select at least one " + type + " first.");
            return;
        }

        app.beginUndoGroup("layer rename");
        var inputError = false;
        this.pal.progLbl.text = 'WORKING ............. PLEASE WAIT';
        
        for (var n = (selNum-1); n >= 0; n--) {
            
            if ( ! inputError ) {
                item = this.s[n];
                oldName = item.name;

                sear = this.pal.nameSearchT.text;
                repl = this.pal.nameReplaceT.text
                
                newName = oldName;
                
                if (this.pal.repRad.value) {
                    
                newName = multiRename.splitReplace(newName, sear, repl);
                
                //now we check for pre-cs4 app version, for which we truncate:
                if ((parseFloat(app.version) < 9.0)) { newName=(newName.substr(0,25));}
                } else if (this.pal.appRad.value) {
                    newName=(sear + oldName + repl );
                    
                } else if (this.pal.remRad.value) {
 
                    if (sear == "") {sear = 0;}
                    if (repl == "") {repl = 0;}
                    sear = ( parseFloat(sear) );
                    repl = ( parseFloat(repl) );
                    if ( (isNaN(sear)) || (isNaN(repl)) ) {
                        alert('Error: Not a number?');
                        inputError = true;
                    } else {
                        newName=(newName.substr( sear, oldName.length ));
                        newName=(newName.substr( 0, newName.length-repl ));
                        sear="";
                        repl="";
                    } 
                } else if (this.pal.numRad.value) {
                    
                    sear = this.pal.startNumT.text;
                    repl = this.pal.countNumT.text
                    if (sear == "") {sear = 0;}
                    if ( (repl == "") || (repl == 0) ) {repl = "NaN";}
                    sear = ( parseFloat(sear) );
                    repl = ( parseFloat(repl) );
                    
                    if ( (isNaN(sear)) || (isNaN(repl)) ) {
                        alert('Error: Not a number, or invalid number to count by.');
                        inputError = true;
                    } else {
                        h = this.pal.nameSearchT.text;
                        t = this.pal.nameReplaceT.text;
                        numNum = ((n * repl) + sear);
                        newName = (h + numNum.toString() + t);
                 //now we check for pre-cs4 app version and we error if name too long:
                if ((parseFloat(app.version) < 9.0)) {
                        if (newName.length > 25) {
                            inputError = true ;
                            // this generates 'error', at beginning of loop,
                            // which is largest number (highest number)
                            alert('Error: Name too long.');
                        }
                 }
                        sear="";
                        repl="";
                    }
                }
                
                //////////////////////
                if (! inputError)
                    item.name = newName;
                else
                    this.pal.progLbl.text = '(ERROR)';
                //////////////////////
            }
        }
        if (! inputError) {this.pal.progLbl.text = '';}
        app.endUndoGroup();
    };


    this.doTextChange = function(target, newText) {
        target.text = newText;
    };

    this.doViz = function(target, bool) {
        target.visible = !bool;
    };

    this.splitReplace = function(st, ss, rs) {
        var stArray = st.split(ss);
        var patchedString = "";
        var i = 0;
        while (i < (stArray.length)) {
            if (i == (stArray.length-1)) {rs = "";}
            patchedString = (patchedString + (stArray[i] + rs) );
            i = (i + 1);
        }

        return patchedString
    };


     // Runs the script  
	this.run = function (thisObj) 
	{
		if (parseFloat(app.version) < parseFloat(this.scriptMinSupportVersion))
		{
			utils.throwErr(this.requirementErr);
		}
		else
		{
			this.buildUI(thisObj);
		}	
	};
}


// Creates an instance of the main class and run it
new MultiRename().run(this);
