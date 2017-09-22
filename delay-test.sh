#!/bin/bash
curl -o /dev/null -s -w "http_code: %{http_code}\nhttp_connect:%{http_connect}\ncontent_type:%{content_type}\ntime_dns:%{time_namelookup}\ntime_redirect:%{time_redirect}\ntime_pretransfer:%{time_pretransfer}\ntime_connect:%{time_connect}\ntime_starttransfer:%{time_starttransfer}\ntime_total:%{time_total}:\nspeed_download:%{speed_download}\n " "$1"
