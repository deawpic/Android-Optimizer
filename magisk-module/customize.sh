# Magisk / KernelSU / APatch module installer script
SKIPUNZIP=0

ui_print "****************************************"
ui_print "* Kernel, GPU & Thermal Optimizer v2.5 *"
ui_print "*      Magisk / KernelSU / APatch      *"
ui_print "****************************************"
ui_print "- Installing module files..."

set_perm "$MODPATH/service.sh" 0 0 0755
set_perm "$MODPATH/uninstall.sh" 0 0 0755

ui_print "- Configured executable permissions."
ui_print "- Optimizations will apply automatically on boot."
