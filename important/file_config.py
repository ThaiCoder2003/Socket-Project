def config():
    config={}

    config["cache_time"]=900
    config["whitelist"]=["oosc.online", "example.com", "www.google.com", "www.bing.com", "testphp.vulnweb.com/login.php", "vbsca.ca/login/login.asp", "vbsca.ca/login", "vbsca.ca/login/LoginsAndPermissions3.htm"]
    config["time_in"]=8
    config["time_out"]=20

    return config