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

