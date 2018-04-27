DESCRIPTION = "Mender test recipe for persistent data files"

LICENSE = "Apache-2.0"
LIC_FILES_CHKSUM = "file://LICENSE;md5=e3fc50a88d0a364313df4b21ef20c29e"

#RPROVIDES_${PN} = "mender-ezgui"
DEPENDS = "qtbase xserver-common"


SRC_URI = "file://menderEzGUI.py;subdir=${PN}-${PV} \
           file://menderLogin.py;subdir=${PN}-${PV} \
           file://mender_logo.png;subdir=${PN}-${PV} \
           file://mender-ezgui.desktop;subdir=${PN}-${PV} \
           file://LICENSE;subdir=${PN}-${PV} \
          "

do_install() {
    install -d ${D}${sysconfdir}/mender-ezgui
    install -m 0644 menderEzGUI.py ${D}${sysconfdir}/mender-ezgui
    install -m 0644 menderLogin.py ${D}${sysconfdir}/mender-ezgui
    install -m 0644 mender_logo.png ${D}${sysconfdir}/mender-ezgui
    install -d ${D}${sysconfdir}/xdg/autostart
    install -m 0644 mender-ezgui.desktop ${D}${sysconfdir}/xdg/autostart

}
