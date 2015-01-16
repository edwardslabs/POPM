def isIP(address):
#Takes a string and returns a status if it matches
#a ipv4 address
# 0 = false / 1 = true
ip = False
try:
    if address[0].isdigit():
        octets = address.split('.')
        if len(octets) == 4:
            ipAddr = "".join(octets)
            if ipAddr.isdigit():
            #correct format
                if (int(octets[0]) >= 0) and (int(octets[0]) <= 255):
                    if (int(octets[1]) >= 0) and (int(octets[1]) <= 255):
                        if (int(octets[2]) >= 0) and (int(octets[2]) <= 255):
                            if (int(octets[3]) >= 0) and (int(octets[3]) <= 255):
                                ip = True
except IndexError:
    pass
return ip