#
# SuicideGirls
# App launch script
#
# by Shawn Rieger / Boxee
#

import mc
import sg

reg = mc.GetApp().GetLocalConfig()

if reg.GetValue("username") and reg.GetValue("password") and sg.check_authentication():
    reg.SetValue("authenticated", "true")
else:
    reg.Reset("authenticated")
    # if sg.login_sg(reg.GetValue('username'), reg.GetValue('password')):
    #	reg.SetValue('authenticated', 'true')

sg.quickLaunch(14000)
