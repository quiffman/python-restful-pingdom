#!/usr/bin/env python
import json, os.path, pingdom, socket
from optparse import OptionParser, OptionGroup
import ConfigParser

def get_checks_for_host(p, hostname=socket.getfqdn()):
    checks = p.method('checks')

    #print checks
    addr = socket.gethostbyname(hostname)
    my_checks = []
    for check in checks['checks']:
        (check_hostname, aliaslist, ipaddrlist) = socket.gethostbyname_ex(check['hostname'])
        if hostname == check_hostname or hostname in aliaslist or addr in ipaddrlist:
            #print check
            my_checks.append(check)
    return my_checks

# MAIN

actions = ['pause','unpause','start','stop','status']

config = ConfigParser.ConfigParser()
config.read(['/etc/sysconfig/pingdom',os.path.expanduser('~/.pingdom')])

parser = OptionParser(
        description='Pause or unpause all pingdom checks for this host.',
        epilog='Action: (' + '|'.join(actions) + ') - this is the action to take for all Pingdom checks for this host.\nNote: start and stop are synonyms for unpause and pause respectively.')

creds = OptionGroup(parser, 'Pingdom Credentials','Can be passed as commandline options, or read from /etc/sysconfig/pingdom, or ~/.pingdom')
creds.add_option('-u', '--username', help='Your Pingdom username')
creds.add_option('-p', '--password', help='Your Pingdom password')
creds.add_option('-k', '--appkey', help='Your Pingdom application key')
parser.add_option_group(creds)
parser.add_option('--hostname', default=socket.getfqdn(), help='The hostname to stop all checks for.')

defaults = dict(config.items('credentials'))
parser.set_defaults(**defaults)

(opts, args) = parser.parse_args()

if not args or len(args) > 1 or args[0] not in actions:
    parser.error('Action must be one of (' + '|'.join(actions) + ')')

paused = 'true' if args[0] == 'pause' or args[0] == 'stop' else 'false'

p = pingdom.Pingdom(username=opts.username, password=opts.password, appkey=opts.appkey)

my_checks = get_checks_for_host(p, opts.hostname)

if not my_checks:
    print 'No checks found for this host.'
    exit(0)

if args[0] == 'status':
    for x in my_checks:
        print "%s: %s" % (x['name'], x['status'])
    exit(0)

checkids = ','.join(str(x['id']) for x in my_checks)

response = p.method('checks', method='PUT', parameters={'paused': paused, 'checkids': checkids})
for x in my_checks:
    print x['name']
print response['message']

# vim: set ts=4 sw=4 tw=0 et:
