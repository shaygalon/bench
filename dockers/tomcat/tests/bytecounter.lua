init = function(args)
  i = 0
  reqs = {}
  reqs[0] = wrk.format("POST", "/examples/servlets/nonblocking/bytecounter", { ["Pragma"]="no-cache", ["Origin"]="http://10.7.56.61:8080", ["Accept-Encoding"]="gzip, deflate", ["Host"]="127.0.0.1", ["Accept-Language"]="en-US,en;q=0.9,he;q=0.8", ["Upgrade-Insecure-Requests"]="1", ["User-Agent"]="Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36", ["Content-Type"]="multipart/form-data; boundary=----WebKitFormBoundarysxjeD7nETzPgENmL", ["Accept"]="text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8", ["Cache-Control"]="no-cache", ["Referer"]="http://10.7.56.61:8080/examples/servlets/nonblocking/bytecounter.html", ["Cookie"]="JSESSIONID=FDD3D1FC6610757BBF63A15BE9DB86AC", ["Connection"]="keep-alive", ["Content-Length"]="337" }, "------WebKitFormBoundarysxjeD7nETzPgENmL\r\nContent-Disposition: form-data; name=\"data\"\r\n\r\n*************from here************\r\n-------------to here\r\n------WebKitFormBoundarysxjeD7nETzPgENmL\r\nContent-Disposition: form-data; name=\"source\"; filename=\"\"\r\nContent-Type: application/octet-stream\r\n\r\n\r\n------WebKitFormBoundarysxjeD7nETzPgENmL--\r\n")
end

request = function ()
  local r = reqs[i]
  i = i + 1
  if i > #reqs then
    i = 0
  end
  return r
end


done = function(summary, latency, requests)
   io.write("------------------------------\n")
   io.write("HEADERS,rps,avg lat,timeouts,50,90,99,99.999\n");
   io.write(string.format("CSV,%.02f,%d,%d",1e6*summary.requests/summary.duration,latency.mean,summary.errors.timeout))
   for _, p in pairs({ 50, 90, 99, 99.999 }) do
      n = latency:percentile(p)
      io.write(string.format(",%d", n))
   end
   io.write("\n")
end

