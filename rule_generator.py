#!/usr/bin/python
#
# Copyright 2016, Mithil Arun
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import  datetime
import  time
import  shlex
import  subprocess

# Global constants
FREQUENCY = 5

class RuleGenerator(object):

    def __init__(self):
        # Nothing to do for now
        return

    def run_cmd(self, cmd=None):
        if cmd is None:
            return

        args = shlex.split(cmd)

        try:
            subprocess.check_call(args)
        except subprocess.CalledProcessError:
            print "Failed to run command " + cmd

    def make_cmd(self, rule=None):
        if rule is None:
            return

        cmd = "ovs-vsctl set interface "
        cmd += rule['port']
        cmd += " ingress_policing_burst="
        cmd += rule['bw']

        return cmd

    def read_data(self):
        # TODO: Need to figure out the interface from the RRDTool database
        data = {}
        return data

    def publish_rule(self, rule=None):
        if rule is None:
            return

        cmd = self.make_cmd(rule)
        self.run_cmd(cmd)

    def create_rules(self):
        # do whatever
        data = self.read_data()

        for entry in data:
            while entry['time'] == datetime.datetime.now().time():
                self.publish_rule(entry)
                time.sleep(FREQUENCY)

def main():
    rule_gen = RuleGenerator()
    rule_gen.create_rules()

if __name__ == '__main__':
    main()
