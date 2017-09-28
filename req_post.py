# -*- coding: utf-8 -*
from req_base import BaseReq
from tools import view_bar
from cache import Cache
from retry import retry
import config
import json
import time
import requests
import threadpool


class PostReq(BaseReq):

    @retry
    def commit_data(self, data, cb=None):
        id_cache = Cache("tmp/id_cache.txt")
        id = id_cache.get_value(data['hqzqdm'])
        if id:
            url = config.api_put.format(id=id)
            response = requests.get(url)
            if response.status_code == 200:
                updated_at_remote = json.loads(response.text)['updated_at']
                updated_at_remote = time.strptime(updated_at_remote, "%Y年%m月%d日 %H:%M:%S")
                updated_at_local = time.strptime(data['updated_at'],"%Y-%m-%dT%H:%M:%S")
                # print("remote", updated_at_remote)
                # print("local", updated_at_local)
                # put
                if updated_at_local and updated_at_remote < updated_at_local:
                    res = requests.put(url, data)
                    if res.status_code == 200:
                        if cb: cb(True, id)
                        print("put成功")
                        return True
                    else:
                        if cb: cb(False, id, res)
                        print("put失败")
                        raise Exception("put失败")
                else:
                    if cb: cb(True, id)
                    print("不需要同步")
                    return True
            else:
                raise Exception("get remote id failed")
        else:  # post
            res = requests.post(config.api_post, data=data, timeout=self._timeout_http)
            if res.status_code == 201:
                id = json.loads(res.text)['id']
                id_cache.put_item(data['hqzqdm'], id)
                if cb: cb(True, id)
                print("post成功")
                return True
            else:
                if cb: cb(False, id, res)
                print("post失败",res.status_code, res.text)
                print(data)
                raise Exception("post failed")

    # batch post data to webservice
    def commit_data_list(self, post_url, data_list, post_json=False, enable_thread=False, thread_pool_size=10, post_success_code=201):
        self.post_success_code = post_success_code
        self.data_total = len(data_list)
        if self.data_total: view_bar(0, self.data_total)
        else: return

        if not self.pool:
            self.pool = threadpool.ThreadPool(thread_pool_size)
        try:
            if enable_thread:
                args = []
                for data in data_list:
                    args.append(([data, self.cb], None))
                    # args.append(([post_url, data, post_json, self.__callback], None))
                reqs = threadpool.makeRequests(self.commit_data, args)
                [self.pool.putRequest(req) for req in reqs]
                self.pool.wait()
                args.clear()
                reqs.clear()
            else:
                for d in data_list:
                    # self.post_try(post_url, d, post_json, self.__callback)
                    result = self.commit_data(d)
            self.success_count = 0
            self.processed_count = 0

        except Exception:
            raise

    def cb(self, result, id="", res=None):
        if res:
            print(res)
            print(res.text)
        self.processed_count += 1
        if result: self.success_count += 1
        view_bar(self.processed_count, self.data_total)
        print(" ", self.success_count, " ", id, end="")

    def __callback(self, *args):
        self.processed_count += 1
        response = args[0]
        if response:
            if response.status_code == self.post_success_code:
                self.success_count += 1
            else:
                self.log.log_error("response error\ncode:%d\nresponse:%s\npost_data data:%s"
                              % (response.status_code,response,response))
        view_bar(self.processed_count, self.data_total)
        print(" ", self.success_count, end="")
