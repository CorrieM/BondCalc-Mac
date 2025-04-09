@echo off
netsh advfirewall firewall add rule name="IGrow Bonds Inbound" dir=in action=allow protocol=TCP localport=5001
netsh advfirewall firewall add rule name="IGrow Bonds Outbound" dir=out action=allow protocol=TCP localport=5001
pause