#
# Copyright (C) Fujitsu Limited 2018 All rights reserved
#

import snack, sys

from ..window import ButtonInfoWindow

#------------------------------------------------------------
# def ButtonErrorWindow()
#
#   Display Error Window.
#
# Input:
#    insScreen : screen instance
# Output:
#    -
#------------------------------------------------------------
def ButtonErrorWindow(insScreen, sItem):
    buttons = ["OK"]

    lst_text = []
    lst_text.append("   The following data is invalid\n\n")
    lst_text.append("   - " + sItem)

    main_text = "".join(lst_text)
    del lst_text

    rcode = ButtonInfoWindow(insScreen, "Error", main_text, 80, 4, buttons)

    if rcode == "y":
        sys.exit(0)
