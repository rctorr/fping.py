#!/usr/bin/env python
"""
Simple generator of fping test commands.

    Takes no options. Executing the script will create a shell script in the
    current directory.

    Requires two files in the current directory: 'testing', and 'testing2'
        testing:  Should contain host name(s) that you know can be resolved to
                  an IP address, IP address(es) that you know can be resolved
                  to a host name, and a host name that you know can NOT be
                  resolved to an IP address.
        testing2: Should contain at least one IP network in CIDR format, and
                  one range of IP addresses in the format of {startIP} {endIP}.
                  To ensure proper testing, make sure at least some IP's in
                  each set can be pinged.
"""

from __future__ import print_function

__author__ = 'NetworkEng - https://github.com/NetworkEng/fping'

opts = 'fgVAnau'
# Since the 'f' option is always set... e.g.
r = range(2 ** (len(opts) - 1), 2 ** len(opts))
bin_strings = [(str(bin(x))).lstrip('0b') for x in r]


def header(text):
    return str(text.center(len(text) + 2, ' ')).center(60, '=')

with open('fpingtest.sh', 'w') as script:
    script.write('#!/bin/bash\n')
    script.write('echo "NOTICE: Please ensure your firewall is set to block '
                 'incoming ICMP such that pinging your localhost (127.0.0.1) '
                 'will fail to reply."\n\n')
    toggle = True
    for word in bin_strings:
        f, g, V, A, n, a, u = [int(word[z]) for z in range(len(word))]
        cmd = 'fping -'
        # a and u are mutually exclusive, so since we use 2 bits wth only 3
        # out of 4 possible outcomes are desired (a is True or u is True or
        # a and u are True (but only once), we need to set up a toggle to
        # skip the duplicate where a == u.
        if not a == u:
            if u:
                cmd += 'u'
            if a:
                cmd += 'a'
        elif toggle:
            toggle = False
            pass
        elif not toggle:
            toggle = True
            continue
        if n:
            cmd += 'n'
        if A:
            cmd += 'A'
        if V:
            cmd += 'V'
        # we use a different test files for hosts and networks due to how the
        # g option works. Since the f (file) option requires 1 argument, we set
        # it here.
        if g == 0:
            cmd += 'f testing'
        elif g == 1:
            with open('testing2') as net_file:
                lines = [line.strip() for line in net_file.readlines()]
            lines = [line for line in lines if len(line) > 0]
            cmds = [cmd + 'g ' + line for line in lines]
            sep = '=' * 60
            script.write('echo -e "\\n' + header(cmd + 'g') + '"\n')
            script.write('echo -e "' + '\\n'.join(lines) + '"\n')
            script.write('echo -e "' + sep + '"\n')
            for cmd in cmds:
                script.write(cmd + '\n')
            continue

        script.write('echo -e "\n' + header(cmd) + '"\n' + cmd + '\n')
