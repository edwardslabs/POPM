# POPM
#### Python Open Proxy Monitor

Intro
---
POPM was created to be a one use tool for helping to block malicious users connecting via proxies and under connections that have been deemed unsafe. The goal of POPM is to be an easy to use, simple to configure, proxy monitor that can support an array of IRCds, as well as be able to be configured as a pseudo server, oper, or regular client for guarding channels.

Design Stage
---
POPM is still an early project, so many things are still yet to be thoroughly tested. A list of features that are planned will come either soon, or are already attached to this repo under "TODO"

Set up
---
Python 2.7 or newer is required for POPM to function.
The basic config.yaml file can be broken down as follows:

####Server
* name: This should be the name of your IRC network (e.g. GameSurge)
* host: The uplink IP address or hostname
* port: The port to connect to
* self-server-host-name: What POPM will identify itself as to the uplink
* hops: This should only need to be set to 1
* server_description: Gives your server a description when viewing clients from /whois or looking at /map or /links
* server_numeric: The UID for POPM
* server_password: The password to send to the uplink while connecting
* protocol: Protocol used to connect to the IRCd (Only P10Server is available right now)

####proxy - Note that variables may be used in these messages
* dnsbl-ban-message: Options that may be added to reason: {network} will be replaced with your Network's name (defined in Server -> name), {list} will be replaced with the DNS Black list the user was on.
* http-ban-message: Options that may be added to reason: {network} will be replaced with your Network's name (defined in Server -> name), {port} will be replaced with the port that was detected by the http_connect monitor.
* socks-ban-message: Options that may be added to reason: {network} will be replaced with your Network's name (defined in Server -> name), {version} will be replaced with the SOCKS version (i.e. 4 or 5), {port} will be replaced with the port that was detected by the socks monitor.

####bot
* nick: The bot's nick
* host: The host that the bot will appear under
* gecos: The bot's real name (i.e. Proxy Monitor Service Bot)
* umodes: User modes that the bot should apply to itself when connecting
* debug_channel: The channel where the bot will put special information
* prefix: The command prefix to use the bot without /msging it directly

####database (only works with Postgres at the moment)
* type: Backend software to use. Currently supports MySQL and Postgres
* dbname: Name of the database
* user: Username for the bot to connect
* host: The host of the database server (usually localhost)
* pass: Database password

####misc
* gline_duration: How long in seconds the user will be G-lined for
* scan-on-netburst: This is either a 1 or 0. I.e. true or false. This will determine whether or not POPM will scan all users when initially bursting to the network. (This is not recommended if you have a large network)
* debug_level: 0 - No debug what-so-ever. 1 - Will display critical errors. 2 - Will include information related to proxy/dnsbl triggers. 3 - Will include information related to POPM's user dictionary. 4 - Will print full data as recieved from the uplink. 5 - Everything. Basically things you can and can't imagine.