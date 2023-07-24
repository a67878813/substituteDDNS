import requests
import time
import json
import os
import sys
from enum import Enum

#print(sys.platform)
if "win" in sys.platform:
    hosts = r"c:\Windows\System32\drivers\etc\hosts"
else :
    hosts = r"\etc\hosts"

LOG = True
log_file = r"uploaded.log"
#default config_data ,enable when config.json isn't exist.
config_data = {
    'behavior': 'Behavior.SERVER',
    'ServerIp': "192.168.88.230", 'ServerPort': '8888',
    'current_ip': '222.222.222.222', 'ip_-1': '222.222.111.111',
    'change_domain_name': 'lib.com',
    'lib.com': "222.222.222.222"
}
class Behavior(Enum):
    SERVER= 1
    CLIENT_UP =2
    CLIENT_GET =3
def load_json():
    file_path = "config.json"
    if len(sys.argv)>1:
        file_path = sys.argv[1]
    with open(file_path,"r") as load_f:
        load_dic = json.load(load_f)
        print("loaded: ", load_dic)
    return load_dic


if (os.path.exists("config.json")):
    config_data = load_json()
    my_behavior = eval(config_data['behavior'])


my_behavior = eval(config_data['behavior'])

data_respond_PSOT = {
    'result_code': '2',
    'result_desc': 'Success',
    'timestamp': '',
    'data': ''  # {'message_id': '25d55ad283aa400af464c76d713c07ad'}
}
return_false_data = {'error': 'has_error',}



def nowtimestr():
    return time.strftime("%Y/%m/%d %H:%M:%S", (time.localtime()) )
#server needs
if my_behavior ==Behavior.SERVER:
    from http.server import HTTPServer, BaseHTTPRequestHandler
    import json
    import shutil
    import io
    import urllib



    class Resquest(BaseHTTPRequestHandler):
        def do_GET(self):
            path = str(self.path)
            # print(path)
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            if len(path) > 1:  # path == "/accc":
                _path = path[1:]
                # print(_path)
                if (len(_path) > 1) & (_path in config_data.keys()):
                    # send {domain: ip}
                    self.wfile.write(json.dumps(
                        {_path: config_data[_path]}).encode())
            else:
                #send {error}
                self.wfile.write(json.dumps(return_false_data).encode())

        def do_POST(self):
            # print("get POST")
            path = str(self.path)
            # print(path)
            req_datas = self.rfile.read(
                int(self.headers['content-length']))  # 重点在此步!
            _tempdict = json.loads(req_datas.decode('UTF-8'))
            # print(_tempdict)
            # update dict
            if len(path) > 1:
                _path = path[1:]
                if _path in config_data.keys() & _path in config_data.keys():
                    if _tempdict[_path] != config_data[_path]:
                        config_data["ip_-1"] = config_data[_path]
                        config_data[_path] = _tempdict[_path]  # update value
                        print("update value at ", _path, " : ", config_data[_path])
                        if LOG == True:
                            with open(log_file,'a+') as f:
                                f.write(nowtimestr()+ _path+"= "+ config_data[_path]+  "\n")
                        # write to disk
                        write_json(config_data)

            # update dict end

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(data_respond_PSOT).encode('utf-8'))

        def do_action(self, path, args):
            self.outputtxt(path + args)

        def outputtxt(self, cotnent):
            enc = "UTF-8"
            content = content.encode(enc)
            f = io.BytesIO()
            f.write(content)
            f.seek(0)
            self.send_response(200)
            self.send_header("Content-type", "text/html;charset=%s" % enc)
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            shutil.copyfileobj(f, self.wfile)




def update_hosts(new_ip):
    with open(hosts,'r') as f:
        readed_host = f.readlines()
    

    # replace ip
    #NEED_UPDQATE = False
    for i in range(len(readed_host)):
        if readed_host[i][0] != '#':
            this_line = readed_host[i].split()
            if len(this_line) >0:
                #this_line  
                # 0 ip   1 domain
                if  (this_line[1] in config_data.keys()):
                    print("replaced domain :",this_line[1]," to ip ", config_data[this_line[1]] , " with ", this_line[1] )
                    this_line[0] = config_data[this_line[1] ]
                    readed_host[i] = " ".join(this_line)

    # save new hosts file
    with open(hosts,'w') as f:
        f.writelines(readed_host)

def my_getIP():
    ip =requests.get(r'http://ifconfig.me/ip')
    return ip.text.strip()

def write_json(j_dic):
    file_path = "config.json"
    if len(sys.argv)>1:
        file_path = sys.argv[1]
    with open(file_path,"w") as f:
        json.dump(j_dic,f)
        print("written: ", j_dic )

#write_json(config_data)


def get_requrl():
    requrl = "http://" + config_data['ServerIp'] + ":" + config_data['ServerPort'] + "/"  \
            + config_data['change_domain_name']
    return requrl


def get_server_innerIP():
    response = requests.get(get_requrl())
    r_data = json.loads(response.content.decode('UTF-8'))
    print(r_data)




def post_server_innerIP():
    pass
    curr_ip = my_getIP()
    if(config_data['current_ip']!= curr_ip):
        domain_name = config_data['change_domain_name']  # update local

        #update server
        response = requests.post(get_requrl(),json=json.dumps(  
            {domain_name:curr_ip}
                                                        ))
        print(nowtimestr(), " updated IP:", curr_ip, " ", )
        temp_value = config_data['current_ip']
        config_data['ip_-1'] = temp_value
        config_data['current_ip'] = curr_ip
        write_json(config_data)
        if LOG == True:
            with open(log_file,'a+') as f:
                f.write(nowtimestr()+ " updated IP:"+ curr_ip+ "\n")




if __name__ == "__main__":
    #check config.json, create new if not exist.
    if (not os.path.exists("config.json")):
        #print('here')
        if my_behavior == Behavior.SERVER:
            config_data['ServerIp']= my_getIP()
        write_json(config_data)
    else:
        #read json from config.json
        #print('tt')
        config_data = load_json()
        my_behavior = eval(config_data['behavior'])

    if my_behavior == Behavior.SERVER:
        #server
        pass
        host = (config_data['ServerIp']  ,  int(config_data['ServerPort'])      )
        server = HTTPServer(host , \
                             Resquest)
        print("Starting server, listen at: %s:%s" % host)
        server.serve_forever()

    if my_behavior == Behavior.CLIENT_UP:
        # upload ip
        pass
        while(1):
            post_server_innerIP()
            time.sleep(60)
            

    if my_behavior == Behavior.CLIENT_GET:
        #get ip
        while(1):

            new_ = my_getIP()
            if config_data[config_data['change_domain_name']] != new_:

            # if ip changed 
                #update local config_data
                config_data[config_data['change_domain_name']] = new_

                update_hosts(new_)
                #update local
            time.sleep(60)