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

import datetime
import time
import shlex
import subprocess

import MySQLdb as db

# Global constants
FREQUENCY = 5


class RuleGenerator(object):

    def __init__(self):
        # Nothing to do for now
        return

    @staticmethod
    def run_cmd(cmd=None):
        if cmd is None:
            return

        args = shlex.split(cmd)

        try:
            subprocess.check_call(args)
        except subprocess.CalledProcessError:
            print "Failed to run command " + cmd

    @staticmethod
    def make_cmd(rule=None):
        if rule is None:
            return

        cmd = "ovs-vsctl set interface "
        cmd += rule['port']
        cmd += " ingress_policing_burst="
        cmd += rule['bw']

        return cmd

    @staticmethod
    def read_data():
        data = []

        predicted_db = db.connect(host='192.168.1.7', user='ubuntu', passwd='123456',
                                  db="predicted_bandwidth", port=3306)
        cursor = predicted_db.cursor()

        # Need to get a list of tables
        cursor.execute("show tables;")
        try:
            tables = cursor.fetchall()
        except db.Error:
            print "Unable to read from predicted_bandwidth db"
            return None

        table_list = [table[0] for table in tables]

        for table in table_list:
            query = "select * from %s", table
            cursor.execute(query)

            try:
                entries = cursor.fetchall()
            except db.Error:
                print "Unable fetch entries from %s table", table

            for entry in entries:
                temp = {}
                temp['time'] = entry[0]
                temp['port'] = entry[1]
                temp['bw'] = entry[2]

                data.append(temp)

            predicted_db.close()

        return data

    def publish_rule(self, rule=None):
        if rule is None:
            return

        cmd = self.make_cmd(rule)
        self.run_cmd(cmd)

    def create_rules(self):
        # do whatever
        data = self.read_data()

        if data is None:
            return -1

        for entry in data:
            while entry['time'] == datetime.datetime.now().time():
                self.publish_rule(entry)
                time.sleep(FREQUENCY)

        return 0


def main():
    rule_gen = RuleGenerator()
    if rule_gen.create_rules() != 0:
        print "Failed to generate rules. Exiting."

if __name__ == '__main__':
    main()
