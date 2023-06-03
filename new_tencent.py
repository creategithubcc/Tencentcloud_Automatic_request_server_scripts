import re

import requests
import random
import time
import json
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.cvm.v20170312 import cvm_client, models


region_zone_dict = {
    'ap-guangzhou': ['ap-guangzhou-3','ap-guangzhou-4','ap-guangzhou-6'],
    # 'ap-shanghai': ['ap-shanghai-2','ap-shanghai-3','ap-shanghai-4','ap-shanghai-5'],
    # 'ap-nanjing': ['ap-nanjing-1','ap-nanjing-2'],
    # 'ap-beijing': ['ap-beijing-1','ap-beijing-2','ap-beijing-3','ap-beijing-4','ap-beijing-5','ap-beijing-6','ap-beijing-7'],
    # 'ap-chengdu': ['ap-chengdu-1','ap-chengdu-2'],
    # 'ap-chongqing': ['ap-chongqing-1'],
    # 'ap-hongkong': ['ap-hongkong-2','ap-hongkong-3'],
    # 'ap-singapore': ['ap-singapore-1','ap-singapore-2','ap-singapore-3'],
    # 'ap-jakarta': ['ap-jakarta-1'],
    # 'ap-seoul': ['ap-seoul-1','ap-seoul-2'],
    # 'ap-tokyo': ['ap-tokyo-1','ap-tokyo-2'],
    # 'ap-mumbai': ['ap-mumbai-1','ap-mumbai-2'],
    # 'ap-bangkok': ['ap-bangkok-1'],
    # 'na-toronto': ['na-toronto-1'],
    # 'na-siliconvalley': ['na-siliconvalley-1','na-siliconvalley-2'],
    # 'na-ashburn': ['na-ashburn-1','na-ashburn-2'],
    # 'eu-frankfurt': ['eu-frankfurt-1'],
}



#创建服务器（大约需要四~五分钟）
def createserver():
    try:
        cred = credential.Credential("aaaaa", "bbbbb")#输入你的key和密码
        httpProfile = HttpProfile()
        httpProfile.endpoint = "cvm.tencentcloudapi.com"
        clientProfile = ClientProfile()
        clientProfile.httpProfile = httpProfile
        client = cvm_client.CvmClient(cred, reg, clientProfile)

        req = models.RunInstancesRequest()#接下来模拟json发包
        params = {
            "InstanceChargeType": "POSTPAID_BY_HOUR",
            "Placement": {
                "Zone": zon#选择国家地区
            },
            "InstanceType": "SA2.MEDIUM2",#服务器配置
            "ImageId": "img-487zeit5",
            "InternetAccessible": {
                "InternetChargeType": "BANDWIDTH_POSTPAID_BY_HOUR",
                "InternetMaxBandwidthOut": 1,
                "PublicIpAssigned": True#分配公网IP
            }
        }
        req.from_json_string(json.dumps(params))
        resp = client.RunInstances(req)
        print(resp.InstanceIdSet)
        insid = str(resp.InstanceIdSet)
        isid = insid.strip("[]'")

        print("time 60s...ip！！")
        time.sleep(60)

        while True:
            try:
                req1 = models.DescribeInstancesRequest()
                params = {
                    "Filters": [
                        {
                            "Name": "instance-id",
                            "Values": [isid]
                        }
                    ]
                }
                req1.from_json_string(json.dumps(params))
                resp1 = client.DescribeInstances(req1)
                print(resp1.to_json_string())
                match = re.search(r'PublicIpAddresses\": \[\"(.*?)\"\]', resp1.to_json_string())
                ip = match.group(1)
                print(ip)
                break
            except:
                print("ip没能命中，等待40s再试一次！！")#这一块等待腾讯的公网IP分配，因为腾讯的服务器的特点就是先创建一个服务器，如何再分配公网，所以IP可能要等一段时间分配
                time.sleep(40)
                continue

        return ip,isid


    except TencentCloudSDKException as err:
        print(err)


def breakserver(isid):
    try:
        cred = credential.Credential("aaa", "bbb")
        httpProfile = HttpProfile()
        httpProfile.endpoint = "cvm.tencentcloudapi.com"
        clientProfile = ClientProfile()
        clientProfile.httpProfile = httpProfile
        client = cvm_client.CvmClient(cred, reg, clientProfile)

        # 实例化一个请求对象,每个接口都会对应一个request对象
        req = models.TerminateInstancesRequest()
        params = {
            "InstanceIds": [isid]
        }
        req.from_json_string(json.dumps(params))
        resp = client.TerminateInstances(req)
        print(resp.to_json_string())

    except TencentCloudSDKException as err:
        print(err)
    print("delete OK！！")




for i in range(0,15):
    reg = random.choice(list(region_zone_dict.keys()))
    print(reg)
    zon = random.choice(region_zone_dict[reg])
    print(zon)

    try:
        ip1, isid1 = createserver()  # 创建服务器并返回ip和SUBID
    except:
        print("创建失败，跳过！")
        continue


    try:
        breakserver(isid1)
    except:
        while True:
            print("还是删不掉，等20s后再试一次！")
            time.sleep(20)
            try:
                breakserver(isid1)
                break
            except:
                continue
