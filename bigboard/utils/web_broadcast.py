import paramiko
from bigboard.utils.besteffortbroadcast import BestEffortBroadcast
from multiprocessing import Process, Manager
from time import sleep
from requests import get


class WebBroadcast:
    def __init__(self, robot_address_list, data, command):
        self.robot_address_list = robot_address_list
        self.input = data
        self.command = command

    def run(self):
        web_address = get('https://api.ipify.org').text
        address_list = self.robot_address_list + [web_address]
        self.command[len(self.command) - 1] += ' ' + ','.join(address_list)

        with Manager() as manager:
            result_list = manager.list()
            processes = []

            for address in self.robot_address_list:
                process = Process(target=self.start_robot_socket, args=(address, result_list, self.command))
                processes.append(process)

            for process in processes:
                process.start()

            sleep(3.0)

            beb = BestEffortBroadcast(address=web_address, process_address_list=address_list)
            beb.broadcast(self.input)
            beb.deliver()
            beb.close()

            for process in processes:
                process.join()

            return [x for x in result_list]

    def start_robot_socket(self, address, result_list, command):
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(address, 22, "mhc", "mhcrobots", timeout=5)
            (stdin, stdout, stderror) = ssh.exec_command('; '.join(command), timeout=10)
            result = (address, stdout.readlines(), stderror.readlines())
            result_list.append(result)
        except:
            result = (address, [], ['Cannot connect to ip address'])
            result_list.append(result)
