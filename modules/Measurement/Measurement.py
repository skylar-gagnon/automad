from abc import ABC, abstractmethod
from xml.dom import minidom
from paramiko import SSHClient, client
import paramiko
import platform
import os

class Measurement(ABC):
     
    def __init__(self, conf_file):
        '''
        Constructor
        '''
        self.conf_file=conf_file
        self.xmldoc = minidom.parse(conf_file)
        
        #most of the below are expected to be initialized in init function (should be called after constructor)
        self.targetRunDir= None
        self.targetHostname= None
        self.targetSSHusername= None
        self.targetSSHpassword = None
        self.coresToUse=None
        self.sourceFilePath=None #to be set in setSourceFilePath funtion
        super().__init__()

    #def init(self):
    #    pass

    def init(self): #should be called after constructor.. this can be overridden by child measurement classes to add new or use other configuration parameters..
        self.targetRunDir= self.try_get_string_value('targetRunDir')
        self.targetHostname= self.try_get_string_value('targetHostname')
        self.targetSSHusername= self.try_get_string_value('targetSSHusername')
        self.targetSSHpassword = self.try_get_string_value('targetSSHpassword')
        coresToUseString=self.try_get_string_value('coresToUse')
        if coresToUseString:
            self.coresToUse=[]
            for core in coresToUseString.split(" "):
                self.coresToUse.append(int(core))
    
    def try_get_string_value(self,key):
        try:
            value=self.xmldoc.getElementsByTagName(key)[0].attributes['value'].value;
            return value
        except:
            print("Warning failed to read "+str(key))
        
    def try_get_int_value(self,key):
        try:
            value=int(self.xmldoc.getElementsByTagName(key)[0].attributes['value'].value);
            return value
        except:
            print("Warning failed to read "+str(key))

    def set_source_file_path(self,source_file_path):
        self.source_file_path = source_file_path

    @abstractmethod
    def measure(self):
        pass

    ## utility function for executing commands over ssh connection.. very common functionality
    def execute_ssh_command(self,command,continousAttempt=True,max_tries=10):
        paramiko.util.log_to_file("tmp/test.log")
        tries=0
        while True:
            try:
                ssh = SSHClient()
                ssh.set_missing_host_key_policy(client.AutoAddPolicy()) 
                ssh.connect(self.targetHostname, username=self.targetSSHusername, password=self.targetSSHpassword)
                stdin,stdout,stderr = ssh.exec_command(command)
                lines=[]
                for line in stdout.readlines():
                    lines.append(line)
                return lines
            except:
                if continousAttempt and tries<max_tries:
                    tries=tries+1
                    continue
                else:
                    raise("Exception: Unable to execute command "+str(command))
            finally:
                ssh.close()


    #### utility function for copying the source file over ssh connection.. very common functionality        
    def copy_file_over_ftp(self,continousAttempt=False):
        paramiko.util.log_to_file("tmp/test.log")
        while True:
            try:
                ssh = SSHClient()
                ssh.set_missing_host_key_policy(client.AutoAddPolicy()) 
                ssh.connect(self.targetHostname, username=self.targetSSHusername, password=self.targetSSHpassword)
                sftp=ssh.open_sftp();
                sftp.put(self.source_file_path,self.targetRunDir + "test")
                break    
            except:
                if continousAttempt:
                    continue
                else:
                    raise("Exception: Unable to copy file")
            finally:
                sftp.close()
                ssh.close()




    def ping (self,host):
        """
        Returns True if host responds to a ping request
        """
        # Ping parameters as function of OS
        ping_str = "-n 1" if  platform.system().lower()=="windows" else "-c 1"
        
        # Ping
        return os.system("ping " + ping_str + " " + host) == 0  
