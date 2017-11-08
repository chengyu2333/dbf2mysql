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
    # 提交一条数据
    @retry(stop_max_attempt_number=config.retry_http,
           wait_exponential_multiplier=config.silence_http_multiplier * 1000,
           wait_exponential_max=config.silence_http_multiplier_max * 1000)
    def commit_data(self, data, cb=None):
        """
        读取ID缓存文件到dict
        读取DBF文件
        映射处理数据
        
        遍历记录
            @retry
            根据ID检测是否存在这条记录（返回False或update_at）
                update_at：
                    对比update_at：
                        ＜：PUT更新
                            是否返回200
                                是：成功
                                否：raise抛异常
                        =：成功
                False：POST添加，缓存ID
                    是否返回201
                        是：成功
                        否：raise抛异常
        保存ID缓存到文件
        """
        # TODO 优化缓存策略
        id_cache = Cache("tmp/id_cache.txt")
        id = id_cache.get_value(data['hqzqdm'])
        # 如果有缓存这个ID
        if id:
            url = config.api_put.format(id=id)
            response = requests.get(url)
            # 如果服务器存在这个ID
            if response.status_code == 200:  # api server have id
                updated_at_remote = json.loads(response.text)['updated_at']
                updated_at_remote = time.strptime(updated_at_remote, "%Y年%m月%d日 %H:%M:%S")
                updated_at_local = time.strptime(data['updated_at'], "%Y-%m-%dT%H:%M:%S")
                # 如果远程update_at ＜ 待传update_at则put该数据
                if updated_at_local and updated_at_remote < updated_at_local:
                    res = requests.put(url, data)
                    if res.status_code == 200:  # put success
                        if cb: cb(True, id)
                        print(" put成功\r", end="")
                        return True
                    elif res.status_code:  # gateway timeout
                        if cb: cb(True, id)
                        print(" put成功\r", end="")
                        return True
                    else:
                        if cb: cb(False, id, res)
                        print(" put失败", res.status_code)
                        raise Exception("put失败")
                else:
                    if cb: cb(True, id)
                    print(" 不需要同步\r", end="")
                    return True
            # 服务器不存在这个ID
            else:
                # 删除这个ID的缓存
                id_cache.remove(data['hqzqdm'])
                # raise Exception("get remote id failed")
        # 缓存里没有这个ID，POST上传
        else:
            res = requests.post(config.api_post, data=data, timeout=self._timeout_http)
            if res.status_code == 201: # post success
                id = json.loads(res.text)['id']
                id_cache.append(data['hqzqdm'], id)
                if cb: cb(True, id)
                print(" post成功\r",end="")
                return True
            else:
                if cb: cb(False, id, res)
                self.log.log_error("\npost失败 " + str(res.status_code))
                raise Exception("post failed")

    # 批量提交数据
    def commit_data_list(self, post_url, data_list, post_json, enable_thread=False, thread_pool_size=10, post_success_code=201):
        """ batch commit data """
        self.post_success_code = post_success_code
        self.data_total = len(data_list)
        if self.data_total: view_bar(0, self.data_total)
        else: return

        if not self.pool:
            print("初始化线程池", thread_pool_size)
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
                    result = self.commit_data(d)
                    if result:
                        self.success_count += 1
            count = self.success_count
            self.success_count = 0
            self.processed_count = 0
            return count
        except Exception:
            raise

    # 提交完毕的回调
    def cb(self, result, id="", res=None):
        if res:
            print(res)
            print(res.text)
        self.processed_count += 1
        if result: self.success_count += 1
        view_bar(self.processed_count, self.data_total)
        print(" ", self.success_count, " ", id, end="")

    # 暂不需要
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
