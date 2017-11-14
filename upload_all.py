import sync

sync = sync.Sync()
if sync.get("tmp/nqhq.dbf"):
    sync.process()
    sync.upload()
