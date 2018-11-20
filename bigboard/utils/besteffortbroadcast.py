from bigboard.utils.perfectpointtopointlinks import PerfectPointToPointLinks

PORT = 10000

"""
besteffortbroadcast.py

BEB object with broadcast and deliver methods
"""
class BestEffortBroadcast:
    # initialize PP2PLs
    def __init__(self, address, process_address_list):
        self.links = PerfectPointToPointLinks(PORT, address)
        self.address_list = process_address_list

    # broadcast a message to all processes
    def broadcast(self, message):
        for process_addr in self.address_list:
            self.links.send(PORT, process_addr, message)

    # deliver a message broadcasted by a process
    def deliver(self):
        return self.links.deliver()

    # close broadcast
    def close(self):
        self.links.close()
