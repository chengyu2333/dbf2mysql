from process import main
import os
if not os.path.exists("data"):
    os.mkdir("data")
if not os.path.exists("tmp"):
    os.mkdir("tmp")
main.run()
# main.once("","")