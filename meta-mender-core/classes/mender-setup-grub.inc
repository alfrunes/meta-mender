EXTRA_IMAGEDEPENDS_append_mender-grub = " grub-efi"

# The device number of the interface to load partitions from. This is normally
# empty, in which case it is deduced from MENDER_STORAGE_DEVICE. Only use this
# if the indexing of devices is different in Grub and in the Linux kernel.
MENDER_GRUB_STORAGE_DEVICE ??= "${MENDER_GRUB_STORAGE_DEVICE_DEFAULT}"
MENDER_GRUB_STORAGE_DEVICE_DEFAULT = ""

IMAGE_BOOT_FILES_append = " ${_MENDER_EFI_BOOT_FILE}"

_MENDER_EFI_BOOT_FILE = ""
_MENDER_EFI_BOOT_FILE_mender-grub_arm = "grub-efi-bootarm.efi;EFI/BOOT/bootarm.efi"
_MENDER_EFI_BOOT_FILE_mender-grub_x86 = "grub-efi-bootia32.efi;EFI/BOOT/boot.efi"
_MENDER_EFI_BOOT_FILE_mender-grub_x86-64 = "grub-efi-bootx64.efi;EFI/BOOT/bootx64.efi"
_MENDER_EFI_BOOT_FILE_mender-grub_mender-bios = ""

# We want to use upstream grub variants if possible. However, we have recipes
# that will be enabled in some configurations where COMPATIBLE_HOSTS doesn't
# match for the upstream recipe. See the recipes-bsp/grub folder.
PREFERRED_PROVIDER_grub-efi ?= "grub-efi"
PREFERRED_RPROVIDER_grub-efi ?= "grub-efi"
PREFERRED_PROVIDER_grub-editenv ?= "grub"
PREFERRED_RPROVIDER_grub-editenv ?= "grub"
