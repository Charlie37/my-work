import QtQuick 2.1
import QtGraphicalEffects 1.0
import "../../sheets"
import "sequence"


// Goal is to apply a shader to our own object of image sequence.

Sheet {
    id: root
    title: "Sequence (click to start)"

    width: 1360
    height: 480


    MySequence {
        id: anim
        x: 0; y: 0
        from: 0; to: 39
        imagesDirectory:"./sequence/intro_"

        loops: -1 // infinite
        mirror: true
        //running: true
        //framerate: 10
        states: [   State {
                        name: "running";
                        PropertyChanges { target: anim; running: true }
                    },
                    State {
                        name: "not_running";
                    }]
    }

    // "ShaderEffect: source or provider missing when binding textures"
    // Qt glitch ?
    // https://bugreports.qt-project.org/browse/QTBUG-34676
    /*BrightnessContrast {
        anchors.fill: anim2
        source: anim2
        brightness: 0
        contrast: 1
    }

    HueSaturation {
        anchors.fill: anim2
        source: anim2
        hue: -0.5
    }*/

    // Our own shader
    ShaderEffect {
                x: root.width - anim.width
                width: anim.width; height: anim.height
                anchors.verticalCenter: parent.verticalCenter

                property variant src: anim

                vertexShader: "
                    uniform highp mat4 qt_Matrix;
                    attribute highp vec4 qt_Vertex;
                    attribute highp vec2 qt_MultiTexCoord0;
                    varying highp vec2 coord;
                    void main() {
                        coord = qt_MultiTexCoord0;
                        gl_Position = qt_Matrix * qt_Vertex;
                    }"
                fragmentShader: "
                    varying highp vec2 coord;
                    uniform sampler2D src;
                    uniform lowp float qt_Opacity;
                    void main() {
                        lowp vec4 tex = texture2D(src, coord);
                // blue to orange (invert blue and red channels)
                gl_FragColor = vec4(tex.b, tex.g, tex.r, tex.a) * qt_Opacity;
                // blue to red
                //gl_FragColor = vec4(tex.b, tex.g/4.0, tex.r/4.0, tex.a) * qt_Opacity;

                          }"

                // Same
                //gl_FragColor = vec4(tex.r, tex.g, tex.b, tex.a) * qt_Opacity;
                // blue to white
                //gl_FragColor = vec4(vec3(dot(tex.rgb, vec3(0, 0, 1))), tex.a) * qt_Opacity;
                // only blue
                //gl_FragColor = vec4(0.0, 0.0, tex.b, tex.a) * qt_Opacity;
                // Greyscale
                //gl_FragColor = vec4(vec3(dot(tex.rgb, vec3(0.344, 0.5, 0.156))), tex.a) * qt_Opacity;
    }

    MouseArea {
       id: mouseArea
       anchors.fill: parent
       onClicked: {
           anim.state = "running";
       }

       onReleased: {
           anim.state = "not_running";
       }
    }


}

