import QtQuick 2.1
import QtMultimedia 5.0


// Provides a simple object to display a clipped image.
// ClippedImage can be embedded into another ClippedImage object:
// x/y coordinates of the 2d object indicates its position among the relative coordinates of the 1st object.

Container {

    id: root

    // This property holds the source URL of the media.
    property alias source: image.source

    Component.onCompleted: {

        if(root.parent.source && root.parent.source.toString() != "") {
            image.source = root.parent.source
            image.visible = true
            clip = true

            image.x = -root.x
            image.y = -root.y
        }
    }

    Image {
        id: image
        visible: false
    }

}
