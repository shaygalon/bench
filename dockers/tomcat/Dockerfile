FROM tomcat:9.0.5-jre9-slim

RUN apt update && \
	apt install -y --no-install-recommends build-essential libssl-dev git 
# Set minimal useful heap for java
RUN echo 'JAVA_OPTS="-Xmx1G"' > /usr/local/tomcat/bin/setenv.sh
RUN git clone https://github.com/wg/wrk.git wrk && \
	cd wrk && make -j && cp wrk /usr/local/bin && cd .. && rm -rf wrk
RUN apt install -y --no-install-recommends wget procps
# entrypoint setting up server and by default running hello world test
COPY runme.sh /usr/bin 
# some config options
ADD sysctl.conf /etc/sysctl.conf
# disable logging
COPY server.xml /usr/local/tomcat/conf/server.xml
# some sample tests
COPY tests/ /tests/

ENTRYPOINT ["/usr/bin/runme.sh"]



