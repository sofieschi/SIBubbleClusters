import QtQuick 2.7
import QtQuick.Controls 2.7

Item
{
    function updateData(data)
    {
        container.visible = data.is_visible;

        texture.width = data.icon_width;
        texture.height = data.icon_height;

        if(data.is_in_preview)
            texture.anchors.leftMargin = 0;
        else
            texture.anchors.leftMargin = texture.width / 2;

        texture.source = data.img_path;

        container.width = data.container_width
        container.height = data.container_height

        filename.color = data.color;
        filename.text = data.name;
        filename.visible = !data.is_in_preview;
    }

    id: container

    visible: true

    Image {
        id: texture
        anchors.left: parent.left
        anchors.top: parent.top
        fillMode: Image.PreserveAspectFit

        visible: true
        cache: true
        asynchronous: true
    }

    Text {
        id: filename
        visible: true

        fontSizeMode: Text.Fit
        minimumPixelSize: 12
        font.pixelSize: 18
        color: "white"
        anchors.verticalCenter: texture.verticalCenter

        width: texture.width * 2
        anchors.top: texture.bottom
        anchors.left: texture.left

        wrapMode: TextEdit.Wrap
    }
}