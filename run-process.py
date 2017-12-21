from process import main
import os
if not os.path.exists("data"):
    os.mkdir("data")
if not os.path.exists("tmp"):
    os.mkdir("tmp")
main.run()
# main.once("/Data/LOneClient-2.3.2.25b/sanban/data/20171214/nqhq/nqhq.dbf.091006","")