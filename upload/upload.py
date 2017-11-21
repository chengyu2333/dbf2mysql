from lib.retry import retry

import config
from lib.log import Log
from process.map_dict import map_dict
from upload.req_post import PostReq


class Upload:
    def __init__(self):
        self.req = PostReq(retry_http=config.retry_http,
                           silence_http_multiplier=config.silence_http_multiplier,
                           silence_http_multiplier_max=config.silence_http_multiplier_max,
                           timeout_http=config.timeout_http)
        self.log = Log()

    @retry(stop_max_attempt_number=3,
           wait_exponential_multiplier=2000,
           wait_exponential_max=10000)
    def upload(self, data_list):

        data_list = map_dict(data_list,
                             config.map_rule['map'],
                             config.map_rule['strict'],
                             config.map_rule['lower'],
                             swap=config.map_rule['swap'])

        try:
            self.req.commit_data_list(post_url=config.api_post,
                                      data_list=data_list,
                                      post_json=config.post_json,
                                      enable_thread=config.enable_thread,
                                      thread_pool_size=config.thread_pool_size,
                                      post_success_code=config.post_success_code)
        except Exception as e:
            self.log.log_error(str(e))
