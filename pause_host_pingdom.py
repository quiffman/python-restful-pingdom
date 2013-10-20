#!/usr/bin/env python
####################################################################
# Script to pause the relivant checks in pingdom for a host        #
# By default the current host is used, and allowing for dns CNAMES #
####################################################################
import ConfigParser
import json
import os.path
import pingdom
import socket
from optparse import OptionParser, OptionGroup


def get_checks_for_host(pingdomObj, hostname=socket.getfqdn()):
    checks = pingdomObj.method('checks')

    addr = socket.gethostbyname(hostname)
    my_checks = []
    for check in checks['checks']:
        (check_hostname, aliaslist, ipaddrlist) = socket.gethostbyname_ex(check['hostname'])
        if ((hostname == check_hostname) or (hostname in aliaslist) or (addr in ipaddrlist)):
            my_checks.append(check)
    return my_checks


# MAIN ()
actions = ['pause','unpause','start','stop','status']

config = ConfigParser.ConfigParser()
config.read(['/etc/sysconfig/pingdom',os.path.expanduser('~/.pingdom')])

parser = OptionParser(
        description='Pause or unpause all pingdom checks for this host.',
        epilog='Action: (' + '|'.join(actions) + ') - this is the action to take for all Pingdom checks for this host. Note: start and stop are synonyms for unpause and pause respectively.')

creds = OptionGroup(parser, 'Pingdom Credentials','Can be passed as commandline options, or read from /etc/sysconfig/pingdom, or ~/.pingdom')
creds.add_option('-u', '--username', help='Your Pingdom username')
creds.add_option('-p', '--password', help='Your Pingdom password')
creds.add_option('-k', '--appkey', help='Your Pingdom application key')
parser.add_option_group(creds)
parser.add_option('--hostname', default=socket.getfqdn(), help='The hostname to stop all checks for.')

defaults = dict(config.items('credentials'))
parser.set_defaults(**defaults)
(opts, args) = parser.parse_args()

if ((not args) or (len(args) > 1) or (args[0] not in actions)):
    parser.error('Action must be one of (' + '|'.join(actions) + ')')

paused = 'true' if args[0] == 'pause' or args[0] == 'stop' else 'false'

pingdomObj = pingdom.Pingdom(username=opts.username, password=opts.password, appkey=opts.appkey)

my_checks = get_checks_for_host(pingdomObj, opts.hostname)

if not my_checks:
    print 'No checks found for this host.'
    exit(0)

if args[0] == 'status':
    for check in my_checks:
        print "%s: %s" % (check['name'], check['status'])
    exit(0)

checkids = ','.join(str(check['id']) for check in my_checks)

response = pingdomObj.method('checks', method='PUT', parameters={'paused': paused, 'checkids': checkids})
for check in my_checks:
    print check['name']
print response['message']

# vim: set ts=4 sw=4 tw=0 et:
