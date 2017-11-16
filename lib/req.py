from req_post import PostReq

from sync.req_get import GetReq


class Req(PostReq, GetReq):
    pass

    # def commit_data(self, data):
    #     id_cache = Cache("tmp/id_cache.txt")
    #     id = id_cache.get_value_by_key(data['hqzqdm'])
    #     if id:
    #         url = config.api_put.format(id=id)
    #         response = requests.get(url)
    #         if response.status_code == 200:
    #             print(response.text)
    #     else:
    #         # post and cache id
    #         pass



# Req().commit_data()