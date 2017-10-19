#!/bin/python
# -*- coding: utf-8 -*-

import sys
from utils.http import AgriHubAPI


class AgriHubNode:
    def __init__(self):
        self.agri_hub = AgriHubAPI()

    @staticmethod
    def print_info():
        print(
            "Usage: \n"
            "$ agrihub-node.py [option] \n\n"
            "Option: \n"
            "start, bootstrap app \n"
            "shell, start CLI"
        )

    def action_start(self):
        self.agri_hub.auth()
        # TODO loop forever! Call .subscribe() based on schedule
        self.agri_hub.subscribe()

    def run(self):
        if 2 is not len(sys.argv):
            self.print_info()
            exit(0)

        if "start" == sys.argv[1]:
            self.action_start()
            print('start the app')
        elif "shell" == sys.argv[1]:
            print('start cli')
        elif "test" == sys.argv[1]:
            print('start the test')
        else:
            self.print_info()

if __name__ == "__main__":
    main = AgriHubNode()
    main.run()
