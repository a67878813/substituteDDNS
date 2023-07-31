import requests
import time
import json
import os
import sys
from enum import Enum

# print(sys.platform)
if "win" in sys.platform:
    hosts = r"c:\Windows\System32\drivers\etc\hosts"
else:
    hosts = r"\etc\hosts"

LOG = True
log_file = r"uploaded.log"
# default config_data ,enable when config.json dosn't exist.
list_test = ['lib.com']
config_data = {
    'behavior': 'Behavior.SERVER',
    'ServerIp': "192.168.88.230", 'ServerPort': '8888',
    'current_ip': '222.222.222.222', 'ip_-1': '222.222.111.111',
    'local_ip_to_server_domain': 'lib.com',
    'lib.com': "222.222.222.222",
    'readed_domain': list_test,
}


def hello_message():
    mes = "\n substituteDDNS 0.1 written by Esir at 2023.07 \n ALL COPYRIGHTES RESERVED\n"
    return mes

class Behavior(Enum):
    SERVER = 1
    CLIENT_UP = 2
    CLIENT_GET = 3


def load_json():
    file_path = "config.json"
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    with open(file_path, "r") as load_f:
        load_dic = json.load(load_f)
        #print("loaded: ", load_dic)
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
return_false_data = {'error': 'default error msg', }


def nowtimestr():
    return time.strftime("%Y/%m/%d %H:%M:%S", (time.localtime()))


# server needs
if my_behavior == Behavior.SERVER:
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
                #print(_path)
                if (len(_path) > 1) & (_path in config_data.keys()):
                    # send {domain: ip}
                    self.wfile.write(json.dumps(
                        {_path: config_data[_path]}).encode("utf-8"))
                else:
                    err_data = return_false_data
                    err_data['error'] = "can not find domain"
                    self.wfile.write(json.dumps(err_data).encode("utf-8"))
            else:
                # send {error}
                self.wfile.write(json.dumps(return_false_data).encode("utf-8"))

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
                C_FLAG = False
                for posted_domain in _tempdict.keys():
                    if posted_domain in config_data.keys():
                        if _tempdict[posted_domain] != config_data[posted_domain]:
                            C_FLAG = True
                            config_data["ip_-1"] = config_data[posted_domain]
                            # update value
                            config_data[posted_domain] = _tempdict[posted_domain]
                            print("update value at ", posted_domain,
                                  " : ", config_data[posted_domain])
                            if LOG == True:
                                with open(log_file, 'a+') as f:
                                    # log  domian = new ip
                                    f.write(nowtimestr() + posted_domain +
                                            "= " + config_data[posted_domain] + "\n")
                if C_FLAG == True:
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


def update_hosts(_new_dict):
    """
    call this func ONLY when there are changes.
    """
    with open(hosts, 'r', encoding='utf-8') as f:
        readed_host = f.readlines()

    for i in range(len(readed_host)):
        if readed_host[i][0] != '#':
            this_line = readed_host[i].split()
            if len(this_line) > 1:  # at least 2 elem.
                # this_line
                # 0 ip   1 domain
                if (this_line[1] in _new_dict.keys()):
                    #                                         to ip wrong
                    print("replaced domain :", this_line[1], " to ip ",
                          _new_dict[this_line[1]], " with ", this_line[1])
                    this_line[0] = _new_dict[this_line[1]]
                    readed_host[i] = " ".join(this_line)

    # save new hosts file
    with open(hosts, 'w', encoding='utf-8') as f:
        f.writelines(readed_host)


def my_getIP():
    ip = requests.get(r'http://ifconfig.me/ip')
    return ip.text.strip()


def my_get_server_inner_IP():
    ip = requests.get(r'http://ifconfig.me/ip')
    return ip.text.strip()


def write_json(j_dic):
    file_path = "config.json"
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    with open(file_path, "w") as f:
        json.dump(j_dic, f)
        print("written: ", j_dic)

# write_json(config_data)


def get_requrl():
    requrl = "http://" + config_data['ServerIp'] + ":" + config_data['ServerPort'] + "/"  \
        + config_data['local_ip_to_server_domain']
    return requrl


def get_server_innerIPs(_domain_name_list=['lib.com']):
    #curr_ip = my_getIP()
    return_dict = {}
    for _domain_name in _domain_name_list:
        if _domain_name != "":
            requrl = "http://" + config_data['ServerIp'] + ":" + config_data['ServerPort'] + "/"  \
                + _domain_name
            #print(requrl)
            response = requests.get(requrl)
            if "error" not in response.json().keys():
                return_dict.update(response.json())
            else:
                print("ERROR: at get_server_innerIPs")
                print("\t","requrl: ",requrl)
                print("\terror msg : ", response.json()['error'])
    return return_dict


def get_server_innerIP(_domain_name='lib.com'):
    requrl = "http://" + config_data['ServerIp'] + ":" + config_data['ServerPort'] + "/"  \
        + _domain_name
    response = requests.get(requrl)
    r_data = json.loads(response.content.decode('UTF-8'))
    return r_data


def post_server_innerIP():
    pass
    curr_ip = my_getIP()
    if(config_data['current_ip'] != curr_ip):
        domain_name = config_data['local_ip_to_server_domain']  # update local

        # update server
        # server
        response = requests.post(get_requrl(), json={domain_name: curr_ip}
                                 )
        print(nowtimestr(), " updated IP:", curr_ip, " ", )
        # local
        temp_value = config_data['current_ip']
        config_data['ip_-1'] = temp_value
        config_data['current_ip'] = curr_ip
        write_json(config_data)
        if LOG == True:
            with open(log_file, 'a+') as f:
                f.write(nowtimestr() + " updated IP:" + curr_ip + "\n")


if __name__ == "__main__":
    # check config.json, create new if not exist.
    print(hello_message())
    print("============================")
    print("============================")
    if (not os.path.exists("config.json")):
        # print('here')
        if my_behavior == Behavior.SERVER:
            config_data['ServerIp'] = my_getIP()
        write_json(config_data)
    else:
        # read json from config.json
        # print('tt')
        config_data = load_json()
        my_behavior = eval(config_data['behavior'])

    if my_behavior == Behavior.SERVER:
        # server
        pass
        host = (config_data['ServerIp'],  int(config_data['ServerPort']))
        server = HTTPServer(host,
                            Resquest)
        print("Starting server, listen at: %s:%s" % host)
        server.serve_forever()

    if my_behavior == Behavior.CLIENT_UP:
        # upload ip
        print("Starting client ip, to host %s" % config_data['ServerIp'])
        while(1):
            post_server_innerIP()
            time.sleep(60)

    if my_behavior == Behavior.CLIENT_GET:
        # get ip
        while(1):
            _tempdict = get_server_innerIPs(config_data['readed_domain'])
            if _tempdict != {}:
                #print(_tempdict)
                C_FLAG = False

                # update config fire
                for _domain in _tempdict.keys():
                    if _domain in config_data.keys():
                        # check domin: ip changes
                        if _tempdict[_domain] != config_data[_domain]:
                            C_FLAG = True
                            # update value
                            config_data[_domain] = _tempdict[_domain]
                            # print("update value at ", _domain,
                            #         " : ", config_data[_domain])

                if C_FLAG == True:
                    # write to disk
                    write_json(config_data)

                    # update HOST file
                    update_hosts(_tempdict)

            time.sleep(60)
